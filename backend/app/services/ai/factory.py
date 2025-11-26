from typing import Dict, Type
from app.services.ai.base import AIProvider
from app.services.ai.gemini import GeminiProvider
from app.core.config import settings

class AIProviderFactory:
    """Factory to instantiate providers"""
    
    _providers: Dict[str, Type[AIProvider]] = {
        "gemini": GeminiProvider,
        # "openrouter": OpenRouterProvider, # To be implemented
    }
    
    @classmethod
    def create(cls, provider: str = "gemini") -> AIProvider:
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        if provider == "gemini":
            return GeminiProvider(api_key=settings.GEMINI_API_KEY)
            
        return cls._providers[provider]()
