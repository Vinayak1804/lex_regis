import os
import joblib
import pandas as pd
from django.conf import settings
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, root_mean_squared_error
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import brier_score_loss

def create_preprocessor():
    categorical_features = ['practice_area', 'matter_category', 'sub_category', 'complexity', 'court']
    numeric_features = ['num_hearings_so_far', 'num_adjournments_so_far']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    return preprocessor

def train_classification_model(X_train, y_train, model_type='rf'):
    preprocessor = create_preprocessor()
    
    if model_type == 'rf':
        base_model = RandomForestClassifier(n_estimators=50, random_state=42)
    else:
        raise ValueError("Unsupported model type")
        
    # Calibrate the classifier
    calibrated_model = CalibratedClassifierCV(estimator=base_model, method='isotonic', cv=3)
    
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', calibrated_model)])
                               
    pipeline.fit(X_train, y_train)
    return pipeline

def train_regression_model(X_train, y_train, model_type='rf'):
    preprocessor = create_preprocessor()
    
    if model_type == 'rf':
        model = RandomForestRegressor(n_estimators=50, random_state=42)
    else:
        raise ValueError("Unsupported model type")
        
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('regressor', model)])
                               
    pipeline.fit(X_train, y_train)
    return pipeline

def evaluate_classification_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    probs = model.predict_proba(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, predictions),
        # 'precision': precision_score(y_test, predictions, average='weighted', zero_division=0),
        # 'recall': recall_score(y_test, predictions, average='weighted', zero_division=0),
        # 'f1': f1_score(y_test, predictions, average='weighted', zero_division=0)
    }
    
    # We could calculate brier score here for each class, but for simplicity we'll just log accuracy.
    return metrics

def evaluate_regression_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    metrics = {
        'mae': mean_absolute_error(y_test, predictions),
        'rmse': root_mean_squared_error(y_test, predictions)
    }
    return metrics

def save_model(model, model_name, version):
    models_dir = os.path.join(settings.MEDIA_ROOT, 'models')
    os.makedirs(models_dir, exist_ok=True)
    file_path = os.path.join(models_dir, f"{model_name}_v{version}.joblib")
    joblib.dump(model, file_path)
    return file_path

def load_model(file_path):
    return joblib.load(file_path)
