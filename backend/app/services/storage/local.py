import os
import shutil
from pathlib import Path
from typing import BinaryIO
from app.services.storage.base import StorageProvider
from app.core.config import settings

class LocalStorageProvider(StorageProvider):
    """Implementation for local file system storage (dev/testing)."""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure public directory exists for serving files
        self.public_dir = Path("frontend/public/uploads")
        self.public_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, file_data: BinaryIO, filename: str, content_type: str = "image/png") -> str:
        """
        Save file locally and return a relative URL.
        For this MVP, we'll save to frontend/public so Next.js can serve it directly.
        """
        file_path = self.public_dir / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_data, buffer)
            
        # Return URL relative to frontend
        return f"/uploads/{filename}"

    async def delete(self, filename: str) -> bool:
        try:
            file_path = self.public_dir / filename
            if file_path.exists():
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
