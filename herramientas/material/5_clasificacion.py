"""Paso 5. Une las notas de clasificación en _analisis/clasificacion.csv.

Claude (o una persona) revisa las hojas de contacto y escribe una línea por fichero en
_analisis/clasificacion_fotos.txt y _analisis/clasificacion_videos.txt con este formato:

    <código>|<línea>|<coche>|<marca antigua>|<calidad>|<nota>
    0042|B|N|N|4|novios saliendo de la iglesia            (fotos: código sin la F)
    V007|C|E|S|2|funda MEHARI TOUR SUR visible            (vídeos: código completo)

  línea:          B boda · T turismo · C coche · D detalle · O otro
  coche:          N naranja · E beige · A ambos · - sin coche
  marca antigua:  N no · S sí · R revisar
  calidad:        1 a 5 (5 = portada)

El CSV usa ";" como separador y UTF-8 con BOM para que Excel en español lo abra bien.

Uso: python 5_clasificacion.py "<carpeta de material>"
"""
import csv
import json
import sys

from comun import carpeta_raiz, leer_analisis

LINEA = {"B": "boda", "T": "turismo", "C": "coche", "D": "detalle", "O": "otro"}
COCHE = {"N": "naranja", "E": "beige", "A": "ambos", "-": "sin coche"}
MARCA = {"N": "no", "S": "si", "R": "revisar"}


def main():
    raiz = carpeta_raiz()
    a = raiz / "_analisis"
    datos = leer_analisis(raiz)
    filas = []
    for fichero, prefijo, ids_json, tipo in (("clasificacion_fotos.txt", "F", "ids_fotos.json", "foto"),
                                             ("clasificacion_videos.txt", "", "ids_videos.json", "video")):
        ruta = a / fichero
        if not ruta.exists():
            continue
        ids = json.loads((a / ids_json).read_text(encoding="utf-8"))
        for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
            if not linea.strip():
                continue
            p = linea.split("|", 5)
            codigo = prefijo + p[0]
            try:
                archivo = ids[codigo]
                r = datos[archivo]
                filas.append({
                    "id": codigo, "archivo": archivo, "tipo": tipo,
                    "linea": LINEA[p[1]], "coche": COCHE[p[2]], "marca_antigua": MARCA[p[3]],
                    "calidad": int(p[4]), "nota": p[5] if len(p) > 5 else "",
                    "fecha": (r.get("date") or "").replace(":", "-", 2) if tipo == "foto" else "",
                    "ancho": r["w"], "alto": r["h"],
                    "duracion_s": round(r.get("dur", 0), 1) if tipo == "video" else "",
                    "mb": round(r["size"] / 1e6, 1),
                })
            except (KeyError, IndexError, ValueError) as e:
                sys.exit(f"{fichero}, línea {n}: {linea!r} -> {e!r}")
    codigos = [f["id"] for f in filas]
    duplicados = {c for c in codigos if codigos.count(c) > 1}
    if duplicados:
        sys.exit(f"Códigos repetidos: {sorted(duplicados)}")
    with open(a / "clasificacion.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]), delimiter=";")
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} filas en {a / 'clasificacion.csv'}")


if __name__ == "__main__":
    main()
