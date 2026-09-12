from apps.ml.models.historical import HistoricalCaseFeature

def generate_similarity_explanation(query_issue, hist_feature: HistoricalCaseFeature, semantic_score: float, structured_score: float) -> str:
    """
    Generates a deterministic, rule-based explanation for why a historical case matched.
    """
    reasons = []
    
    if query_issue.ai_analysis and query_issue.ai_analysis.practice_area:
        if hist_feature.dispute_type.lower() == query_issue.ai_analysis.practice_area.lower():
            reasons.append(f"Shares the same practice area ({hist_feature.dispute_type})")
            
    if query_issue.state:
        if hist_feature.jurisdiction and query_issue.state.lower() in hist_feature.jurisdiction.lower():
            reasons.append(f"Occurred in a similar jurisdiction ({hist_feature.jurisdiction})")
            
    if query_issue.ai_analysis and query_issue.ai_analysis.important_keywords:
        query_kws = set([k.lower() for k in query_issue.ai_analysis.important_keywords])
        hist_kws = set([k.lower() for k in hist_feature.legal_issues])
        overlap = query_kws.intersection(hist_kws)
        if overlap:
            reasons.append(f"Involves similar legal keywords ({', '.join(list(overlap)[:3])})")
            
    if semantic_score > 0.8:
        reasons.append("Highly similar factual description")
    elif semantic_score > 0.6:
        reasons.append("Related factual context")
        
    if not reasons:
        return "Matched based on general semantic and structural similarity."
        
    return "This case was retrieved because it: " + "; and ".join(reasons) + "."
