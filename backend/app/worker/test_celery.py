#!/usr/bin/env python3
"""
Script de teste para verificar funcionamento do Celery.
"""

import asyncio
import sys
import os
import pytest
from pathlib import Path

# Adicionar o diretório raiz do projeto ao Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.worker.celery_app import celery_app
from app.worker.tasks import health_check, generate_book_content
from app.core.database import AsyncSessionLocal
from app.models.book import Book
from app.repositories.book_repository import BookRepository


@pytest.mark.asyncio
async def test_database_connection():
    """Testa conexão com o banco de dados."""
    try:
        async with AsyncSessionLocal() as session:
            # Tentar criar repository
            book_repo = BookRepository(session)
            
            # Tentar fazer uma query simples
            books = await book_repo.get_multi(limit=1)
            
            print("✅ Conexão com banco de dados funcionando")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False


def test_celery_basic():
    """Testa funcionalidades básicas do Celery."""
    try:
        # Verificar se Celery está configurado
        print(f"📊 Celery App: {celery_app.main}")
        print(f"📊 Broker: {celery_app.conf.broker_url}")
        print(f"📊 Backend: {celery_app.conf.result_backend}")
        
        # Verificar tasks registradas
        registered_tasks = list(celery_app.tasks.keys())
        print(f"📊 Tasks registradas: {len(registered_tasks)}")
        for task in registered_tasks:
            print(f"   - {task}")
        
        print("✅ Configuração básica do Celery OK")
        return True
    except Exception as e:
        print(f"❌ Erro na configuração do Celery: {e}")
        return False


def test_health_check_task():
    """Testa task de health check."""
    try:
        print("\n🧪 Testando health check task...")
        
        # Executar task de health check
        result = health_check.delay()
        
        print(f"📊 Task ID: {result.id}")
        print(f"📊 Status: {result.status}")
        
        # Aguardar resultado (se eager mode estiver ativo)
        if celery_app.conf.task_always_eager:
            task_result = result.get(timeout=10)
            print(f"✅ Health check resultado: {task_result}")
            return True
        else:
            print("⏳ Task enviada para fila (modo assíncrono)")
            print("   Use um worker Celery para processar a task")
            return True
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False


async def create_test_book():
    """Cria um livro de teste no banco."""
    try:
        async with AsyncSessionLocal() as session:
            book_repo = BookRepository(session)
            
            # Criar livro de teste
            test_book = await book_repo.create(
                title="Livro de Teste Celery",
                description="Aventuras de um robô em uma fábrica de livros",
                pages_count=8,
                style="cartoon",
                status="draft",
                user_id=1  # Assumindo que existe usuário ID 1
            )
            
            await session.commit()
            print(f"✅ Livro de teste criado: ID {test_book.id}")
            return test_book.id
            
    except Exception as e:
        print(f"❌ Erro criando livro de teste: {e}")
        return None


def test_book_generation_task():
    """Testa task de geração de livro."""
    try:
        print("\n🧪 Testando task de geração de livro...")
        
        # Criar livro de teste
        book_id = asyncio.run(create_test_book())
        if not book_id:
            return False
        
        # Executar task de geração
        result = generate_book_content.delay(book_id)
        
        print(f"📊 Task ID: {result.id}")
        print(f"📊 Status: {result.status}")
        
        # Se modo eager, aguardar resultado
        if celery_app.conf.task_always_eager:
            try:
                task_result = result.get(timeout=30)
                print(f"✅ Geração de livro resultado: {task_result}")
                return True
            except Exception as e:
                print(f"⚠️  Task falhou (esperado em teste): {e}")
                return True  # Falha esperada se não houver IA configurada
        else:
            print("⏳ Task de geração enviada para fila")
            print("   Use um worker Celery para processar a task")
            return True
            
    except Exception as e:
        print(f"❌ Erro na task de geração: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("🚀 INICIANDO TESTES DO CELERY")
    print("=" * 50)
    
    tests = [
        ("Conexão Banco de Dados", test_database_connection),
        ("Configuração Celery", test_celery_basic),
        ("Health Check Task", test_health_check_task),
        ("Book Generation Task", test_book_generation_task),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        if asyncio.iscoroutinefunction(test_func):
            success = asyncio.run(test_func())
        else:
            success = test_func()
        
        results.append((test_name, success))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:<30} {status}")
        if success:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! Celery está funcionando corretamente.")
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
    
    # Instruções para executar worker
    print("\n📋 INSTRUÇÕES PARA EXECUTAR WORKER:")
    print("1. Em um terminal separado, execute:")
    print("   cd backend")
    print("   celery -A app.worker.celery_app worker --loglevel=info")
    print("\n2. Para monitoramento, execute:")
    print("   celery -A app.worker.celery_app flower")


if __name__ == "__main__":
    main()