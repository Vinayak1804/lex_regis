from apps.cases.models import Case

def evaluate_data_quality(case: Case) -> str:
    """
    Evaluates a Case object and returns a quality score (HIGH, MEDIUM, LOW)
    based on missing fields and inconsistent metadata.
    """
    score = 0
    max_score = 5
    
    # 1. Has basic metadata
    if case.title and case.matter_category and case.status:
        score += 1
        
    # 2. Has court info
    if case.court:
        score += 1
        
    # 3. Has practice area
    if case.practice_area:
        score += 1
        
    # 4. Has dates
    if case.created_at:
        score += 1
        
    # 5. Has descriptions or issues
    if case.description:
        score += 1
        
    if score == max_score:
        return 'HIGH'
    elif score >= 3:
        return 'MEDIUM'
    else:
        return 'LOW'
