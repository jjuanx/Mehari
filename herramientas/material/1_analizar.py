"""Paso 1. Analiza todas las fotos y vídeos de la carpeta SIN modificar nada.

Escribe _analisis/analisis.jsonl (una línea por fichero) y _analisis/thumbs/ (miniaturas de 400 px).
Por foto: resolución, fecha EXIF, nitidez (varianza del laplaciano global y de la mejor tesela 4x4),
brillo, pHash y dHash. Por vídeo: resolución y duración (ffprobe), y si es el vídeo de un Live Photo.
Si se interrumpe, al relanzarlo continúa donde lo dejó.

Uso: python 1_analizar.py "<carpeta de material>"
"""
import collections
import hashlib
import json
from multiprocessing import Pool
from pathlib import Path

import cv2
import imagehash
import numpy as np
from PIL import Image, ImageOps

from comun import EXT_FOTO, EXT_VIDEO, carpeta_analisis, carpeta_raiz, ffprobe, ficheros_sueltos, nombre_miniatura

RAIZ = None


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 22), b""):
            h.update(bloque)
    return h.hexdigest()


def nitidez(gris):
    lap = cv2.Laplacian(gris, cv2.CV_64F)
    alto, ancho = gris.shape
    teselas = sorted(
        float(lap[i * alto // 4:(i + 1) * alto // 4, j * ancho // 4:(j + 1) * ancho // 4].var())
        for i in range(4) for j in range(4)
    )
    # La mejor tesela evita marcar como movidas las fotos con fondo desenfocado a propósito.
    return float(lap.var()), teselas[-1], teselas[-2]


def analizar_foto(args):
    raiz, nombre = args
    r = {"file": nombre, "kind": "img"}
    try:
        im = Image.open(raiz / nombre)
        exif = im.getexif()
        r["date"] = exif.get_ifd(0x8769).get(36867) or exif.get(306)
        im = ImageOps.exif_transpose(im).convert("RGB")
        r["w"], r["h"] = im.size
        peq = im.copy()
        peq.thumbnail((1024, 1024))
        gris = cv2.cvtColor(np.asarray(peq), cv2.COLOR_RGB2GRAY)
        r["sharp_g"], r["sharp_max"], r["sharp_2"] = nitidez(gris)
        r["bright"] = float(gris.mean())
        r["phash"], r["dhash"] = str(imagehash.phash(peq)), str(imagehash.dhash(peq))
        mini = peq.copy()
        mini.thumbnail((400, 400))
        mini.save(raiz / "_analisis" / "thumbs" / nombre_miniatura(nombre), quality=80)
    except Exception as e:  # noqa: BLE001 - se registra y se sigue con el resto
        r["error"] = repr(e)
    return r


def main():
    raiz = carpeta_raiz()
    analisis = carpeta_analisis(raiz)
    (analisis / "thumbs").mkdir(exist_ok=True)
    fotos = ficheros_sueltos(raiz, EXT_FOTO)
    videos = ficheros_sueltos(raiz, EXT_VIDEO)
    tamanos = {f: (raiz / f).stat().st_size for f in fotos + videos}
    repetidos = collections.Counter(tamanos.values())  # solo se calcula SHA-256 si coincide el tamaño
    tallos_foto = {Path(f).stem for f in fotos}

    jsonl = analisis / "analisis.jsonl"
    hechos = set()
    if jsonl.exists():
        for linea in jsonl.read_text(encoding="utf-8").splitlines():
            try:
                hechos.add(json.loads(linea)["file"])
            except (json.JSONDecodeError, KeyError):
                pass
    pendientes_f = [f for f in fotos if f not in hechos]
    pendientes_v = [v for v in videos if v not in hechos]
    print(f"Fotos: {len(fotos)} ({len(pendientes_f)} pendientes) · Vídeos: {len(videos)} ({len(pendientes_v)} pendientes)")

    with open(jsonl, "a", encoding="utf-8") as out:
        with Pool() as pool:
            for n, r in enumerate(pool.imap_unordered(analizar_foto, [(raiz, f) for f in pendientes_f], chunksize=4), 1):
                r["size"] = tamanos[r["file"]]
                if repetidos[r["size"]] > 1:
                    r["sha"] = sha256(raiz / r["file"])
                out.write(json.dumps(r) + "\n")
                out.flush()
                if n % 100 == 0:
                    print(f"  fotos {n}/{len(pendientes_f)}", flush=True)
        for v in pendientes_v:
            r = {"file": v, "kind": "vid", "size": tamanos[v], "livephoto": Path(v).stem in tallos_foto}
            try:
                r.update(ffprobe(raiz / v))
            except Exception as e:  # noqa: BLE001
                r["error"] = repr(e)
            if repetidos[r["size"]] > 1:
                r["sha"] = sha256(raiz / v)
            out.write(json.dumps(r) + "\n")
            out.flush()
    print("Listo:", jsonl)


if __name__ == "__main__":
    main()
