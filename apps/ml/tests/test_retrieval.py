from django.test import TestCase
from apps.intake.models import LegalIssue, AIAnalysis
from apps.cases.models import Case
from apps.ml.models.historical import HistoricalCaseFeature
from apps.ml.services.retrieval import cosine_similarity, structured_similarity, retrieve_similar_cases
from django.contrib.auth import get_user_model

User = get_user_model()

class MLRetrievalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password', first_name='Test', last_name='User', role='CLIENT')
        
    def test_cosine_similarity(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        v3 = [0.0, 1.0, 0.0]
        
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0)
        
    def test_structured_similarity(self):
        issue = LegalIssue.objects.create(user=self.user, description='Test', state='Maharashtra')
        ai_analysis = AIAnalysis.objects.create(
            issue=issue, practice_area='Civil', complexity='High',
            suggested_documents=['Doc 1'],
            possible_acts=['Act 1'],
            possible_sections=['Section 1'],
            important_keywords=['Keyword 1'],
            suggested_next_steps=['Step 1']
        )
        
        profile = self.user.profile
        case = Case.objects.create(title="Historical", matter_category="Civil", status="CLOSED", client=profile)
        hist = HistoricalCaseFeature.objects.create(
            case=case, dispute_type='Civil', complexity='High', jurisdiction='Maharashtra',
            legal_issues=['Keyword 1']
        )
        
        score = structured_similarity(issue, hist)
        self.assertGreater(score, 0.9)
        
    def test_retrieve_similar_cases(self):
        issue = LegalIssue.objects.create(user=self.user, description='Contract breach in software supply', state='Maharashtra')
        ai_analysis = AIAnalysis.objects.create(
            issue=issue, practice_area='Civil', complexity='High',
            suggested_documents=['Doc 1'],
            possible_acts=['Act 1'],
            possible_sections=['Section 1'],
            important_keywords=['Keyword 1'],
            suggested_next_steps=['Step 1']
        )
        
        profile = self.user.profile
        case = Case.objects.create(title="Historical", matter_category="Civil", status="CLOSED", description="Contract breach in software supply", client=profile)
        hist = HistoricalCaseFeature.objects.create(
            case=case, dispute_type='Civil', complexity='High', jurisdiction='Maharashtra',
            embedding=[0.5, 0.5, 0.5] # dummy embedding
        )
        
        # Will not match semantically (query embedding will be calculated), but structurally it will
        # Let's mock the embedding service in real usage, but here it's an integration test.
        # Since it actually calls sentence-transformers, it might take a moment.
        # Let's run it.
        results = retrieve_similar_cases(issue, user=self.user, limit=5, threshold=0.1)
        self.assertTrue(len(results) > 0)
