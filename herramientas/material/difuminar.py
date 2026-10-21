"""Difumina matrículas, logos o caras en un vídeo siguiendo la zona fotograma a fotograma.

Uso:
    python difuminar.py <entrada> <salida> --zona T,X,Y,AN,AL [--zona ...] [--fija] [--radio 60]

- `--zona`: segundo del vídeo (T) en el que se marca la zona y su caja en píxeles del vídeo
  de entrada (X, Y, ancho, alto). Se puede repetir para tapar varias cosas. Opcionalmente,
  `T,X,Y,AN,AL,DESDE,HASTA` limita el difuminado a ese intervalo (en segundos), por ejemplo
  cuando la zona queda tapada o sale de plano.
- Ancla: si lo que hay que tapar queda oculto a ratos (una matrícula detrás de un velo), se
  sigue otra parte rígida del mismo objeto y la zona se mueve con ella:
  `T,X,Y,AN,AL[,DESDE,HASTA]/AX,AY,AAN,AAL` (caja del ancla en el mismo instante T).
- Sin `--fija`, la caja se sigue hacia delante y hacia atrás desde T con template matching
  (determinista: el mismo vídeo da siempre el mismo resultado). Con `--fija`, la caja no se mueve.
- `--radio`: cuántos píxeles puede desplazarse la zona entre dos fotogramas (por defecto 60).

Al terminar imprime, por zona, el peor parecido del seguimiento. Si baja de 0,5 hay que revisar
el vídeo: el seguimiento puede haberse perdido. Necesita FFmpeg en el PATH y opencv-python-headless.

La entrada tiene que ser SDR (BT.709). Los vídeos del iPhone vienen en HDR (HLG): conviértelos
antes, o los colores saldrán apagados y el naranja parecerá amarillo:
    ffmpeg -i entrada.mov -vf "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,
      tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" -c:v libx264 -crf 15 salida.mp4
"""
import argparse
import subprocess
import sys

import cv2
import numpy as np


def leer_fotogramas(ruta):
    cap = cv2.VideoCapture(ruta)
    if not cap.isOpened():
        sys.exit(f"No se puede abrir: {ruta}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    fotogramas = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        fotogramas.append(f)
    cap.release()
    return fotogramas, fps


def seguir(fotogramas, i0, caja, radio):
    """Devuelve una caja por fotograma y el peor parecido encontrado."""
    x, y, an, al = caja
    alto, ancho = fotogramas[0].shape[:2]
    cajas = [None] * len(fotogramas)
    cajas[i0] = (x, y)
    peor = 1.0
    for paso in (1, -1):
        px, py = x, y
        plantilla = cv2.cvtColor(fotogramas[i0], cv2.COLOR_BGR2GRAY)[y:y + al, x:x + an]
        i = i0 + paso
        while 0 <= i < len(fotogramas):
            gris = cv2.cvtColor(fotogramas[i], cv2.COLOR_BGR2GRAY)
            x0, y0 = max(0, px - radio), max(0, py - radio)
            x1, y1 = min(ancho, px + an + radio), min(alto, py + al + radio)
            res = cv2.matchTemplate(gris[y0:y1, x0:x1], plantilla, cv2.TM_CCOEFF_NORMED)
            _, valor, _, (mx, my) = cv2.minMaxLoc(res)
            peor = min(peor, valor)
            if valor >= 0.4:
                px, py = x0 + mx, y0 + my
                plantilla = gris[py:py + al, px:px + an]
            cajas[i] = (px, py)
            i += paso
    return cajas, peor


def difuminar(f, x, y, an, al, margen=0.35):
    alto, ancho = f.shape[:2]
    mx, my = int(an * margen), int(al * margen)
    x0, y0 = max(0, x - mx), max(0, y - my)
    x1, y1 = min(ancho, x + an + mx), min(alto, y + al + my)
    if x1 - x0 < 2 or y1 - y0 < 2:  # la zona ha salido del plano
        return
    zona = f[y0:y1, x0:x1]
    # pixelado y desenfoque: ilegible incluso al ampliar la captura
    peq = cv2.resize(zona, (max(1, (x1 - x0) // 10), max(1, (y1 - y0) // 10)), interpolation=cv2.INTER_AREA)
    zona = cv2.resize(peq, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    k = max(3, (min(x1 - x0, y1 - y0) // 2) | 1)
    f[y0:y1, x0:x1] = cv2.GaussianBlur(zona, (k, k), 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--zona", action="append", required=True, help="T,X,Y,ANCHO,ALTO[,DESDE,HASTA]")
    ap.add_argument("--fija", action="store_true")
    ap.add_argument("--radio", type=int, default=60)
    a = ap.parse_args()

    fotogramas, fps = leer_fotogramas(a.entrada)
    if not fotogramas:
        sys.exit("El vídeo no tiene fotogramas")
    alto, ancho = fotogramas[0].shape[:2]

    pistas = []
    for z in a.zona:
        zona, _, ancla = z.partition("/")
        v = [float(n) for n in zona.split(",")]
        if len(v) not in (5, 7):
            sys.exit(f"Zona mal escrita: {z}")
        t, x, y, an, al = v[0], int(v[1]), int(v[2]), int(v[3]), int(v[4])
        desde, hasta = (round(v[5] * fps), round(v[6] * fps)) if len(v) == 7 else (0, len(fotogramas) - 1)
        i0 = min(len(fotogramas) - 1, round(t * fps))
        if a.fija:
            cajas = [(x, y)] * len(fotogramas)
            print(f"Zona {z}: fija")
        else:
            seguida = tuple(int(n) for n in ancla.split(",")) if ancla else (x, y, an, al)
            # solo se sigue dentro del intervalo, para que lo que pase fuera no lo arrastre
            tramo, peor = seguir(fotogramas[desde:hasta + 1], i0 - desde, seguida, a.radio)
            dx, dy = x - seguida[0], y - seguida[1]
            cajas = [None] * len(fotogramas)
            cajas[desde:hasta + 1] = [(px + dx, py + dy) for px, py in tramo]
            aviso = "  << REVISAR" if peor < 0.5 else ""
            print(f"Zona {z}: peor parecido {peor:.2f}{aviso}")
        pistas.append((cajas, an, al))

    cmd = ["ffmpeg", "-v", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{ancho}x{alto}", "-r", f"{fps}", "-i", "-",
           "-i", a.entrada, "-map", "0:v", "-map", "1:a?",
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "copy", "-shortest", a.salida]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i, f in enumerate(fotogramas):
        for cajas, an, al in pistas:
            if cajas[i] is not None:
                difuminar(f, *cajas[i], an, al)
        proc.stdin.write(np.ascontiguousarray(f).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("FFmpeg ha fallado")
    print(f"Hecho: {a.salida}")


if __name__ == "__main__":
    main()
