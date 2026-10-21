"""Descarga las fotos de las historias desde Drive y las deja listas para componer.

Uso (desde esta carpeta):
    python preparar.py            # descarga lo que falte y limpia todo
    python preparar.py --limpiar  # solo limpia (las fotos ya están en fotos/)

1. Descarga a `fotos/` cada foto de `ids.txt` (selección de Drive, enlace de lectura).
2. Gira según el EXIF, difumina las zonas de TAPAR (matrículas, emblema del fabricante,
   funda de rueda), recorta lo que indica RECORTAR y reduce a 2400 px de lado mayor.
3. Guarda el resultado en `limpias/`, que es lo que usa `historias.html`.

`fotos/` y `limpias/` no se suben a Git (material del cliente, ver CLAUDE.md §5).
Las cajas van en fracciones de la foto ya girada: (x0, y0, x1, y1).
"""
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

AQUI = Path(__file__).parent
FOTOS = AQUI / "fotos"
LIMPIAS = AQUI / "limpias"
LADO_MAX = 2400

TAPAR = {
    "F0005": [(0.40, 0.85, 0.63, 0.92), (0.48, 0.785, 0.535, 0.825)],
    "F0009": [(0.415, 0.745, 0.59, 0.84), (0.48, 0.63, 0.52, 0.675)],
    "F0015": [(0.585, 0.535, 0.735, 0.62), (0.645, 0.44, 0.68, 0.475)],
    "F0058": [(0.065, 0.71, 0.245, 0.805), (0.15, 0.565, 0.185, 0.60)],
    "F0180": [(0.435, 0.77, 0.645, 0.825), (0.51, 0.665, 0.545, 0.695)],
    "F0345": [(0.405, 0.88, 0.445, 0.96)],
    "F0524": [(0.375, 0.65, 0.50, 0.72), (0.40, 0.535, 0.425, 0.565)],
    "F0750": [(0.615, 0.545, 0.80, 0.64), (0.675, 0.41, 0.71, 0.445)],
    "F0834": [(0.69, 0.70, 0.88, 0.795), (0.76, 0.605, 0.79, 0.64)],
    "F1163": [(0.44, 0.735, 0.61, 0.80), (0.51, 0.565, 0.55, 0.605), (0.515, 0.70, 0.545, 0.73)],
    "F1839": [(0.085, 0.79, 0.245, 0.915), (0.195, 0.675, 0.235, 0.71)],
    "F1958": [(0.17, 0.42, 0.31, 0.78)],
    "F2041": [(0.07, 0.57, 0.10, 0.60)],
    "F2194": [(0.785, 0.775, 0.89, 0.85), (0.805, 0.655, 0.835, 0.685)],
}

# Rótulo del fabricante y matrícula en el tercio inferior: se quedan fuera del recorte
RECORTAR = {
    "F2067": (0.0, 0.0, 1.0, 0.79),
}


def descargar():
    FOTOS.mkdir(exist_ok=True)
    for linea in (AQUI / "ids.txt").read_text(encoding="utf-8").split("\n"):
        if not linea.strip():
            continue
        nombre, id_drive = linea.split()
        destino = FOTOS / f"{nombre}.jpg"
        if destino.exists():
            continue
        url = f"https://drive.usercontent.google.com/download?id={id_drive}&export=download"
        print("Descargando", nombre)
        urllib.request.urlretrieve(url, destino)


def caja_px(caja, ancho, alto):
    x0, y0, x1, y1 = caja
    return int(x0 * ancho), int(y0 * alto), int(x1 * ancho), int(y1 * alto)


def limpiar():
    LIMPIAS.mkdir(exist_ok=True)
    for ruta in sorted(FOTOS.glob("*.jpg")):
        nombre = ruta.stem
        im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
        ancho, alto = im.size
        for caja in TAPAR.get(nombre, []):
            x0, y0, x1, y1 = caja_px(caja, ancho, alto)
            zona = im.crop((x0, y0, x1, y1))
            radio = max(12, (x1 - x0) // 4)
            borrosa = zona.resize((max(1, zona.width // 12), max(1, zona.height // 12))).resize(zona.size)
            borrosa = borrosa.filter(ImageFilter.GaussianBlur(radio))
            mascara = Image.new("L", zona.size, 0)
            ImageDraw.Draw(mascara).rounded_rectangle((0, 0, zona.width - 1, zona.height - 1), radius=radio, fill=255)
            im.paste(borrosa, (x0, y0), mascara.filter(ImageFilter.GaussianBlur(max(2, radio // 8))))
        if nombre in RECORTAR:
            im = im.crop(caja_px(RECORTAR[nombre], ancho, alto))
        im.thumbnail((LADO_MAX, LADO_MAX), Image.LANCZOS)
        im.save(LIMPIAS / f"{nombre}.jpg", quality=90)
        print("Limpia", nombre, im.size)


if __name__ == "__main__":
    if "--limpiar" not in sys.argv:
        descargar()
    limpiar()
