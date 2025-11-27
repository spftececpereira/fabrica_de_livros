from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, books, websocket

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(websocket.router, prefix="/websocket", tags=["websocket"])
