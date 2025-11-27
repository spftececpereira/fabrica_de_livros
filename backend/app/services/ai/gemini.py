import google.generativeai as genai
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import io
import random
from app.services.ai.base import AIProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    """Specific implementation for Gemini"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Default models
        self.text_model_name = "gemini-1.5-flash" # Updated to a newer, faster model
        
    async def generate_text(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        model_name = model or self.text_model_name
        try:
            model_instance = genai.GenerativeModel(model_name)
            # Gemini async generation
            response = await model_instance.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            # Fallback or re-raise
            raise e
    
    async def generate_image(self, description: str, style: str, model: Optional[str] = None, **kwargs) -> bytes:
        """
        Generates a placeholder image using Pillow since Gemini Image Gen (Imagen) 
        via this SDK is not standard or might fail without Vertex AI.
        This ensures the PDF generation flow works.
        """
        try:
            # Create a basic image
            width, height = 1024, 1024
            # Random background color based on style
            colors = {
                "cartoon": (255, 200, 200),
                "realistic": (200, 200, 255),
                "manga": (255, 255, 200),
                "classic": (240, 240, 240)
            }
            bg_color = colors.get(style, (230, 230, 230))
            
            img = Image.new('RGB', (width, height), color=bg_color)
            d = ImageDraw.Draw(img)
            
            # Draw some random shapes to make it look "generated"
            for _ in range(5):
                shape_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(x1, width)
                y2 = random.randint(y1, height)
                d.rectangle([x1, y1, x2, y2], outline=shape_color, width=5)
            
            # Add text indicating it's a placeholder
            # Trying to load a default font, otherwise default
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
                
            text = f"AI Image Placeholder\nStyle: {style}\n{description[:30]}..."
            
            # Centered text (rough approximation)
            d.text((width/2 - 100, height/2), text, fill=(0, 0, 0), font=font)
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Image generation placeholder failed: {e}")
            raise e
