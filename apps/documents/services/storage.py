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
