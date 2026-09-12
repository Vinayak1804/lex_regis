import os
import numpy as np
from django.conf import settings
from .pipeline import extract_case_features_at_time
from .training import load_model
from apps.ml.models.registry import ModelVersion
from apps.ml.models.prediction import (
    UrgencyPrediction, ComplexityPrediction, DurationPrediction, 
    FeePrediction, AdjournmentRiskPrediction
)

# Cache loaded models to avoid disk I/O on every prediction
_model_cache = {}

def get_active_model(model_name: str):
    """
    Retrieves the PRODUCTION version of the requested model.
    """
    mv = ModelVersion.objects.filter(ml_model__name=model_name, status='PRODUCTION').order_by('-created_at').first()
    if not mv:
        return None
        
    if mv.id not in _model_cache:
        try:
            _model_cache[mv.id] = load_model(mv.model_file_path)
        except Exception as e:
            print(f"Error loading model {model_name} v{mv.version}: {e}")
            return None
            
    return _model_cache[mv.id], mv

def predict_case(case, model_name: str, target_model_class, **kwargs):
    """
    Generic inference function.
    """
    model_data = get_active_model(model_name)
    if not model_data:
        return None
        
    model, model_version = model_data
    
    # Extract features at CURRENT time for inference
    features = extract_case_features_at_time(case)
    
    # Convert features to a format scikit-learn pipeline can consume (pandas DataFrame)
    import pandas as pd
    df = pd.DataFrame([features])
    
    try:
        # Determine if it's classification or regression based on predict_proba
        if hasattr(model, 'predict_proba'):
            # Classification
            probs = model.predict_proba(df)[0]
            pred_class_index = np.argmax(probs)
            confidence = probs[pred_class_index]
            
            # Check confidence threshold (e.g., 0.5)
            if confidence < kwargs.get('confidence_threshold', 0.5):
                return None # Abstain
                
            prediction_label = model.classes_[pred_class_index]
            
            # Create prediction record
            if target_model_class == UrgencyPrediction:
                return UrgencyPrediction.objects.create(
                    case=case,
                    model_version=model_version,
                    urgency_level=prediction_label,
                    probability=confidence,
                    confidence=confidence
                )
            elif target_model_class == ComplexityPrediction:
                return ComplexityPrediction.objects.create(
                    case=case,
                    model_version=model_version,
                    complexity_level=prediction_label,
                    probability=confidence,
                    confidence=confidence
                )
            elif target_model_class == AdjournmentRiskPrediction:
                return AdjournmentRiskPrediction.objects.create(
                    case=case,
                    model_version=model_version,
                    risk_level=prediction_label,
                    probability=confidence,
                    confidence=confidence
                )
                
        else:
            # Regression
            prediction = model.predict(df)[0]
            # Random Forest Regressor doesn't output confidence interval out-of-the-box in sklearn, 
            # so we'll use a heuristic or dummy bounds for now based on estimators
            preds = []
            if hasattr(model.named_steps['regressor'], 'estimators_'):
                # Extract preprocessor
                preprocessor = model.named_steps['preprocessor']
                X_transformed = preprocessor.transform(df)
                
                for estimator in model.named_steps['regressor'].estimators_:
                    preds.append(estimator.predict(X_transformed)[0])
                    
            if preds:
                lower = np.percentile(preds, 10)
                upper = np.percentile(preds, 90)
                std_dev = np.std(preds)
                # heuristic confidence based on std dev
                confidence = max(0, 1 - (std_dev / (prediction + 1)))
            else:
                lower = prediction * 0.8
                upper = prediction * 1.2
                confidence = 0.5
                
            if confidence < kwargs.get('confidence_threshold', 0.3):
                return None
                
            if target_model_class == DurationPrediction:
                return DurationPrediction.objects.create(
                    case=case,
                    model_version=model_version,
                    median_days=max(0, int(prediction)),
                    lower_bound_days=max(0, int(lower)),
                    upper_bound_days=max(0, int(upper)),
                    confidence=confidence
                )
            elif target_model_class == FeePrediction:
                return FeePrediction.objects.create(
                    case=case,
                    model_version=model_version,
                    median_fee=max(0, prediction),
                    lower_bound_fee=max(0, lower),
                    upper_bound_fee=max(0, upper),
                    confidence=confidence
                )
    except Exception as e:
        print(f"Inference error on {model_name}: {e}")
        return None

def run_all_inferences(case):
    """
    Runs all available production models for a given case.
    """
    results = {}
    
    results['urgency'] = predict_case(case, 'urgency-model', UrgencyPrediction)
    results['complexity'] = predict_case(case, 'complexity-model', ComplexityPrediction)
    results['duration'] = predict_case(case, 'duration-model', DurationPrediction)
    results['fee'] = predict_case(case, 'fee-model', FeePrediction)
    results['adjournment_risk'] = predict_case(case, 'adjournment-risk-model', AdjournmentRiskPrediction)
    
    return results

def predict_intake(issue, ai_analysis, model_name: str, target_model_class, **kwargs):
    """
    Inference function for the intake stage. 
    Does NOT save to database since a Case doesn't exist yet. Returns dict.
    """
    from .pipeline import extract_features_from_intake
    import pandas as pd
    
    model_data = get_active_model(model_name)
    if not model_data:
        return None
        
    model, model_version = model_data
    
    features = extract_features_from_intake(issue, ai_analysis)
    df = pd.DataFrame([features])
    
    try:
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(df)[0]
            pred_class_index = np.argmax(probs)
            confidence = probs[pred_class_index]
            
            if confidence < kwargs.get('confidence_threshold', 0.5):
                return {'prediction': None, 'confidence': confidence, 'abstain': True}
                
            prediction_label = model.classes_[pred_class_index]
            return {'prediction': prediction_label, 'confidence': confidence, 'model_version': model_version.version}
        else:
            prediction = model.predict(df)[0]
            preds = []
            if hasattr(model.named_steps['regressor'], 'estimators_'):
                preprocessor = model.named_steps['preprocessor']
                X_transformed = preprocessor.transform(df)
                for estimator in model.named_steps['regressor'].estimators_:
                    preds.append(estimator.predict(X_transformed)[0])
                    
            if preds:
                lower = np.percentile(preds, 10)
                upper = np.percentile(preds, 90)
                std_dev = np.std(preds)
                confidence = max(0, 1 - (std_dev / (prediction + 1)))
            else:
                lower = prediction * 0.8
                upper = prediction * 1.2
                confidence = 0.5
                
            if confidence < kwargs.get('confidence_threshold', 0.3):
                return {'prediction': None, 'confidence': confidence, 'abstain': True}
                
            return {
                'prediction': max(0, prediction), 
                'lower': max(0, lower), 
                'upper': max(0, upper), 
                'confidence': confidence, 
                'model_version': model_version.version
            }
    except Exception as e:
        print(f"Inference error on {model_name}: {e}")
        return None

def run_intake_inferences(issue, ai_analysis):
    results = {}
    results['urgency'] = predict_intake(issue, ai_analysis, 'urgency-model', UrgencyPrediction)
    results['complexity'] = predict_intake(issue, ai_analysis, 'complexity-model', ComplexityPrediction)
    results['duration'] = predict_intake(issue, ai_analysis, 'duration-model', DurationPrediction)
    results['fee'] = predict_intake(issue, ai_analysis, 'fee-model', FeePrediction)
    results['adjournment_risk'] = predict_intake(issue, ai_analysis, 'adjournment-risk-model', AdjournmentRiskPrediction)
    return results
