import copy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

# Permite `import pieza`, `import rutas`... desde las pruebas.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

TEXTO_VALIDO = "Las cestas, llenas de flores. Pide presupuesto: 625 06 42 93 #boda #mehariwe"


@pytest.fixture
def foto_jpg(tmp_path) -> Path:
    """3024x4032 (vertical) con un rectángulo rojo conocido en (300,400)-(900,1000)."""
    img = Image.new("RGB", (3024, 4032), (240, 240, 240))
    ImageDraw.Draw(img).rectangle([300, 400, 900, 1000], fill=(200, 30, 30))
    ruta = tmp_path / "foto.jpg"
    img.save(ruta, quality=95)
    return ruta


@pytest.fixture
def foto_rotada(tmp_path) -> Path:
    """JPEG guardado de 4032x3024 con EXIF Orientation=6 (se ve de 3024x4032)."""
    img = Image.new("RGB", (4032, 3024), (240, 240, 240))
    ImageDraw.Draw(img).rectangle([300, 400, 900, 1000], fill=(200, 30, 30))
    exif = Image.Exif()
    exif[0x0112] = 6
    ruta = tmp_path / "rotada.jpg"
    img.save(ruta, quality=95, exif=exif)
    return ruta


def _ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


@pytest.fixture
def clip_mp4(tmp_path) -> Path:
    """Vídeo vertical de 5 s, 1080x1920."""
    ruta = tmp_path / "clip.mp4"
    _ffmpeg("-f", "lavfi", "-i", "testsrc=size=1080x1920:rate=30", "-t", "5",
            "-pix_fmt", "yuv420p", str(ruta))
    return ruta


@pytest.fixture
def clip_rotado(tmp_path) -> Path:
    """Vertical guardado como 1920x1080 con rotación de 90° en los metadatos."""
    plano = tmp_path / "plano.mp4"
    ruta = tmp_path / "rotado.mp4"
    _ffmpeg("-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30", "-t", "5",
            "-pix_fmt", "yuv420p", str(plano))
    # -display_rotation es opción de entrada: se añade al remultiplexar sin recodificar.
    _ffmpeg("-display_rotation", "90", "-i", str(plano), "-c", "copy", str(ruta))
    return ruta


def _base(formato: str, variante: str, elementos: list) -> dict:
    return {
        "version": 1,
        "boda": "2026-10-24_la-posadilla",
        "formato": formato,
        "variante": variante,
        "tema": "las-cestas",
        "permiso_caras": "pendiente",
        "hay_caras": False,
        "musica": None,
        "ubicacion": None,
        "elementos": elementos,
        "texto": TEXTO_VALIDO,
        "pendientes": [],
    }


def _minima(formato: str) -> dict:
    if formato == "reel":
        tramos = ("gancho", "detalle", "prueba", "momento")
        return _base("reel", "limpio", [
            {"orden": i + 1, "fichero": f"clip{i + 1}.mov", "desde": 0, "hasta": 3, "tramo": t}
            for i, t in enumerate(tramos)])
    if formato == "deslizar":
        return _base("deslizar", "foto-entera", [
            {"orden": i + 1, "fichero": f"IMG_{i + 1}.HEIC"} for i in range(5)])
    if formato == "historia":
        return _base("historia", "foto-frase", [{"orden": 1, "fichero": "IMG_1.HEIC"}])
    raise ValueError(formato)


@pytest.fixture
def pieza_minima():
    """Fábrica: pieza_minima("reel") devuelve una pieza válida nueva cada vez."""
    return lambda formato: copy.deepcopy(_minima(formato))


@pytest.fixture
def drive_falso(tmp_path) -> Path:
    """Árbol mínimo de «Mehari We» con nombres reales (incluida la errata «Selecccion»)."""
    raiz = tmp_path / "Mehari We"
    for ruta in (
        "01_Material/Selecccion/Boda 24:10:2026/IMG_1.HEIC",
        "01_Material/Bodas/2026-11-07_sanlucar/fotos/a.jpg",
        "01_Material/Bodas/_interno/b.jpg",
        "01_Material/Selecccion/fotos/c.jpg",
        "01_Material/Galeria/thumbs/d.jpg",
    ):
        f = raiz / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"")
    return raiz


def _preparada(pieza_minima, foto_jpg, tmp_path, formato, variante, n_fotos, rotulo):
    from preparar import preparar
    p = pieza_minima(formato)
    p["variante"] = variante
    boda = tmp_path / "boda"
    boda.mkdir(exist_ok=True)
    elementos = []
    for i in range(1, n_fotos + 1):
        shutil.copy(foto_jpg, boda / f"IMG_{i}.jpg")
        el = {"orden": i, "fichero": f"IMG_{i}.jpg"}
        if rotulo is not None and i == 1:
            el["rotulo"] = rotulo
        elif rotulo is not None or variante == "con-rotulos":
            el["rotulo"] = f"Rótulo {i}"
        elementos.append(el)
    p["elementos"] = elementos
    proyecto = tmp_path / "proyecto"
    preparar(p, boda, proyecto)
    return p, proyecto


@pytest.fixture
def pieza_deslizar_preparada(pieza_minima, foto_jpg, tmp_path):
    """Fábrica: (pieza, proyecto) de un carrusel con las fotos ya preparadas."""
    return lambda n_fotos=5, rotulo=None, variante="foto-entera": _preparada(
        pieza_minima, foto_jpg, tmp_path, "deslizar", variante, n_fotos, rotulo)


@pytest.fixture
def pieza_historia_preparada(pieza_minima, foto_jpg, tmp_path):
    """Fábrica: (pieza, proyecto) de una historia en foto con las fotos ya preparadas."""
    return lambda n_fotos=1, rotulo="Vuestra boda, a vuestro ritmo": _preparada(
        pieza_minima, foto_jpg, tmp_path, "historia", "foto-frase", n_fotos, rotulo)
