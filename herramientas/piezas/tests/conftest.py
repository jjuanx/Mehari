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


@pytest.fixture
def entrega_preparada(pieza_minima, tmp_path):
    """Fábrica: (ruta_pieza, salidas, proyecto) de un carrusel listo para entregar.

    Con pendiente=True la pieza tiene caras sin permiso (no se puede publicar).
    """
    import json
    from ayudas import escribir_preparado
    contador = []

    def fabrica(pendiente=False, avisos=None):
        contador.append(1)
        raiz = tmp_path / f"entrega{len(contador)}"
        raiz.mkdir()
        p = pieza_minima("deslizar")
        p["hay_caras"] = bool(pendiente)
        p["permiso_caras"] = "pendiente" if pendiente else "si"
        p["ubicacion"] = "Finca La Posadilla"
        p["a_mano_despues"] = ["Etiquetar a la finca"]
        p["elementos"][0]["revision_marca"] = "APTA CON RETOQUE: funda de rueda"
        p["elementos"][0]["retoques"] = [{"tipo": "funda", "poligono": [[10, 10], [60, 10], [60, 40], [10, 40]]}]
        ruta = raiz / "pieza.json"
        ruta.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
        salidas = raiz / "salidas"
        salidas.mkdir()
        ficheros = []
        for i in range(1, 7):  # 5 fotos + cierre
            f = salidas / f"{i:02d}.jpg"
            Image.new("RGB", (1080, 1440), (200, 200, 200)).save(f, quality=90)
            ficheros.append(f)
        proyecto = raiz / "proyecto"
        (proyecto / "revision").mkdir(parents=True)
        for n in ("01_antes.jpg", "01_despues.jpg"):
            Image.new("RGB", (80, 60), (10, 10, 10)).save(proyecto / "revision" / n)
        (proyecto / "revision" / "avisos.json").write_text(
            json.dumps(avisos or [], ensure_ascii=False), encoding="utf-8")
        escribir_preparado(proyecto, p)
        return ruta, ficheros, proyecto

    return fabrica


def pytest_configure(config):
    config.addinivalue_line("markers", "lento: render real con HyperFrames (varios minutos)")


def _clip_de_prueba(ruta: Path, segundos: float, filtro: str = "testsrc") -> Path:
    _ffmpeg("-f", "lavfi", "-i", f"{filtro}=size=1080x1920:rate=30", "-t", str(segundos),
            "-pix_fmt", "yuv420p", str(ruta))
    return ruta


@pytest.fixture
def pieza_reel_preparada(pieza_minima, foto_jpg, tmp_path):
    """Fábrica: (pieza, proyecto) de un reel de 16 s (3 clips, 1 foto, música) ya preparado.

    El gancho y la prueba llevan rótulo (el del gancho con comillas, «&» y «<»).
    """
    def fabrica(variante="limpio", musica=True):
        from preparar import preparar
        boda = tmp_path / "boda"
        boda.mkdir(exist_ok=True)
        for i, filtro in ((1, "testsrc"), (3, "testsrc2"), (4, "smptebars")):
            _clip_de_prueba(boda / f"clip{i}.mp4", 5, filtro)
        shutil.copy(foto_jpg, boda / "IMG_2.jpg")
        p = pieza_minima("reel")
        p["variante"] = variante
        p["elementos"] = [
            {"orden": 1, "fichero": "clip1.mp4", "desde": 0, "hasta": 3, "tramo": "gancho",
             "rotulo": 'Salís "de" la iglesia & <ya>'},
            {"orden": 2, "fichero": "IMG_2.jpg", "duracion": 3, "tramo": "detalle"},
            {"orden": 3, "fichero": "clip3.mp4", "desde": 0, "hasta": 3, "tramo": "prueba",
             "rotulo": "Las cestas, llenas de flores"},
            {"orden": 4, "fichero": "clip4.mp4", "desde": 1, "hasta": 4, "tramo": "momento"},
        ]
        if musica:
            pista = tmp_path / "Pista libre.m4a"
            _ffmpeg("-f", "lavfi", "-i", "sine=frequency=440:duration=20", "-c:a", "aac", str(pista))
            p["musica"] = {"ruta": str(pista), "licencia": "prueba"}
        proyecto = tmp_path / "proyecto"
        preparar(p, boda, proyecto)
        return p, proyecto

    return fabrica


@pytest.fixture
def pieza_historia_clip_preparada(pieza_minima, tmp_path):
    """Fábrica: (pieza, proyecto) de una historia en clip con n clips de 3 s ya preparados."""
    def fabrica(n_clips=1):
        from preparar import preparar
        boda = tmp_path / "boda"
        boda.mkdir(exist_ok=True)
        elementos = []
        for i in range(1, n_clips + 1):
            _clip_de_prueba(boda / f"clip{i}.mp4", 4)
            elementos.append({"orden": i, "fichero": f"clip{i}.mp4", "desde": 0, "hasta": 3})
        p = pieza_minima("historia") | {"variante": "clip-cta", "elementos": elementos}
        proyecto = tmp_path / "proyecto"
        preparar(p, boda, proyecto)
        return p, proyecto

    return fabrica
