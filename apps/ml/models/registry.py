from django.db import models
from apps.common.models.base import BaseModel

class ModelStatus(models.TextChoices):
    RESEARCH = 'RESEARCH', 'Research'
    EVALUATION = 'EVALUATION', 'Evaluation'
    PRODUCTION = 'PRODUCTION', 'Production'

class MLModel(BaseModel):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., urgency-classifier")
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=50, help_text="e.g., classification, regression")

    def __str__(self):
        return self.name

class FeatureSet(BaseModel):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    features_schema = models.JSONField(help_text="Schema describing features used")

    class Meta:
        unique_together = ('name', 'version')

    def __str__(self):
        return f"{self.name} v{self.version}"

class ModelVersion(BaseModel):
    ml_model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=ModelStatus.choices, default=ModelStatus.RESEARCH)
    
    # Temporal Data tracking
    training_period_start = models.DateField(null=True, blank=True)
    training_period_end = models.DateField(null=True, blank=True)
    
    # Storage
    model_file_path = models.CharField(max_length=255, help_text="Path to .joblib file in media/models/")
    checksum = models.CharField(max_length=255, blank=True)
    
    class Meta:
        unique_together = ('ml_model', 'version')

    def __str__(self):
        return f"{self.ml_model.name} v{self.version}"

class ModelEvaluation(BaseModel):
    model_version = models.ForeignKey(ModelVersion, on_delete=models.CASCADE, related_name='evaluations')
    feature_set = models.ForeignKey(FeatureSet, on_delete=models.PROTECT)
    
    evaluation_period_start = models.DateField(null=True, blank=True)
    evaluation_period_end = models.DateField(null=True, blank=True)
    
    metrics = models.JSONField(help_text="Accuracy, F1, MAE, RMSE, etc.")
    calibration_metrics = models.JSONField(blank=True, null=True, help_text="Brier score, etc.")
    
    def __str__(self):
        return f"Eval for {self.model_version}"
