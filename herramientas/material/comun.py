"""Utilidades compartidas por los scripts de material (Mac, Windows y Linux)."""
import json
import subprocess
import sys
from pathlib import Path

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:  # sin HEIC solo se procesan JPG/PNG
    pass

EXT_FOTO = {".heic", ".jpg", ".jpeg", ".png", ".gif"}
EXT_VIDEO = {".mov", ".mp4"}


def carpeta_raiz() -> Path:
    """Carpeta de material que se pasa como primer argumento."""
    if len(sys.argv) < 2:
        sys.exit(f"Uso: python {Path(sys.argv[0]).name} <carpeta de material> [opciones]")
    raiz = Path(sys.argv[1]).expanduser().resolve()
    if not raiz.is_dir():
        sys.exit(f"No existe la carpeta: {raiz}")
    return raiz


def ficheros_sueltos(raiz: Path, extensiones: set) -> list:
    """Ficheros de la raíz (no entra en subcarpetas como _analisis o _DESCARTADOS)."""
    return sorted(
        f.name for f in raiz.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in extensiones
    )


def carpeta_analisis(raiz: Path) -> Path:
    a = raiz / "_analisis"
    a.mkdir(exist_ok=True)
    return a


def nombre_miniatura(archivo: str) -> str:
    """IMG_0001.HEIC -> IMG_0001.heic.jpg (evita choques entre IMG_0001.HEIC e IMG_0001.JPG)."""
    p = Path(archivo)
    return f"{p.stem}{p.suffix.lower()}.jpg"


def leer_analisis(raiz: Path) -> dict:
    ruta = raiz / "_analisis" / "analisis.jsonl"
    if not ruta.exists():
        sys.exit("Falta _analisis/analisis.jsonl: ejecuta antes 1_analizar.py")
    datos = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(linea)
            datos[r["file"]] = r
        except (json.JSONDecodeError, KeyError):
            pass  # línea cortada por una ejecución interrumpida
    return datos


def ffprobe(ruta: Path) -> dict:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration", "-of", "json", str(ruta)],
        capture_output=True, text=True,
    ).stdout
    o = json.loads(salida)
    s = o["streams"][0]
    return {"w": s["width"], "h": s["height"], "dur": float(o["format"].get("duration", 0))}
