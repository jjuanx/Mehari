"""Rutas fijas del repositorio que usan las herramientas de piezas."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRABAJO = REPO / ".trabajo"
PLANTILLAS = REPO / "marca/plantillas"
MATERIAL = REPO / "herramientas/material"
