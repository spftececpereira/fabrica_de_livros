from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Fábrica de Livros API",
    description="API para geração de livros infantis com IA",
    version="2.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.api import api_router
from app.core.config import settings

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Fábrica de Livros API v2"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
