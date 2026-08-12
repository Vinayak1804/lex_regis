import hashlib
import json

class HashService:
    @staticmethod
    def hash_text(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_file(file_obj) -> str:
        sha256_hash = hashlib.sha256()
        for byte_block in file_obj.chunks():
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def hash_blockchain_payload(payload: dict) -> str:
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        return HashService.hash_bytes(payload_bytes)
