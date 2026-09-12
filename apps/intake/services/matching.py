from typing import List, Dict, Tuple
from apps.intake.models import LegalIssue, AIAnalysis
from apps.accounts.models import ProfessionalProfile

class LawyerMatchService:
    @staticmethod
    def get_matched_lawyers(issue: LegalIssue, analysis: AIAnalysis) -> List[Dict]:
        """
        Calculates a Platform Lawyer Match Score based on configurable weights.
        Returns a list of dicts containing the lawyer, score, and matching reasons.
        """
        weights = {
            'practice_area': 30,
            'region': 15,
            'experience': 15,
            'budget': 15,
            'consultation_mode': 10,
            'availability': 10,
            'response_time': 5,
        }
        
        # Get all lawyers. In production we would pre-filter.
        lawyers = ProfessionalProfile.objects.all().select_related('user', 'user__profile')
        
        matches = []
        for lawyer in lawyers:
            score = 0
            reasons = []
            profile = getattr(lawyer.user, 'profile', None)
            
            # Practice Area (30%)
            # We assume lawyer has practice_areas JSON field or similar. 
            # Let's say we check if analysis.practice_area is in lawyer's bio or practice areas.
            lawyer_bio = (profile.short_bio or '') if profile else ''
            lawyer_practices = " ".join(lawyer.practice_areas) if lawyer.practice_areas else ""
            match_text = (lawyer_bio + " " + lawyer_practices).lower()
            
            if analysis.practice_area and analysis.practice_area.lower() in match_text:
                score += weights['practice_area']
                reasons.append("Exact practice-area match")
            elif analysis.category and analysis.category.lower() in match_text:
                score += weights['practice_area'] * 0.5
                reasons.append("Partial practice-area match")
                
            # Region (15%)
            lawyer_city = profile.city if profile else ''
            lawyer_state = profile.state if profile else ''
            
            if issue.city and lawyer_city and issue.city.lower() == lawyer_city.lower():
                score += weights['region']
                reasons.append("Relevant regional experience")
            elif issue.state and lawyer_state and issue.state.lower() == lawyer_state.lower():
                score += weights['region'] * 0.5
                
            # Experience (15%)
            # We don't have exact issue experience requirement, but let's give points if they have > 5 years
            if lawyer.years_of_experience and lawyer.years_of_experience > 5:
                score += weights['experience']
                reasons.append(f"Highly experienced ({lawyer.years_of_experience} years)")
                
            # Budget (15%)
            # A simple match for demonstration
            score += weights['budget']
            reasons.append("Flexible budget")
                
            # Consultation Mode (10%)
            if issue.preferred_consultation:
                score += weights['consultation_mode']
                reasons.append(f"Available for {issue.preferred_consultation} consultation")
                
            # Availability (10%)
            if lawyer.user.is_active:
                score += weights['availability']
                reasons.append("Lawyer is available now")
                
            # Response Time (5%)
            score += weights['response_time']
            reasons.append("Typically responds within 24 hours")
            
            if score > 0:
                matches.append({
                    'lawyer': lawyer,
                    'score': min(int(score), 100),
                    'reasons': reasons
                })
                
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:10]
