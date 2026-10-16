"""Paso 3. Aparta en _livephotos/ los clips de 2-3 s que el iPhone graba con cada Live Photo.

Un vídeo cuenta como Live Photo si hay una foto con el mismo nombre (IMG_0001.HEIC + IMG_0001.MOV).
Sirven como recurso para reels, pero no hay que revisarlos uno a uno.

Uso: python 3_livephotos.py "<carpeta de material>"
"""
import shutil
from pathlib import Path

from comun import EXT_FOTO, EXT_VIDEO, carpeta_raiz, ficheros_sueltos


def main():
    raiz = carpeta_raiz()
    tallos = {Path(f).stem for f in ficheros_sueltos(raiz, EXT_FOTO)}
    destino = raiz / "_livephotos"
    destino.mkdir(exist_ok=True)
    n = 0
    for v in ficheros_sueltos(raiz, EXT_VIDEO):
        if Path(v).stem in tallos and not (destino / v).exists():
            shutil.move(str(raiz / v), str(destino / v))
            n += 1
    print(f"Movidos {n} vídeos de Live Photo a {destino}")


if __name__ == "__main__":
    main()
