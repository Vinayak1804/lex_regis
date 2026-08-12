from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SearchProvider(ABC):
    @abstractmethod
    def index_document(self, document_id: str, content: str, metadata: Dict[str, Any]):
        pass

    @abstractmethod
    def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def delete_document(self, document_id: str):
        pass

class DatabaseSearchProvider(SearchProvider):
    def index_document(self, document_id: str, content: str, metadata: Dict[str, Any]):
        pass # Fallback to standard DB queries or Postgres Full Text Search

    def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return []

    def delete_document(self, document_id: str):
        pass

class FutureElasticSearchProvider(SearchProvider):
    def index_document(self, document_id: str, content: str, metadata: Dict[str, Any]):
        raise NotImplementedError("ElasticSearch integration pending")

    def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("ElasticSearch integration pending")

    def delete_document(self, document_id: str):
        raise NotImplementedError("ElasticSearch integration pending")

class DocumentSearchService:
    def __init__(self, provider: SearchProvider = None):
        self.provider = provider or DatabaseSearchProvider()
        
    def index_document(self, document, extracted_text=""):
        metadata = {
            "title": document.original_file.name,
            "case_id": str(document.case.id),
            "owner_id": str(document.owner.id) if document.owner else None,
            "status": document.status.name,
        }
        self.provider.index_document(str(document.id), extracted_text, metadata)
        
    def search_documents(self, query: str, filters: Dict = None):
        return self.provider.search(query, filters)