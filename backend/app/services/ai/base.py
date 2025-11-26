from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AIProvider(ABC):
    """Base class for all AI providers"""
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        description: str,
        style: str,
        model: Optional[str] = None,
        **kwargs
    ) -> bytes: # Or URL string, depending on implementation. Returning bytes or URL.
        pass
