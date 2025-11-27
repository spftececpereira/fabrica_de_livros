import sys
import os
from pathlib import Path

# Add the backend directory to the Python path so that imports work correctly
# This assumes conftest.py is in backend/tests/
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
