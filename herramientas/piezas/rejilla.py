"""Rejilla de coordenadas sobre una foto o un fotograma, para leer vértices (matrícula, funda).

Las coordenadas son las de la imagen tal como se ve (tras `exif_transpose`) y los números
son siempre absolutos, aunque se recorte con --zona.

Uso: python3 herramientas/piezas/rejilla.py <fichero> <salida.jpg> [--zona X,Y,AN,AL] [--paso 50] [--t 1.2]
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rutas  # noqa: E402

sys.path.insert(0, str(rutas.MATERIAL))
from comun import EXT_VIDEO  # noqa: E402,F401  (registra también pillow_heif)


def _fotograma(video: Path, t: float, carpeta: Path) -> Path:
    destino = Path(tempfile.mkstemp(suffix=".png", dir=carpeta)[1])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(video),
                    "-frames:v", "1", str(destino)], check=True)
    return destino


def _fuente(tam: int):
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:
        return ImageFont.load_default()


def rejilla(entrada: Path, salida: Path, zona: tuple[int, int, int, int] | None = None,
            paso: int = 100, t: float = 0.0) -> Path:
    entrada, salida = Path(entrada), Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    temporal = None
    try:
        if entrada.suffix.lower() in EXT_VIDEO:
            temporal = _fotograma(entrada, t, salida.parent)
            origen = temporal
        else:
            origen = entrada
        with Image.open(origen) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
        x0, y0, x1, y1 = 0, 0, im.width, im.height
        if zona:
            x, y, an, al = zona
            x0, y0 = max(0, x), max(0, y)
            x1, y1 = min(im.width, x + an), min(im.height, y + al)
            im = im.crop((x0, y0, x1, y1))
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)

    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    tam = max(14, min(im.size) // 45)
    fuente = _fuente(tam)
    linea, texto = (255, 255, 0, 110), (255, 255, 0, 255)

    def etiqueta(pos, num):
        caja = d.textbbox(pos, str(num), font=fuente)
        d.rectangle(caja, fill=(0, 0, 0, 170))
        d.text(pos, str(num), fill=texto, font=fuente)

    primero_x = -(-x0 // paso) * paso
    for gx in range(primero_x, x1, paso):
        px = gx - x0
        d.line([(px, 0), (px, im.height)], fill=linea, width=1)
        etiqueta((px + 2, 2), gx)
    primero_y = -(-y0 // paso) * paso
    for gy in range(primero_y, y1, paso):
        py = gy - y0
        d.line([(0, py), (im.width, py)], fill=linea, width=1)
        etiqueta((2, py + 2), gy)

    Image.alpha_composite(im.convert("RGBA"), capa).convert("RGB").save(salida, quality=92)
    return salida


def main() -> None:
    ap = argparse.ArgumentParser(description="Rejilla de coordenadas sobre una foto o un fotograma.")
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--zona", help="X,Y,AN,AL en píxeles de la imagen tal como se ve")
    ap.add_argument("--paso", type=int, default=100)
    ap.add_argument("--t", type=float, default=0.0, help="segundo del fotograma (vídeos)")
    a = ap.parse_args()
    zona = tuple(int(v) for v in a.zona.split(",")) if a.zona else None
    if zona and len(zona) != 4:
        sys.exit("--zona necesita cuatro números: X,Y,AN,AL")
    print(rejilla(a.entrada, a.salida, zona, a.paso, a.t))


if __name__ == "__main__":
    main()
