"""Vectoriza un logo PNG de color plano y lo guarda como SVG, en uno o varios colores.

Uso:
    python vectorizar_logo.py <entrada.png> <salida-base> [--color nombre=#RRGGBB ...] [--margen 0.04]

Crea <salida-base>-<nombre>.svg por cada --color (por defecto, solo el color original del PNG).
Se usa cuando la grafista entrega el logo en EPS de Illustrator y no hay Ghostscript ni Illustrator
para exportarlo: se traza el PNG a alta resolución (canal alfa) con potrace y se obtienen curvas Bézier.
Revisa el resultado a tamaño grande. Si la grafista puede exportar el SVG desde Illustrator, es mejor.
Necesita opencv-python y potracer.
"""
import argparse

import cv2
import numpy as np
import potrace


def trazar(alfa):
    bmp = potrace.Bitmap(alfa <= 127)  # potracer traza lo oscuro (valor 0)
    ruta = bmp.trace(turdsize=4, alphamax=1.0, opticurve=True, opttolerance=0.2)
    partes = []
    for curva in ruta:
        p = curva.start_point
        d = [f"M{p.x:.1f} {p.y:.1f}"]
        for seg in curva.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f} {seg.c.y:.1f}L{seg.end_point.x:.1f} {seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f} {seg.c1.y:.1f} {seg.c2.x:.1f} {seg.c2.y:.1f} "
                         f"{seg.end_point.x:.1f} {seg.end_point.y:.1f}")
        partes.append("".join(d) + "Z")
    return "".join(partes)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--color", action="append", default=[])
    ap.add_argument("--margen", type=float, default=0.04, help="aire alrededor, en fracción del lado mayor")
    a = ap.parse_args()

    img = cv2.imread(a.entrada, cv2.IMREAD_UNCHANGED)
    if img is None or img.shape[2] != 4:
        raise SystemExit(f"Hace falta un PNG con transparencia: {a.entrada}")
    alfa = img[..., 3]
    ys, xs = np.where(alfa > 127)
    m = int(a.margen * max(np.ptp(xs), np.ptp(ys)))
    x0, y0 = max(0, xs.min() - m), max(0, ys.min() - m)
    x1, y1 = min(alfa.shape[1], xs.max() + m + 1), min(alfa.shape[0], ys.max() + m + 1)
    recorte = alfa[y0:y1, x0:x1]
    d = trazar(recorte)

    colores = dict(c.split("=", 1) for c in a.color)
    if not colores:
        b, g, r = np.median(img[..., :3][alfa > 250], axis=0)
        colores = {"original": f"#{int(r):02X}{int(g):02X}{int(b):02X}"}
    w, h = x1 - x0, y1 - y0
    for nombre, hexa in colores.items():
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
               f'<path fill="{hexa}" fill-rule="evenodd" d="{d}"/></svg>\n')
        with open(f"{a.salida}-{nombre}.svg", "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"{a.salida}-{nombre}.svg  {w}x{h}  {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
