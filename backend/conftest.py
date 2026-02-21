"""Pytest configuration file."""
import sys
from pathlib import Path

# Ajouter le dossier backend au sys.path pour que les imports fonctionnent
sys.path.insert(0, str(Path(__file__).parent))
