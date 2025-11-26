from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from typing import List
from app.models.book import Book

class PDFService:
    @staticmethod
    def generate_book_pdf(book: Book) -> BytesIO:
        """
        Generates a PDF for the given book.
        Returns a BytesIO object containing the PDF data.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Title Page
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height / 2 + 50, book.title)
        c.setFont("Helvetica", 14)
        c.drawCentredString(width / 2, height / 2, f"Theme: {book.theme}")
        c.drawCentredString(width / 2, height / 2 - 30, f"Style: {book.style}")
        c.showPage()

        # Content Pages
        # Sort pages by page_number just in case
        sorted_pages = sorted(book.pages, key=lambda p: p.page_number)
        
        for page in sorted_pages:
            # Page Number
            c.setFont("Helvetica", 10)
            c.drawString(width - 50, 30, f"Page {page.page_number}")
            
            # Text Content
            text_y = height - 100
            if page.text_content:
                c.setFont("Helvetica", 12)
                # Simple text wrapping (very basic)
                text_lines = page.text_content.split('\n')
                for line in text_lines:
                    # Check if line is too long and wrap it roughly
                    if len(line) > 80:
                        # Very naive wrapping
                        chunks = [line[i:i+80] for i in range(0, len(line), 80)]
                        for chunk in chunks:
                            c.drawCentredString(width / 2, text_y, chunk)
                            text_y -= 20
                    else:
                        c.drawCentredString(width / 2, text_y, line)
                        text_y -= 20
            
            # Image Placeholder (since we don't have real images yet)
            # If image_url exists and is reachable, we could draw it.
            # For now, draw a placeholder rectangle.
            c.rect(100, height / 2 - 150, width - 200, 300)
            c.drawCentredString(width / 2, height / 2, "Image Placeholder")
            if page.image_prompt:
                 c.setFont("Helvetica-Oblique", 8)
                 c.drawCentredString(width / 2, height / 2 - 140, f"Prompt: {page.image_prompt[:50]}...")

            c.showPage()

        c.save()
        buffer.seek(0)
        return buffer
