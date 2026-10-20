import os
import sys


def caminho_recurso(caminho_relativo: str) -> str:
    """Resolve um caminho de arquivo tanto rodando normal quanto empacotado com PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, caminho_relativo)
