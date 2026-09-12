from apps.cases.models import Case
from apps.ml.models.historical import HistoricalCaseFeature
from apps.ml.services.outcome_normalization import normalize_case_outcome
from apps.ml.services.data_quality import evaluate_data_quality
import json

def extract_historical_features(case: Case, is_synthetic: bool = False) -> HistoricalCaseFeature:
    """
    Extracts structured features from a Case and saves them to HistoricalCaseFeature.
    """
    # Create or update the feature record
    feature, created = HistoricalCaseFeature.objects.get_or_create(case=case)
    
    feature.jurisdiction = case.location
    feature.court_level = case.court
    
    # We will map practice_area to dispute_type since HistoricalCaseFeature doesn't have practice_area
    feature.dispute_type = case.practice_area or case.matter_category
    
    feature.case_stage = case.status
    feature.relief_sought = case.description[:500] if case.description else ''
    
    # Outcomes - Fallback safely
    if hasattr(case, 'hearings') and hasattr(case.hearings, 'count'):
        feature.hearing_count = case.hearings.count()
        feature.adjournment_count = case.hearings.filter(status='ADJOURNED').count()
    else:
        feature.hearing_count = 0
        feature.adjournment_count = 0
        
    feature.disposition = case.status
    feature.outcome_classification = normalize_case_outcome(feature.disposition)
    
    feature.data_quality_score = evaluate_data_quality(case)
    
    # Generate Semantic Representation
    semantic_parts = [
        f"Case Type: {feature.dispute_type}",
        f"Court: {feature.court_level} {feature.jurisdiction}",
        f"Facts: {case.description or ''}"
    ]
    feature.semantic_representation = " | ".join(semantic_parts)
    feature.is_synthetic = is_synthetic
    
    feature.save()
    return feature
