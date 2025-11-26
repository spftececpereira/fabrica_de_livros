from app.worker.celery_app import celery_app
from app.services.ai.factory import AIProviderFactory
from app.core.database import AsyncSessionLocal
from app.models.book import Book, Page, BookStatus
from app.models.user import User
from sqlalchemy import select
import asyncio

async def generate_book_logic(book_id: int, theme: str, style: str):
    async with AsyncSessionLocal() as session:
        book = None
        try:
            # 1. Fetch Book
            result = await session.execute(select(Book).where(Book.id == book_id))
            book = result.scalars().first()
            if not book:
                return "Book not found"

            # 2. Generate Story (Text)
            provider = AIProviderFactory.create(provider="gemini")
            prompt = f"Write a children's story about {theme}. The story should be suitable for a coloring book. Split the story into 5 distinct pages/scenes. Format the output as 'Page 1: [text]', 'Page 2: [text]', etc."
            
            story_text = await provider.generate_text(prompt)
            
            # 3. Parse and Save Pages
            # Simple parsing logic (robust parsing would be better)
            lines = story_text.split('\n')
            current_page_num = 0
            current_text = []
            
            for line in lines:
                if "Page" in line and ":" in line:
                    if current_page_num > 0:
                        # Save previous page
                        page = Page(
                            book_id=book.id,
                            page_number=current_page_num,
                            text_content="\n".join(current_text).strip()
                        )
                        session.add(page)
                    
                    # Start new page
                    try:
                        # Extract number "Page 1:" -> 1
                        parts = line.split(":")
                        page_part = parts[0].strip() # "Page 1"
                        current_page_num = int(page_part.split(" ")[1])
                        current_text = [parts[1].strip()] if len(parts) > 1 else []
                    except:
                        current_page_num += 1 # Fallback
                        current_text = []
                else:
                    current_text.append(line)
            
            # Save last page
            if current_page_num > 0:
                page = Page(
                    book_id=book.id,
                    page_number=current_page_num,
                    text_content="\n".join(current_text).strip()
                )
                session.add(page)

            # 4. Update Book Status
            book.status = BookStatus.COMPLETED
            await session.commit()
            return f"Book {book_id} generated successfully"

        except Exception as e:
            # Handle failure
            if book:
                book.status = BookStatus.FAILED
                await session.commit()
            return f"Error generating book: {str(e)}"

@celery_app.task(acks_late=True)
def generate_story_task(book_id: int, theme: str, style: str) -> str:
    """
    Async task wrapper
    """
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    result = loop.run_until_complete(generate_book_logic(book_id, theme, style))
    return result

@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"
