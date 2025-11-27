#!/usr/bin/env python3
"""
Ponto de entrada para worker Celery.

Este script pode ser usado para iniciar workers Celery em diferentes ambientes.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar configuração do Celery
from app.worker.celery_app import celery_app

if __name__ == '__main__':
    # Executar worker Celery
    celery_app.start()