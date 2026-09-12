from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
import pandas as pd
from apps.ml.services.pipeline import temporal_train_test_split, extract_features_from_intake
from apps.intake.models import LegalIssue, AIAnalysis
from django.contrib.auth import get_user_model

User = get_user_model()

class MLPipelineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password', first_name='Test', last_name='User', role='CLIENT')
        
    def test_temporal_split(self):
        # Create a mock dataframe
        data = {
            'case_created_at': [
                timezone.now() - timedelta(days=50),
                timezone.now() - timedelta(days=40),
                timezone.now() - timedelta(days=30),
                timezone.now() - timedelta(days=20),
                timezone.now() - timedelta(days=10),
            ],
            'target': [1, 2, 3, 4, 5]
        }
        df = pd.DataFrame(data)
        
        train, val, test = temporal_train_test_split(df, train_ratio=0.6, val_ratio=0.2)
        
        # 5 items: 3 train (60%), 1 val (20%), 1 test (20%)
        self.assertEqual(len(train), 3)
        self.assertEqual(len(val), 1)
        self.assertEqual(len(test), 1)
        
        # Assert order is preserved
        self.assertTrue(train['case_created_at'].max() <= val['case_created_at'].min())
        self.assertTrue(val['case_created_at'].max() <= test['case_created_at'].min())

    def test_intake_features(self):
        issue = LegalIssue.objects.create(
            user=self.user,
            description='Test issue',
            urgency='URGENT'
        )
        ai_analysis = AIAnalysis.objects.create(
            issue=issue,
            practice_area='Civil',
            complexity='High',
            suggested_documents=['Doc 1'],
            possible_acts=['Act 1'],
            possible_sections=['Section 1'],
            important_keywords=['Keyword 1'],
            suggested_next_steps=['Step 1']
        )
        
        features = extract_features_from_intake(issue, ai_analysis)
        
        self.assertEqual(features['practice_area'], 'Civil')
        self.assertEqual(features['complexity'], 'High')
        self.assertEqual(features['priority'], 'URGENT')
        self.assertEqual(features['num_hearings_so_far'], 0)
