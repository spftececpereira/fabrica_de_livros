from typing import Optional
from app.services.storage.base import StorageProvider
from app.services.storage.local import LocalStorageProvider
# from app.services.storage.s3 import S3StorageProvider # To be implemented for prod

class StorageServiceFactory:
    
    @staticmethod
    def create_storage() -> StorageProvider:
        # Logic to choose provider based on environment
        # For now, default to local
        return LocalStorageProvider()
