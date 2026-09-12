import os
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.cases.models import Case
from apps.ml.models.registry import MLModel, ModelVersion, FeatureSet, ModelEvaluation
from apps.ml.services.pipeline import build_dataset_for_model, temporal_train_test_split
from apps.ml.services.training import (
    train_classification_model, train_regression_model, 
    evaluate_classification_model, evaluate_regression_model,
    save_model
)

class Command(BaseCommand):
    help = 'Train ML models on existing case data'

    def handle(self, *args, **options):
        self.stdout.write("Starting model training pipeline...")
        
        # Define models to train
        tasks = [
            {'name': 'urgency-model', 'type': 'classification', 'target': 'urgency'},
            {'name': 'complexity-model', 'type': 'classification', 'target': 'complexity'},
            {'name': 'duration-model', 'type': 'regression', 'target': 'duration'},
            {'name': 'fee-model', 'type': 'regression', 'target': 'fee'},
            {'name': 'adjournment-risk-model', 'type': 'classification', 'target': 'adjournment_risk'}
        ]
        
        feature_set, _ = FeatureSet.objects.get_or_create(
            name='case-intake',
            version='1.0',
            defaults={'features_schema': {'fields': ['practice_area', 'matter_category', 'complexity', 'num_hearings_so_far']}}
        )
        
        for task in tasks:
            self.stdout.write(f"\n--- Training {task['name']} ---")
            
            # Ensure MLModel exists
            ml_model, _ = MLModel.objects.get_or_create(
                name=task['name'],
                defaults={'model_type': task['type'], 'description': f"Predicts {task['target']}"}
            )
            
            # 1. Build Dataset
            self.stdout.write("Extracting point-in-time features...")
            df = build_dataset_for_model(task['target'])
            
            if len(df) < 10:
                self.stdout.write(self.style.WARNING(f"Insufficient data for {task['name']} ({len(df)} records). Skipping."))
                continue
                
            # 2. Temporal Split
            self.stdout.write("Applying temporal train/val/test split...")
            train_df, val_df, test_df = temporal_train_test_split(df)
            
            if train_df.empty or test_df.empty:
                self.stdout.write(self.style.WARNING("Split resulted in empty sets. Skipping."))
                continue
                
            # Prepare features and target
            features = ['practice_area', 'matter_category', 'sub_category', 'complexity', 'court', 'num_hearings_so_far', 'num_adjournments_so_far']
            X_train = train_df[features]
            y_train = train_df['target']
            
            X_test = test_df[features]
            y_test = test_df['target']
            
            # 3. Train Model
            self.stdout.write(f"Training {task['type']} model...")
            if task['type'] == 'classification':
                model = train_classification_model(X_train, y_train)
                metrics = evaluate_classification_model(model, X_test, y_test)
            else:
                model = train_regression_model(X_train, y_train)
                metrics = evaluate_regression_model(model, X_test, y_test)
                
            self.stdout.write(self.style.SUCCESS(f"Evaluation Metrics: {metrics}"))
            
            # 4. Save and Register Model
            version_str = timezone.now().strftime("%Y%m%d%H%M")
            file_path = save_model(model, ml_model.name, version_str)
            
            mv = ModelVersion.objects.create(
                ml_model=ml_model,
                version=version_str,
                status='PRODUCTION', # In real world, set to RESEARCH and promote after gating
                model_file_path=file_path,
                training_period_start=train_df['case_created_at'].min(),
                training_period_end=train_df['case_created_at'].max()
            )
            
            ModelEvaluation.objects.create(
                model_version=mv,
                feature_set=feature_set,
                metrics=metrics,
                evaluation_period_start=test_df['case_created_at'].min(),
                evaluation_period_end=test_df['case_created_at'].max()
            )
            
            self.stdout.write(self.style.SUCCESS(f"Successfully registered {ml_model.name} v{version_str}"))

        self.stdout.write("\nDone training models.")
