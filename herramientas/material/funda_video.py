"""Deja lisa la funda de la rueda de repuesto en un vídeo (borra «@MEHARI_TOURSUR» y el logo de Instagram).

Es `--funda` de `retocar_foto.py` aplicado fotograma a fotograma: el polígono se marca una vez y se
mueve con la funda, que se sigue con template matching. Se nota mucho menos que un difuminado.

Uso:
    python funda_video.py <entrada> <salida> T X,Y,AN,AL X1,Y1,X2,Y2,...

- T: segundo en el que se marcan la caja y el polígono.
- X,Y,AN,AL: caja que se sigue (la funda con un poco de margen), en píxeles del vídeo de entrada.
- X1,Y1,…: polígono de la funda en ese mismo instante, por dentro del borde y sin tocar velos ni
  ropa blanca, porque lo claro dentro del polígono se borra.

Imprime el peor parecido del seguimiento; por debajo de 0,8 hay que revisar el vídeo. La salida no
lleva audio y va en mp4v: vuelve a codificarla con FFmpeg (libx264) antes de montarla.
La entrada tiene que ser SDR (ver la cabecera de `difuminar.py`). Necesita opencv-python-headless.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from retocar_foto import funda_lisa  # noqa: E402


def main():
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    ent, sal, t0 = sys.argv[1], sys.argv[2], float(sys.argv[3])
    x, y, w, h = (int(v) for v in sys.argv[4].split(","))
    poli = np.array([int(v) for v in sys.argv[5].split(",")]).reshape(-1, 2)

    cap = cv2.VideoCapture(ent)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fs = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fs.append(f)
    if not fs:
        sys.exit(f"No se puede leer: {ent}")

    i0 = min(len(fs) - 1, int(round(t0 * fps)))
    cajas = [None] * len(fs)
    cajas[i0] = (x, y)
    peor = 1.0
    for paso in (1, -1):
        px, py = x, y
        tpl = cv2.cvtColor(fs[i0], cv2.COLOR_BGR2GRAY)[y:y + h, x:x + w]
        i = i0 + paso
        while 0 <= i < len(fs):
            g = cv2.cvtColor(fs[i], cv2.COLOR_BGR2GRAY)
            r = 50
            x0, y0 = max(0, px - r), max(0, py - r)
            zona = g[y0:min(g.shape[0], py + h + r), x0:min(g.shape[1], px + w + r)]
            _, v, _, loc = cv2.minMaxLoc(cv2.matchTemplate(zona, tpl, cv2.TM_CCOEFF_NORMED))
            peor = min(peor, v)
            px, py = x0 + loc[0], y0 + loc[1]
            cajas[i] = (px, py)
            tpl = g[py:py + h, px:px + w]  # la plantilla se actualiza: aguanta giros y cambios de escala lentos
            i += paso

    alto, ancho = fs[0].shape[:2]
    out = cv2.VideoWriter(sal, cv2.VideoWriter_fourcc(*"mp4v"), fps, (ancho, alto))
    for f, (cx, cy) in zip(fs, cajas):
        out.write(funda_lisa(f, (poli + [cx - x, cy - y]).tolist()))
    out.release()
    print("peor parecido", round(peor, 2))


if __name__ == "__main__":
    main()
