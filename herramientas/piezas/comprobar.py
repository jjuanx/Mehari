"""Controles automáticos antes de entregar una pieza: formato de los medios y texto."""
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

TELEFONO = "625 06 42 93"
MAX_HASHTAGS = 5
TOLERANCIA_DURACION = 0.05
TOLERANCIA_FPS = 0.01
RE_HASHTAG = re.compile(r"#\w+")
RE_PENDIENTE = re.compile(r"\[[^\[\]]*\]")
RE_AVISO = re.compile(r"\b(sevilla|sevillan[oa]s?|c[aá]diz)\b", re.IGNORECASE)
# Marca antigua: se busca en el texto en minúsculas y sin tildes
RE_MARCA_ANTIGUA = re.compile(r"tour\s*sur|mehari[_ ]?experiences")


@dataclass
class ResultadoTexto:
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    pendientes: list[str] = field(default_factory=list)


def _sin_tildes(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def _reglas_comunes(texto: str, donde: str) -> ResultadoTexto:
    """Reglas de redacción que valen para cualquier texto que se publica o se incrusta."""
    r = ResultadoTexto()
    bajo = texto.lower()
    if "citroën" in bajo or "citroen" in bajo:
        r.errores.append(f"{donde} nombra a «Citroën»")
    if "—" in texto:
        r.errores.append(f"{donde} contiene la raya «—»")
    if "experiencia única" in bajo or "experiencia unica" in bajo:
        r.errores.append(f"{donde} contiene «experiencia única»")
    for m in sorted({m.group(0) for m in RE_MARCA_ANTIGUA.finditer(_sin_tildes(texto))}):
        r.errores.append(f"{donde} nombra la marca antigua («{m}»)")
    for m in sorted({m.group(0).lower() for m in RE_AVISO.finditer(texto)}):
        r.avisos.append(f"{donde} menciona «{m}»: la marca no se ata a una ciudad")
    r.pendientes = RE_PENDIENTE.findall(texto)
    return r


def comprobar_texto(texto: str) -> ResultadoTexto:
    """Aplica las reglas de redacción de la marca al texto (copy) de la publicación."""
    r = _reglas_comunes(texto, "el texto")
    n = len(RE_HASHTAG.findall(texto))
    if n > MAX_HASHTAGS:
        r.errores.append(f"el texto tiene {n} hashtags (máximo {MAX_HASHTAGS})")
    if TELEFONO not in texto:
        r.errores.append(f"falta el teléfono {TELEFONO}")
    return r


def comprobar_textos_pieza(p: dict) -> ResultadoTexto:
    """Copy, rótulos, ubicación y «a mano en la app» de una pieza.

    Los rótulos, la ubicación y las líneas de a_mano_despues siguen las mismas reglas que el
    copy salvo el teléfono y el número de hashtags. Sus marcadores [..] cuentan como
    pendientes, con el sitio donde están entre paréntesis.
    """
    total = comprobar_texto(p.get("texto") or "")
    otros = [(f"el rótulo del elemento {int(el['orden']):02d}", el.get("rotulo"))
             for el in sorted(p.get("elementos", []), key=lambda e: e["orden"])]
    otros.append(("la ubicación", p.get("ubicacion")))
    otros += [(f"«A mano en la app» (línea {i})", x)
              for i, x in enumerate(p.get("a_mano_despues") or [], 1)]
    for donde, texto in otros:
        if not texto:
            continue
        r = _reglas_comunes(texto, donde)
        total.errores += r.errores
        total.avisos += r.avisos
        corto = donde.removeprefix("el ").removeprefix("la ")
        total.pendientes += [f"{x} ({corto})" for x in r.pendientes]
    return total


# ---------------------------------------------------------------- medios

def _num(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


def _fraccion(s: str | None) -> float | None:
    try:
        a, _, b = (s or "").partition("/")
        return float(a) / float(b) if b else float(a)
    except (ValueError, ZeroDivisionError):
        return None


def _sonda(ruta: Path) -> dict:
    """Datos de ffprobe: flujos y formato. Lanza ValueError si no es un vídeo legible."""
    try:
        sal = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(ruta)],
            capture_output=True, text=True, check=True).stdout
        return json.loads(sal)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError) as e:
        raise ValueError(f"no se puede leer con ffprobe ({type(e).__name__})") from e


def _dimensiones(flujo: dict) -> tuple[int, int]:
    """Ancho y alto tal como se ve el vídeo, teniendo en cuenta la rotación."""
    ancho, alto = int(flujo["width"]), int(flujo["height"])
    rot = flujo.get("tags", {}).get("rotate")
    for lado in flujo.get("side_data_list", []):
        if "rotation" in lado:
            rot = lado["rotation"]
    if rot is not None and int(float(rot)) % 180 != 0:
        ancho, alto = alto, ancho
    return ancho, alto


def _errores_jpeg(ruta: Path, tam: tuple[int, int]) -> list[str]:
    try:
        with Image.open(ruta) as img:
            formato, dims = img.format, img.size
    except Exception:
        return [f"{ruta.name}: no es una imagen legible"]
    errores = []
    if formato != "JPEG":
        errores.append(f"{ruta.name}: formato {formato} (debe ser JPEG)")
    if dims != tam:
        errores.append(f"{ruta.name}: dimensiones {dims[0]}×{dims[1]} (deben ser {tam[0]}×{tam[1]})")
    return errores


def _errores_video(ruta: Path, minimo: float | None, maximo: float) -> list[str]:
    n = ruta.name
    try:
        datos = _sonda(ruta)
        video = next(f for f in datos["streams"] if f.get("codec_type") == "video")
    except (ValueError, StopIteration):
        return [f"{n}: no es un vídeo legible"]
    errores = []
    if video.get("codec_name") != "h264":
        errores.append(f"{n}: códec {video.get('codec_name')} (debe ser h264)")
    if _dimensiones(video) != (1080, 1920):
        a, h = _dimensiones(video)
        errores.append(f"{n}: dimensiones {a}×{h} (deben ser 1080×1920)")
    for clave in ("r_frame_rate", "avg_frame_rate"):
        fps = _fraccion(video.get(clave))
        if fps is None or abs(fps - 30) > TOLERANCIA_FPS:
            errores.append(f"{n}: {clave.split('_')[0]} fps "
                           f"{_num(fps) if fps is not None else '?'} (deben ser 30)")
            break
    try:
        dur = float(datos["format"]["duration"])
    except (KeyError, ValueError):
        dur = None
    if dur is None:
        errores.append(f"{n}: duración desconocida")
    elif minimo is not None and not minimo - TOLERANCIA_DURACION <= dur <= maximo + TOLERANCIA_DURACION:
        errores.append(f"{n}: duración {_num(dur)} s (debe estar entre {minimo:g} y {maximo:g} s)")
    elif minimo is None and dur > maximo + TOLERANCIA_DURACION:
        errores.append(f"{n}: duración {_num(dur)} s (debe ser de {maximo:g} s como máximo)")
    for flujo in datos["streams"]:
        if flujo.get("codec_type") == "audio" and flujo.get("codec_name") != "aac":
            errores.append(f"{n}: audio {flujo.get('codec_name')} (debe ser AAC)")
    return errores


def comprobar_medios(formato: str, variante: str, ficheros: list[Path]) -> list[str]:
    """Devuelve los errores de formato de los ficheros de una pieza (lista vacía si todo bien)."""
    ficheros = [Path(f) for f in ficheros]
    errores = []
    if formato == "deslizar" and not 2 <= len(ficheros) <= 10:
        errores.append(f"el carrusel tiene {len(ficheros)} ficheros (debe tener de 2 a 10)")
    for f in ficheros:
        ext = f.suffix.lower()
        if not f.is_file():
            errores.append(f"{f.name}: no existe")
        elif formato == "reel" and ext == ".mp4":
            errores += _errores_video(f, 15.0, 25.0)
        elif formato == "reel" and f.name == "portada.jpg":
            errores += _errores_jpeg(f, (1080, 1920))
        elif formato == "historia" and ext == ".mp4":
            errores += _errores_video(f, None, 15.0)
        elif formato == "historia" and ext in (".jpg", ".jpeg"):
            errores += _errores_jpeg(f, (1080, 1920))
        elif formato == "deslizar" and ext in (".jpg", ".jpeg"):
            errores += _errores_jpeg(f, (1080, 1440))
        else:
            errores.append(f"{f.name}: fichero no válido para {formato}")
    return errores


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("uso: comprobar.py <pieza.json> <fichero>...", file=sys.stderr)
        return 2
    pieza = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    texto = comprobar_textos_pieza(pieza)
    errores = comprobar_medios(pieza["formato"], pieza["variante"], [Path(a) for a in argv[1:]])
    salida = {"errores": errores + texto.errores, "avisos": texto.avisos,
              "pendientes": texto.pendientes}
    print(json.dumps(salida, ensure_ascii=False, indent=2))
    return 1 if salida["errores"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
