from apps.common.services.crypto import HashService

class DocumentHashService:
    @staticmethod
    def generate_hash(file_obj):
        return HashService.hash_file(file_obj)
