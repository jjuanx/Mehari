"""Produce los ficheros finales de una pieza a partir del material ya preparado.

Uso:
    python3 herramientas/piezas/producir.py <pieza.json> <proyecto> <salida>

Carrusel (`deslizar`) e historia en foto (`historia` / `foto-frase`): se copia la plantilla
`marca/plantillas/estaticas/` sobre <proyecto> (sin borrar assets/material ni revision), se
escribe datos.json (y se incrusta en el index.html copiado, porque con file:// no se puede
leer por fetch) y Chromium exporta cada diapositiva a JPEG con exportar.mjs.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pieza  # noqa: E402
import rutas  # noqa: E402

PLANTILLA_ESTATICAS = rutas.PLANTILLAS / "estaticas"
EXPORTAR = Path(__file__).resolve().parent / "exportar.mjs"
MARCADOR_DATOS = '<script type="application/json" id="datos"></script>'
TAMANOS = {"deslizar": (1080, 1440), "historia": (1080, 1920)}


def _diapositivas(p: dict) -> list[dict]:
    elementos = sorted(p["elementos"], key=lambda e: e["orden"])
    hojas = []
    for i, el in enumerate(elementos):
        if p["formato"] == "historia":
            tipo = "historia"
        else:
            tipo = "portada" if i == 0 else "paso"
        hojas.append({"foto": f"assets/material/{int(el['orden']):02d}.jpg",
                      "rotulo": el.get("rotulo"), "tipo": tipo})
    if p["formato"] == "deslizar":
        hojas.append({"foto": None, "rotulo": None, "tipo": "cierre"})
    return hojas


def estaticas(p: dict, proyecto: Path, salida: Path) -> list[Path]:
    """Carrusel o historia en foto → JPEG en `salida`; devuelve los ficheros por orden."""
    proyecto, salida = Path(proyecto), Path(salida)
    ancho, alto = TAMANOS[p["formato"]]
    hojas = _diapositivas(p)
    datos = {"formato": p["formato"], "variante": p["variante"],
             "ancho": ancho, "alto": alto, "diapositivas": hojas}

    shutil.copytree(PLANTILLA_ESTATICAS, proyecto, dirs_exist_ok=True)
    texto = json.dumps(datos, ensure_ascii=False)
    (proyecto / "datos.json").write_text(texto, encoding="utf-8")
    # «</» dentro de un <script> cerraría el bloque; «<\/» es JSON válido y equivale
    incrustado = texto.replace("</", "<\\/")
    index = proyecto / "index.html"
    html = index.read_text(encoding="utf-8")
    index.write_text(html.replace(MARCADOR_DATOS, MARCADOR_DATOS.replace("></", f">{incrustado}</")),
                     encoding="utf-8")

    salida.mkdir(parents=True, exist_ok=True)
    if p["formato"] == "historia":
        prefijo = "historia-"
        nombres = ([f"historia-{i:02d}.jpg" for i in range(1, len(hojas) + 1)] if len(hojas) > 1
                   else ["historia.jpg"])
    else:
        prefijo = ""
        nombres = [f"{i:02d}.jpg" for i in range(1, len(hojas) + 1)]
    for viejo in nombres:
        (salida / viejo).unlink(missing_ok=True)
    cmd = ["node", str(EXPORTAR), str(proyecto.resolve()), str(len(hojas)), str(ancho), str(alto),
           str(salida.resolve()), prefijo]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=EXPORTAR.parent)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"exportar.mjs ha fallado (código {e.returncode}): "
                           f"{(e.stderr or '').strip()} {(e.stdout or '').strip()}".strip()) from e
    if len(hojas) == 1 and p["formato"] == "historia":
        (salida / "historia-01.jpg").rename(salida / "historia.jpg")
    return [salida / n for n in nombres]


def producir(ruta_pieza: Path, proyecto: Path, salida: Path) -> list[Path]:
    """Elige la producción según el formato y la variante."""
    p = pieza.cargar_pieza(Path(ruta_pieza))
    if p["formato"] == "reel" or (p["formato"] == "historia" and p["variante"] == "clip-cta"):
        raise NotImplementedError("reel e historia en clip: tarea 8")
    return estaticas(p, Path(proyecto), Path(salida))


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("Uso: python3 herramientas/piezas/producir.py <pieza.json> <proyecto> <salida>")
    for f in producir(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])):
        print(f)


if __name__ == "__main__":
    main()
