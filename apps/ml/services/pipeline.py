import pandas as pd
from django.utils import timezone
from apps.cases.models import Case
from apps.ml.models.registry import FeatureSet

def extract_case_features_at_time(case: Case, reference_date=None) -> dict:
    """
    Extracts features for a case, strictly using data available up to reference_date.
    This prevents data leakage.
    """
    if reference_date is None:
        reference_date = timezone.now()

    # Base features (assuming these are known at intake)
    features = {
        'case_id': str(case.id),
        'practice_area': case.practice_area or 'Unknown',
        'matter_category': case.matter_category or 'Unknown',
        'sub_category': case.sub_category or 'Unknown',
        'complexity': case.complexity or 'Unknown',
        'court': case.court or 'Unknown',
        'priority': case.priority or 'Unknown',
        # In a real app, you might encode text or use specific embeddings
    }
    
    # Example of point-in-time features: Hearings up to reference_date
    hearings_up_to_date = case.hearings.filter(start_time__lte=reference_date)
    features['num_hearings_so_far'] = hearings_up_to_date.count()
    
    adjournments = hearings_up_to_date.filter(status='ADJOURNED')
    features['num_adjournments_so_far'] = adjournments.count()
    
    return features

def extract_features_from_intake(issue, ai_analysis) -> dict:
    """
    Extracts features from an intake LegalIssue and its AIAnalysis for early ML inference.
    """
    features = {
        'case_id': f"issue_{issue.id}",
        'practice_area': ai_analysis.practice_area if ai_analysis else 'Unknown',
        'matter_category': ai_analysis.category if ai_analysis else 'Unknown',
        'sub_category': ai_analysis.subcategory if ai_analysis else 'Unknown',
        'complexity': ai_analysis.complexity if ai_analysis else 'Medium',
        'court': ai_analysis.recommended_court if ai_analysis else 'Unknown',
        'priority': issue.urgency if issue else 'NORMAL',
        'num_hearings_so_far': 0,
        'num_adjournments_so_far': 0,
    }
    return features

def build_dataset_for_model(target_type: str, cases_queryset=None, reference_date=None) -> pd.DataFrame:
    """
    Builds a pandas DataFrame containing features and the target variable.
    """
    if cases_queryset is None:
        cases_queryset = Case.objects.all()
        
    data = []
    for case in cases_queryset:
        features = extract_case_features_at_time(case, reference_date)
        
        # Determine the target based on target_type
        if target_type == 'urgency':
            features['target'] = case.priority if case.priority else 'NORMAL'
        elif target_type == 'complexity':
            features['target'] = case.complexity if case.complexity else 'MEDIUM'
        elif target_type == 'duration':
            # Example: total duration in days. If not closed, we might skip or use current duration
            if case.status == 'CLOSED' and case.created_at and case.updated_at:
                features['target'] = (case.updated_at - case.created_at).days
            else:
                continue # Skip cases that don't have a final duration for training
        elif target_type == 'fee':
            features['target'] = float(case.budget_estimate) if case.budget_estimate else 0.0
        elif target_type == 'adjournment_risk':
            # E.g., High if > 2 adjournments
            total_adjournments = case.hearings.filter(status='ADJOURNED').count()
            features['target'] = 'HIGH' if total_adjournments > 2 else ('MEDIUM' if total_adjournments > 0 else 'LOW')
        else:
            continue
            
        # Also store created_at for temporal splitting
        features['case_created_at'] = case.created_at
        data.append(features)
        
    df = pd.DataFrame(data)
    return df

def temporal_train_test_split(df: pd.DataFrame, date_column: str = 'case_created_at', train_ratio=0.7, val_ratio=0.15):
    """
    Splits data chronologically to prevent future data from leaking into the past.
    """
    if df.empty:
        return df, pd.DataFrame(), pd.DataFrame()
        
    df = df.sort_values(by=date_column)
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]
    
    return train_df, val_df, test_df
