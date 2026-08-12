import hashlib
import json
import time
from typing import Dict, Any, Tuple
from django.utils import timezone
from ..models import BlockchainRecord
from django.contrib.contenttypes.models import ContentType

class BlockchainVerificationService:
    @staticmethod
    def verify_document(document) -> BlockchainRecord:
        """
        Mock implementation of verifying a document on the blockchain.
        In a real scenario, this would connect to an Ethereum node or third-party API.
        """
        # 1. Generate SHA256 of document properties
        data = {
            'document_number': document.document_number,
            'title': getattr(document, 'title', ''),
            'uploaded_at': document.upload_timestamp.isoformat() if document.upload_timestamp else '',
            'file_size': document.file_size
        }
        
        payload_str = json.dumps(data, sort_keys=True)
        sha256_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
        
        # 2. Mock Transaction on Ethereum
        tx_hash = f"0x{hashlib.md5(str(time.time()).encode()).hexdigest()}{hashlib.md5(sha256_hash.encode()).hexdigest()}"
        
        # 3. Create Record
        content_type = ContentType.objects.get_for_model(document)
        
        record = BlockchainRecord.objects.create(
            content_type=content_type,
            object_id=document.id,
            record_type='DOCUMENT_HASH',
            data_payload=data,
            sha256_hash=sha256_hash,
            transaction_hash=tx_hash,
            block_number=14205566,
            is_verified=True,
            verified_at=timezone.now()
        )
        
        # 4. Update Document
        document.blockchain_verification_status = 'VERIFIED'
        document.blockchain_transaction_hash = tx_hash
        document.verification_timestamp = timezone.now()
        document.immutable_record_id = str(record.id)
        document.save(update_fields=['blockchain_verification_status', 'blockchain_transaction_hash', 'verification_timestamp', 'immutable_record_id'])
        
        return record
