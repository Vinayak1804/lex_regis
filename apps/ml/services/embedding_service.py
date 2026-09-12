import json
from apps.ml.models.historical import HistoricalCaseFeature

# We try to load sentence-transformers lazily to avoid heavy loading on boot
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Use a fast, small model for local sqlite-based operations
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            _model = None
    return _model

def generate_embedding(text: str) -> list[float]:
    """
    Generates a dense vector embedding for the given text.
    """
    if not text:
        return []
        
    model = get_embedding_model()
    if not model:
        # Fallback if sentence-transformers is not available
        return []
        
    # Generate embedding
    embedding = model.encode(text)
    return embedding.tolist()

def embed_case_feature(feature: HistoricalCaseFeature, force=False):
    """
    Generates and saves the embedding for a HistoricalCaseFeature.
    """
    if feature.embedding and not force:
        return
        
    if not feature.semantic_representation:
        return
        
    embedding_list = generate_embedding(feature.semantic_representation)
    if embedding_list:
        feature.embedding = embedding_list
        feature.embedding_model_version = 'all-MiniLM-L6-v2'
        feature.save(update_fields=['embedding', 'embedding_model_version'])
