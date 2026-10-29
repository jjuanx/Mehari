"""Tapa matrículas y emblemas de una foto sin que se note (alternativa al difuminado).

Uso:
    python retocar_foto.py <entrada> <salida> [--placa X,Y,X,Y,...] [--emblema X,Y,AN,AL]
                           [--conservar X,Y,AN,AL --desde <foto>] [--umbral 28] [--dilatar 7]

- `--placa`: polígono interior de la matrícula (al menos 4 vértices, en píxeles de la entrada).
  Se borran los caracteres y la placa se rellena con su propio sombreado: queda una placa lisa,
  con su forma, su marco y la banda azul europea. Se puede repetir.
- `--emblema`: caja de un emblema sobre chapa lisa (capó, calandra). Se rellena con el color
  de la chapa de alrededor (inpainting). Se puede repetir.
- `--conservar` + `--desde`: copia esa caja de otra foto del mismo tamaño (por ejemplo, la versión
  difuminada) cuando una zona no se puede retocar bien y se va a dejar fuera del encuadre.
- `--umbral` y `--dilatar`: si quedan restos de letra, bájese el umbral (16) y súbase la dilatación (11).

Para marcar el polígono, abre la foto en cualquier visor con coordenadas y apunta las esquinas
por dentro del borde de la placa. Revisa siempre el resultado a tamaño real: el retoque no sustituye
a `revision-marca`. Necesita opencv-python.
"""
import argparse

import cv2
import numpy as np


def placa_lisa(img, poli, umbral=28, dil=7):
    m = np.zeros(img.shape[:2], np.uint8)
    cv2.fillPoly(m, [np.array(poli, np.int32)], 1)
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mediana = np.median(gris[m > 0])
    azul = (hsv[..., 1] > 90) & (hsv[..., 0] > 95) & (hsv[..., 0] < 130)
    letras = ((gris < mediana - umbral) & ~azul).astype(np.uint8) & m
    letras = cv2.dilate(letras, np.ones((dil, dil), np.uint8)) & m
    # Sombreado de la placa a partir de sus píxeles blancos (convolución normalizada)
    blanco = (m & (1 - letras) & (~azul).astype(np.uint8)).astype(np.float32)
    f = img.astype(np.float32)
    num = cv2.GaussianBlur(f * blanco[..., None], (0, 0), 12)
    den = cv2.GaussianBlur(blanco, (0, 0), 12)[..., None] + 1e-4
    ruido = np.random.default_rng(0).normal(0, 2.0, img.shape).astype(np.float32)
    relleno = np.clip(num / den + ruido, 0, 255)
    a = cv2.GaussianBlur(letras.astype(np.float32), (0, 0), 1.5)[..., None]
    return (relleno * a + f * (1 - a)).astype(np.uint8)


def emblema(img, x, y, w, h):
    pad = int(0.25 * max(w, h))
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(img.shape[1], x + w + pad), min(img.shape[0], y + h + pad)
    crop = img[y0:y1, x0:x1].copy()
    anillo = np.ones(crop.shape[:2], bool)
    anillo[pad // 2:-(pad // 2) or None, pad // 2:-(pad // 2) or None] = False
    ref = np.median(crop[anillo], axis=0)
    lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB).astype(np.float32)
    ref_lab = cv2.cvtColor(np.uint8([[ref]]), cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]
    dist = np.linalg.norm(lab - ref_lab, axis=2)
    mask = np.zeros(crop.shape[:2], np.uint8)
    cx, cy = x - x0, y - y0
    mask[cy:cy + h, cx:cx + w] = (dist[cy:cy + h, cx:cx + w] > 22).astype(np.uint8)
    mask = cv2.dilate(mask, np.ones((7, 7), np.uint8))
    rel = cv2.inpaint(crop, mask * 255, 11, cv2.INPAINT_TELEA)
    alfa = np.zeros(crop.shape[:2], np.float32)
    alfa[cv2.dilate(mask, np.ones((15, 15), np.uint8)) > 0] = 1
    alfa = cv2.GaussianBlur(alfa, (0, 0), 4)[..., None]
    img[y0:y1, x0:x1] = (rel * alfa + crop * (1 - alfa)).astype(np.uint8)


def numeros(texto, n=None):
    v = [int(round(float(t))) for t in texto.split(",")]
    if n and len(v) != n:
        raise SystemExit(f"Se esperaban {n} números: {texto}")
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--placa", action="append", default=[])
    ap.add_argument("--emblema", action="append", default=[])
    ap.add_argument("--conservar", action="append", default=[])
    ap.add_argument("--desde")
    ap.add_argument("--umbral", type=float, default=28)
    ap.add_argument("--dilatar", type=int, default=7)
    a = ap.parse_args()

    img = cv2.imread(a.entrada)
    if img is None:
        raise SystemExit(f"No se puede abrir: {a.entrada}")
    for e in a.emblema:
        emblema(img, *numeros(e, 4))
    for p in a.placa:
        v = numeros(p)
        if len(v) < 8 or len(v) % 2:
            raise SystemExit(f"El polígono necesita al menos 4 vértices X,Y: {p}")
        img = placa_lisa(img, list(zip(v[::2], v[1::2])), a.umbral, a.dilatar)
    if a.conservar:
        otra = cv2.imread(a.desde) if a.desde else None
        if otra is None or otra.shape != img.shape:
            raise SystemExit("--conservar necesita --desde con una foto del mismo tamaño")
        for c in a.conservar:
            x, y, w, h = numeros(c, 4)
            img[y:y + h, x:x + w] = otra[y:y + h, x:x + w]
    cv2.imwrite(a.salida, img, [cv2.IMWRITE_JPEG_QUALITY, 95])


if __name__ == "__main__":
    main()
