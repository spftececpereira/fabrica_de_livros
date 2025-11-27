"""
Módulo de repositórios para acesso aos dados.

Este módulo implementa o Repository Pattern para abstrair
o acesso aos dados e facilitar testes unitários.
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .book_repository import BookRepository

__all__ = [
    "BaseRepository",
    "UserRepository", 
    "BookRepository",
]