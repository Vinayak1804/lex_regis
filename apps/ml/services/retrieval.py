import math
from typing import List, Dict, Any, Optional
from apps.cases.models import Case
from apps.ml.models.historical import HistoricalCaseFeature, HistoricalSearchLog
from apps.ml.services.embedding_service import generate_embedding

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Computes cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    if len(vec1) != len(vec2):
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
        
    return dot_product / (mag1 * mag2)

def structured_similarity(query_issue, hist_feature: HistoricalCaseFeature) -> float:
    """
    Computes a basic structured similarity score (0 to 1) based on metadata matches.
    """
    score = 0.0
    weight_total = 0.0
    
    # Practice Area (30%)
    if query_issue.ai_analysis and query_issue.ai_analysis.practice_area:
        weight_total += 0.3
        if hist_feature.dispute_type.lower() == query_issue.ai_analysis.practice_area.lower():
            score += 0.3
            
    # Complexity (20%)
    if query_issue.ai_analysis and query_issue.ai_analysis.complexity:
        weight_total += 0.2
        if hist_feature.complexity.lower() == query_issue.ai_analysis.complexity.lower():
            score += 0.2
            
    # Jurisdiction (20%)
    if query_issue.state:
        weight_total += 0.2
        if hist_feature.jurisdiction and query_issue.state.lower() in hist_feature.jurisdiction.lower():
            score += 0.2
            
    # Keywords overlap (30%)
    if query_issue.ai_analysis and query_issue.ai_analysis.important_keywords:
        query_kws = set([k.lower() for k in query_issue.ai_analysis.important_keywords])
        hist_kws = set([k.lower() for k in hist_feature.legal_issues])
        if query_kws and hist_kws:
            weight_total += 0.3
            overlap = len(query_kws.intersection(hist_kws))
            jaccard = overlap / len(query_kws.union(hist_kws))
            score += (0.3 * jaccard)
            
    if weight_total == 0:
        return 0.5
        
    return score / weight_total


def retrieve_similar_cases(query_issue, user=None, limit: int = 5, threshold: float = 0.6) -> List[Dict[str, Any]]:
    """
    Hybrid retrieval combining embedding cosine similarity and structured overlap.
    """
    # 1. Prepare query string
    query_parts = []
    if query_issue.ai_analysis:
        query_parts.append(f"Practice Area: {query_issue.ai_analysis.practice_area}")
    query_parts.append(f"Facts: {query_issue.description}")
    query_text = " | ".join(query_parts)
    
    # 2. Get Query Embedding
    query_embedding = generate_embedding(query_text)
    
    # 3. Fetch Candidate Historical Cases (For SQLite we fetch all features, in PG we'd use pgvector)
    candidates = HistoricalCaseFeature.objects.select_related('case').all()
    
    results = []
    
    for hist in candidates:
        if not hist.embedding:
            continue
            
        # Semantic Score
        sem_score = cosine_similarity(query_embedding, hist.embedding)
        
        # Structured Score
        struct_score = structured_similarity(query_issue, hist)
        
        # Hybrid Score (60% semantic, 40% structured)
        hybrid_score = (0.6 * sem_score) + (0.4 * struct_score)
        
        if hybrid_score >= threshold:
            results.append({
                'case': hist.case,
                'feature': hist,
                'similarity': hybrid_score,
                'semantic_score': sem_score,
                'structured_score': struct_score
            })
            
    # Sort by hybrid score
    results.sort(key=lambda x: x['similarity'], reverse=True)
    results = results[:limit]
    
    # Log the search
    HistoricalSearchLog.objects.create(
        user=user,
        query_text=query_text,
        trigger_issue=query_issue,
        results_count=len(results)
    )
    
    return results
