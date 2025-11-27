from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from typing import List
import aiohttp
import os
from app.models.book import Book
from app.core.config import settings

class PDFService:
    
    @staticmethod
    async def _fetch_image(url_or_path: str) -> BytesIO:
        """
        Fetches image data from a URL or local path.
        """
        if url_or_path.startswith("http"):
            async with aiohttp.ClientSession() as session:
                async with session.get(url_or_path) as response:
                    if response.status == 200:
                        data = await response.read()
                        return BytesIO(data)
        else:
            # Assume local path (relative to project root or absolute)
            # If path starts with /, treat as absolute or relative to root
            # Adjust based on where files are stored.
            # Our LocalStorageProvider saves to 'frontend/public/uploads' and returns '/uploads/...'
            # We need to map that back to the file system.
            
            # Strip leading slash if present to join correctly
            clean_path = url_or_path.lstrip('/')
            
            # Try to find the file in frontend/public if it looks like a relative upload
            potential_path = os.path.join("frontend/public", clean_path)
            
            if os.path.exists(potential_path):
                 with open(potential_path, "rb") as f:
                     return BytesIO(f.read())
            elif os.path.exists(url_or_path):
                with open(url_or_path, "rb") as f:
                     return BytesIO(f.read())
                     
        return None

    @staticmethod
    async def generate_book_pdf(book: Book) -> str:
        """
        Generates a PDF for the given book and saves it.
        Returns the path/url to the generated PDF.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Title Page
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height / 2 + 50, book.title)
        c.setFont("Helvetica", 14)
        # Handle potential missing fields safely
        theme = getattr(book, 'theme', 'General')
        c.drawCentredString(width / 2, height / 2, f"Theme: {theme}")
        c.drawCentredString(width / 2, height / 2 - 30, f"Style: {book.style}")
        c.showPage()

        # Content Pages
        sorted_pages = sorted(book.pages, key=lambda p: p.page_number)
        
        for page in sorted_pages:
            # Page Number
            c.setFont("Helvetica", 10)
            c.drawString(width - 50, 30, f"Page {page.page_number}")
            
            # Text Content
            text_y = height - 100
            if page.text_content:
                c.setFont("Helvetica", 12)
                text_lines = page.text_content.split('\n')
                for line in text_lines:
                    if len(line) > 80:
                        chunks = [line[i:i+80] for i in range(0, len(line), 80)]
                        for chunk in chunks:
                            c.drawCentredString(width / 2, text_y, chunk)
                            text_y -= 20
                    else:
                        c.drawCentredString(width / 2, text_y, line)
                        text_y -= 20
            
            # Image Handling
            image_drawn = False
            if page.image_url:
                try:
                    img_data = await PDFService._fetch_image(page.image_url)
                    if img_data:
                        img = ImageReader(img_data)
                        # Draw image centered
                        img_width = 400
                        img_height = 300
                        x = (width - img_width) / 2
                        y = height / 2 - 150
                        c.drawImage(img, x, y, width=img_width, height=img_height, preserveAspectRatio=True)
                        image_drawn = True
                except Exception as e:
                    print(f"Failed to load image for page {page.page_number}: {e}")

            if not image_drawn:
                # Placeholder if image failed or missing
                c.rect(100, height / 2 - 150, width - 200, 300)
                c.drawCentredString(width / 2, height / 2, "Image Placeholder")
                if page.image_prompt:
                     c.setFont("Helvetica-Oblique", 8)
                     c.drawCentredString(width / 2, height / 2 - 140, f"Prompt: {page.image_prompt[:50]}...")

            c.showPage()

        c.save()
        buffer.seek(0)
        
        # Save PDF locally using Storage Service logic (conceptually)
        # For now, we save directly to the public uploads folder to return a URL
        filename = f"book_{book.id}.pdf"
        output_path = os.path.join("frontend/public/uploads", filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())
            
        return f"/uploads/{filename}"
