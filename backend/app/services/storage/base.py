from abc import ABC, abstractmethod
from typing import BinaryIO
import os

class StorageProvider(ABC):
    """Abstract base class for file storage providers."""
    
    @abstractmethod
    async def upload(self, file_data: BinaryIO, filename: str, content_type: str = "image/png") -> str:
        """Upload a file and return its URL/path."""
        pass

    @abstractmethod
    async def delete(self, filename: str) -> bool:
        """Delete a file."""
        pass
