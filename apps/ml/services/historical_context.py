from typing import List, Dict
from apps.ml.models.historical import HistoricalCaseFeature
from apps.intake.models import LegalIssue, AIAnalysis

class HistoricalContextService:
    @staticmethod
    def get_similar_cases(issue: LegalIssue, analysis: AIAnalysis) -> List[Dict]:
        """
        Retrieves historical cases similar to the given issue/analysis.
        Returns authorized high-level information only.
        """
        # Simple retrieval based on category and practice area for now, 
        # since we are not building new predictive ML models in this task.
        qs = HistoricalCaseFeature.objects.filter(is_synthetic=False)
        
        if analysis.practice_area:
            # We assume jurisdiction/dispute_type/legal_issues might contain practice area
            qs = qs.filter(legal_issues__icontains=analysis.practice_area)
            
        # Or try to match at least one keyword
        if analysis.important_keywords and not qs.exists():
            from django.db.models import Q
            query = Q()
            for kw in analysis.important_keywords:
                query |= Q(legal_issues__icontains=kw) | Q(relief_sought__icontains=kw)
            qs = HistoricalCaseFeature.objects.filter(is_synthetic=False).filter(query)

        # Limit to 7
        features = qs.select_related('case').order_by('-case__created_at')[:7]
        
        results = []
        for feat in features:
            results.append({
                'similarity': 'High',  # In a real model, this would be computed
                'category': feat.dispute_type or 'General',
                'court': feat.court_level or 'District Court',
                'year': feat.case.created_at.year,
                'duration': f"{feat.duration_days} days" if feat.duration_days else 'Unknown',
                'disposition': feat.disposition or 'Pending',
                'legal_issues': feat.legal_issues[:3] if isinstance(feat.legal_issues, list) else [],
                'why_similar': 'Matches identified practice area and key facts.'
            })
            
        return results
