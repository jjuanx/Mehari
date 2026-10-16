"""Paso 2. Aparta duplicados exactos, casi duplicados, fotos movidas y vídeos de baja resolución.

No borra nada: mueve a _DESCARTADOS/<motivo>/ y deja descartes.csv y restaurar.py para deshacerlo.
Por defecto solo SIMULA y escribe _analisis/plan_descartes.csv. Con --aplicar mueve de verdad.

Fotos movidas: el detector solo propone candidatas (nitidez de la mejor tesela < 600) y escribe
_analisis/candidatas_desenfoque.txt. Muchas son desenfoques buscados (flores en primer plano,
atardeceres), así que se revisan a ojo y se pasan las elegidas en un fichero de texto
(un nombre por línea) con --desenfocadas.

Uso:
  python 2_descartar.py "<carpeta>"                                   # simula
  python 2_descartar.py "<carpeta>" --desenfocadas elegidas.txt --aplicar
"""
import argparse
import collections
import csv
import shutil
from pathlib import Path

import numpy as np

from comun import leer_analisis

# Umbrales calibrados a ojo con el material del cliente (oct. 2026).
PHASH_MAX, DHASH_MAX = 10, 16        # o bien ambos <= 12
LADO_CORTO_MIN_VIDEO = 1080           # por debajo de 1080p no sirve para reels 1080x1920
NITIDEZ_CANDIDATA = 600

RESTAURAR = '''"""Devuelve a la carpeta principal lo que hay en _DESCARTADOS (todo o solo un motivo).
Uso:  python restaurar.py                      -> restaura todo
      python restaurar.py casi_duplicados      -> restaura solo esa subcarpeta"""
import shutil, sys
from pathlib import Path
aqui = Path(__file__).resolve().parent
motivos = sys.argv[1:] or [d.name for d in aqui.iterdir() if d.is_dir()]
n = 0
for m in motivos:
    for f in (aqui / m).iterdir():
        if f.is_file() and not (aqui.parent / f.name).exists():
            shutil.move(str(f), str(aqui.parent / f.name)); n += 1
print(f"Restaurados {n} archivos")
'''


def bits(hexes):
    """Hashes hexadecimales de 64 bits -> matriz booleana (n, 64)."""
    return np.array([[c == "1" for c in bin(int(h, 16))[2:].zfill(64)] for h in hexes], dtype=bool)


def distancias(m):
    n = len(m)
    d = np.zeros((n, n), dtype=np.uint8)
    for i in range(0, n, 256):  # por bloques para no agotar la memoria
        d[i:i + 256] = (m[i:i + 256, None, :] != m[None, :, :]).sum(-1)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("--desenfocadas", help="fichero de texto con las fotos movidas confirmadas a ojo")
    ap.add_argument("--aplicar", action="store_true", help="mover de verdad (si no, solo simula)")
    a = ap.parse_args()
    raiz = Path(a.carpeta).expanduser().resolve()
    datos = leer_analisis(raiz)
    presentes = {f.name for f in raiz.iterdir() if f.is_file()}
    fotos = [r for r in datos.values() if r["kind"] == "img" and "error" not in r and r["file"] in presentes]
    videos = [r for r in datos.values() if r["kind"] == "vid" and "error" not in r and r["file"] in presentes]
    plan = []  # (archivo, motivo, detalle)

    # 1) Duplicados exactos (mismo SHA-256): se conserva el primero por nombre.
    por_hash = collections.defaultdict(list)
    for r in fotos + videos:
        if "sha" in r:
            por_hash[r["sha"]].append(r["file"])
    exactos = set()
    for grupo in por_hash.values():
        grupo.sort(key=lambda f: (len(f), f))  # se conserva el nombre más corto (sin " copy", " 2"…)
        for f in grupo[1:]:
            plan.append((f, "duplicados_exactos", f"igual que {grupo[0]}"))
            exactos.add(f)

    # 2) Fotos movidas confirmadas a ojo.
    candidatas = sorted((r for r in fotos if r["sharp_max"] < NITIDEZ_CANDIDATA), key=lambda r: r["sharp_max"])
    (raiz / "_analisis" / "candidatas_desenfoque.txt").write_text(
        "\n".join(f"{r['file']}\t{r['sharp_max']:.0f}" for r in candidatas), encoding="utf-8")
    movidas = set()
    if a.desenfocadas:
        movidas = {l.strip().split("\t")[0] for l in Path(a.desenfocadas).read_text(encoding="utf-8").splitlines() if l.strip()}
        for f in sorted(movidas & presentes):
            plan.append((f, "fotos_movidas_o_desenfocadas", ""))

    # 3) Casi duplicados: en cada grupo se queda la de más resolución y, a igualdad, la más nítida.
    resto = [r for r in fotos if r["file"] not in exactos | movidas]
    if resto:
        pa, pb = distancias(bits([r["phash"] for r in resto])), distancias(bits([r["dhash"] for r in resto]))
        orden = sorted(range(len(resto)), key=lambda i: (round(np.log2(resto[i]["w"] * resto[i]["h"]) * 2), resto[i]["sharp_max"]), reverse=True)
        asignadas = set()
        for i in orden:
            if i in asignadas:
                continue
            asignadas.add(i)
            for j in orden:
                if j not in asignadas and ((pa[i, j] <= PHASH_MAX and pb[i, j] <= DHASH_MAX) or (pa[i, j] <= 12 and pb[i, j] <= 12)):
                    asignadas.add(j)
                    plan.append((resto[j]["file"], "casi_duplicados", f"se conserva {resto[i]['file']} (pHash {pa[i, j]}, dHash {pb[i, j]})"))

    # 4) Vídeos de baja resolución (no se tocan los de Live Photo).
    for v in videos:
        if not v.get("livephoto") and min(v["w"], v["h"]) < LADO_CORTO_MIN_VIDEO and v["file"] not in exactos:
            plan.append((v["file"], "videos_baja_resolucion", f"{v['w']}x{v['h']}, {v['dur']:.1f}s"))

    # 5) El vídeo de un Live Photo acompaña a su foto.
    motivo_foto = {Path(f).stem: m for f, m, _ in plan if Path(f).suffix.lower() not in {".mov", ".mp4"}}
    for v in videos:
        if v.get("livephoto") and Path(v["file"]).stem in motivo_foto:
            plan.append((v["file"], motivo_foto[Path(v["file"]).stem], "vídeo Live Photo de la foto descartada"))

    with open(raiz / "_analisis" / "plan_descartes.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["archivo", "motivo", "detalle"])
        w.writerows(plan)
    print(collections.Counter(m for _, m, _ in plan))
    print(f"Candidatas a desenfoque para revisar a ojo: {len(candidatas)} (_analisis/candidatas_desenfoque.txt)")
    if not a.aplicar:
        print("Simulación: no se ha movido nada. Revisa _analisis/plan_descartes.csv y repite con --aplicar.")
        return

    destino = raiz / "_DESCARTADOS"
    destino.mkdir(exist_ok=True)
    nuevo = not (destino / "descartes.csv").exists()
    with open(destino / "descartes.csv", "a", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        if nuevo:
            w.writerow(["archivo", "motivo", "detalle"])
        for f, m, det in plan:
            (destino / m).mkdir(exist_ok=True)
            if (raiz / f).exists() and not (destino / m / f).exists():
                shutil.move(str(raiz / f), str(destino / m / f))
                w.writerow([f, m, det])
    (destino / "restaurar.py").write_text(RESTAURAR, encoding="utf-8")
    print(f"Movidos {len(plan)} ficheros a {destino}")


if __name__ == "__main__":
    main()
