from typing import Dict, Type, Optional
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

# Alias for backward compatibility with book_service.py
class AIServiceFactory:
    """Alias for AIProviderFactory to maintain compatibility"""
    
    @staticmethod
    def create_ai_service(provider: str = "gemini") -> Optional[AIProvider]:
        """Create AI service instance"""
        try:
            return AIProviderFactory.create(provider)
        except Exception:
            return None
    
    @staticmethod
    def get_default_service() -> Optional[AIProvider]:
        """Get default AI service"""
        if settings.GEMINI_API_KEY:
            return AIProviderFactory.create("gemini")
        return None
