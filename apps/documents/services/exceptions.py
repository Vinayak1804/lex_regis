class DocumentServiceError(Exception):
    pass

class DuplicateDocumentError(DocumentServiceError):
    def __init__(self, message, document_id=None):
        super().__init__(message)
        self.document_id = document_id
