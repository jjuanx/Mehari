"""Paso 6. Copia lo bueno (calidad >= 4) a _SELECCION/, ordenado por línea.

- Sin marca antigua -> _SELECCION/fotos/<bodas|coche|detalles|turismo|otros>/ y _SELECCION/videos/…
- Con marca antigua (sí o revisar) -> _SELECCION/para_retoque_marca_antigua/
- Las fotos se convierten a JPG (calidad 92) para que se abran en Windows sin extensiones HEIC.
- Los originales no se tocan. Si se interrumpe, al relanzarlo sigue donde lo dejó.
- Nombre de cada copia: <código>_q<calidad>_<coche>.jpg  (ej. F1259_q5_beige.jpg)

Uso: python 6_seleccion.py "<carpeta de material>" [calidad mínima, por defecto 4]
"""
import csv
import shutil
import sys
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, ImageOps

from comun import carpeta_raiz

CARPETA = {"boda": "bodas", "coche": "coche", "detalle": "detalles", "turismo": "turismo", "otro": "otros"}


def destino(sel: Path, r: dict) -> Path:
    base = sel / f"{r['tipo']}s" / CARPETA[r["linea"]] if r["marca_antigua"] == "no" else sel / "para_retoque_marca_antigua"
    nombre = f"{r['id']}_q{r['calidad']}_{r['coche'].replace(' ', '')}"
    return base / (nombre + (".jpg" if r["tipo"] == "foto" else Path(r["archivo"]).suffix.lower()))


def copiar(trabajo):
    origen, dst, tipo = trabajo
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".tmp")
    if tipo == "foto":
        ImageOps.exif_transpose(Image.open(origen)).convert("RGB").save(tmp, "JPEG", quality=92)
    else:
        shutil.copy2(origen, tmp)
    tmp.replace(dst)


def main():
    raiz = carpeta_raiz()
    minimo = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    sel = raiz / "_SELECCION"
    with open(raiz / "_analisis" / "clasificacion.csv", encoding="utf-8-sig") as fh:
        filas = [r for r in csv.DictReader(fh, delimiter=";") if int(r["calidad"]) >= minimo]
    trabajos = [(raiz / r["archivo"], destino(sel, r), r["tipo"]) for r in filas]
    pendientes = [t for t in trabajos if not t[1].exists()]
    print(f"{len(trabajos)} ficheros con calidad >= {minimo}; faltan {len(pendientes)}")
    with Pool() as pool:
        for n, _ in enumerate(pool.imap_unordered(copiar, pendientes, chunksize=2), 1):
            if n % 100 == 0:
                print(f"  {n}/{len(pendientes)}", flush=True)
    print("Listo:", sel)


if __name__ == "__main__":
    main()
