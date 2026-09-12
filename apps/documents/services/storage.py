from abc import ABC, abstractmethod
from django.core.files.storage import default_storage

class StorageProvider(ABC):
    @abstractmethod
    def save(self, path, file_obj):
        pass

    @abstractmethod
    def get_url(self, path):
        pass

    @abstractmethod
    def delete(self, path):
        pass

class LocalStorageProvider(StorageProvider):
    def save(self, path, file_obj):
        return default_storage.save(path, file_obj)

    def get_url(self, path):
        return default_storage.url(path)

    def delete(self, path):
        default_storage.delete(path)

class FutureS3Provider(StorageProvider):
    def save(self, path, file_obj):
        raise NotImplementedError("S3 integration pending")

    def get_url(self, path):
        raise NotImplementedError("S3 integration pending")

    def delete(self, path):
        raise NotImplementedError("S3 integration pending")

class FutureAzureProvider(StorageProvider):
    def save(self, path, file_obj):
        raise NotImplementedError("Azure integration pending")

    def get_url(self, path):
        raise NotImplementedError("Azure integration pending")

    def delete(self, path):
        raise NotImplementedError("Azure integration pending")

class FutureIPFSProvider(StorageProvider):
    def save(self, path, file_obj):
        raise NotImplementedError("IPFS integration pending")

    def get_url(self, path):
        raise NotImplementedError("IPFS integration pending")

    def delete(self, path):
        raise NotImplementedError("IPFS integration pending")

class DocumentStorageService:
    def __init__(self, provider: StorageProvider = None):
        self.provider = provider or LocalStorageProvider()

    def save_file(self, file_obj, path):
        return self.provider.save(path, file_obj)
        
    def get_file_url(self, path):
        return self.provider.get_url(path)
        
    def delete_file(self, path):
        self.provider.delete(path)

    @classmethod
    def get_usage(cls):
        from apps.documents.models import Document, DocumentVersion
        from django.db.models import Sum
        
        # DocumentVersion tracks the physical files. We sum their sizes to prevent double counting.
        version_size = DocumentVersion.objects.aggregate(total=Sum('file_size'))['total'] or 0
        
        total_used_bytes = version_size
        
        # Make capacity configurable, default 500GB
        from django.conf import settings
        capacity_gb = getattr(settings, 'DMS_STORAGE_CAPACITY_GB', 500)
        capacity_bytes = capacity_gb * 1024 * 1024 * 1024
        
        used_gb = round(total_used_bytes / (1024 * 1024 * 1024), 2)
        percentage_used = min(100, round((total_used_bytes / capacity_bytes) * 100, 2)) if capacity_bytes > 0 else 0
        
        return {
            'total_bytes': total_used_bytes,
            'used_gb': used_gb,
            'available_gb': max(0, capacity_gb - used_gb),
            'capacity_gb': capacity_gb,
            'percentage_used': percentage_used
        }
