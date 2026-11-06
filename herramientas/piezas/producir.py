"""Produce los ficheros finales de una pieza a partir del material ya preparado.

Uso:
    python3 herramientas/piezas/producir.py <pieza.json> <proyecto> <salida>

Carrusel (`deslizar`) e historia en foto (`historia` / `foto-frase`): se copia la plantilla
`marca/plantillas/estaticas/` sobre <proyecto> (sin borrar assets/material ni revision), se
escribe datos.json (y se incrusta en el index.html copiado, porque con file:// no se puede
leer por fetch) y Chromium exporta cada diapositiva a JPEG con exportar.mjs.

Reel e historia en clip (`historia` / `clip-cta`): se copia la plantilla `marca/plantillas/reel/`
(HyperFrames) sobre <proyecto>, se rellenan sus marcadores con generar_html, se comprueba con
`hyperframes check` y se renderiza a MP4 (1080×1920, 30 fps). El reel saca además portada.jpg.
"""
import html as html_mod
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pieza  # noqa: E402
import rutas  # noqa: E402

sys.path.insert(0, str(rutas.MATERIAL))
from comun import EXT_VIDEO  # noqa: E402

PLANTILLA_ESTATICAS = rutas.PLANTILLAS / "estaticas"
PLANTILLA_REEL = rutas.PLANTILLAS / "reel"
HYPERFRAMES = ["--yes", "hyperframes@0.8.174"]  # se lanza con el npx que encuentre _npx()
DURACION_TRANSICION = 0.866  # marca/animaciones/renders/transicion.webm
TRANSICION_TAPA = 0.41       # a los 0,41 s la transición tapa la pantalla: ahí va el corte
ROTULO_HISTORIA = "¿Cuándo os casáis?"
FUNDIDO_ROTULO = 0.25
FUNDIDO_MUSICA = 1.0
ESCALA_CLIP, ESCALA_FOTO = 1.05, 1.06
SEGUNDO_PORTADA = 1.0
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


def _exigir_preparado(p: dict, proyecto: Path) -> None:
    errores = pieza.errores_preparado(p, proyecto)
    if errores:
        raise RuntimeError("No se produce la pieza: " + "; ".join(errores))


def estaticas(p: dict, proyecto: Path, salida: Path) -> list[Path]:
    """Carrusel o historia en foto → JPEG en `salida`; devuelve los ficheros por orden."""
    proyecto, salida = Path(proyecto), Path(salida)
    _exigir_preparado(p, proyecto)
    ancho, alto = TAMANOS[p["formato"]]
    hojas = _diapositivas(p)
    datos = {"formato": p["formato"], "variante": p["variante"],
             "ancho": ancho, "alto": alto, "diapositivas": hojas}

    shutil.copytree(PLANTILLA_ESTATICAS, proyecto, dirs_exist_ok=True)
    texto = json.dumps(datos, ensure_ascii=False)
    (proyecto / "datos.json").write_text(texto, encoding="utf-8")
    # Cualquier «<» (</script>, <!--, <script) puede alterar el tokenizador de HTML dentro
    # de un <script>; «\u003c» es JSON válido y equivale
    incrustado = texto.replace("<", "\\u003c")
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
    # Borra salidas antiguas con el mismo patrón de nombres (una pasada previa con más diapositivas)
    patron = "historia*.jpg" if p["formato"] == "historia" else "[0-9][0-9].jpg"
    for viejo in salida.glob(patron):
        viejo.unlink()
    cmd = ["node", str(EXPORTAR), str(proyecto.resolve()), str(len(hojas)), str(ancho), str(alto),
           str(salida.resolve()), prefijo]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=EXPORTAR.parent)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"exportar.mjs ha fallado (código {e.returncode}): "
                           f"{(e.stderr or '').strip()} {(e.stdout or '').strip()}".strip()) from e
    if len(hojas) == 1 and p["formato"] == "historia":
        (salida / "historia-01.jpg").rename(salida / "historia.jpg")
    return [salida / n for n in nombres]


# ---------------------------------------------------------------- reel e historia en clip

def _s(x: float) -> str:
    """Segundos para los atributos y el JS: 12 → «12», 0.41 → «0.41»."""
    return f"{round(float(x), 3):g}"


def _musica(p: dict) -> Path | None:
    m = p.get("musica")
    return Path(m["ruta"]) if isinstance(m, dict) and m.get("ruta") else None


def generar_html(p: dict, duraciones: list[float]) -> str:
    """index.html de la plantilla del reel con los planos, rótulos y animaciones de la pieza.

    `duraciones` va en el mismo orden que p["elementos"]; los planos se colocan por `orden`.
    """
    es_reel = p["formato"] == "reel"
    titular = es_reel and p["variante"] == "titular"
    pares = sorted(zip(p["elementos"], duraciones), key=lambda par: par[0]["orden"])
    planos, rotulos, animacion, transiciones = [], [], [], []
    t = 0.0
    for i, (el, d) in enumerate(pares):
        n, d = int(el["orden"]), float(d)
        tiempos = f'data-start="{_s(t)}" data-duration="{_s(d)}"'
        if Path(el["fichero"]).suffix.lower() in EXT_VIDEO:
            planos.append(f'<video id="p{n}" class="clip plano" src="assets/material/{n:02d}.mp4" {tiempos} '
                          f'data-media-start="0" data-track-index="0" playsinline muted></video>')
            escala = ESCALA_CLIP
        else:
            planos.append(f'<img id="p{n}" class="clip plano" src="assets/material/{n:02d}.jpg" {tiempos} '
                          f'data-track-index="0" alt="">')
            escala = ESCALA_FOTO
        animacion.append(f'tl.fromTo("#p{n}", {{ scale: 1 }}, {{ scale: {escala:g}, duration: {_s(d)}, '
                         f'ease: "none" }}, {_s(t)});')

        texto = el.get("rotulo") or (None if es_reel else ROTULO_HISTORIA)
        if texto:
            grande = titular and el.get("tramo") == "gancho"
            clase = "clip rotulo rotulo-titular" if grande else "clip rotulo"
            rotulos.append(f'<div id="r{n}" class="{clase}" {tiempos} data-track-index="1">'
                           f'{html_mod.escape(texto)}</div>')
            ids = [f"#r{n}"]
            fundido = min(FUNDIDO_ROTULO, d / 4)
            fin = max(t + fundido, t + d - fundido - 0.04)  # se va antes del final del plano
            animacion.append(f'tl.fromTo("#r{n}", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, '
                             f'duration: {_s(fundido)}, ease: "expo.out" }}, {_s(t)});')
            if grande:
                rotulos.append(f'<div id="v{n}" class="clip velo" {tiempos} data-track-index="3"></div>')
                ids.append(f"#v{n}")
                animacion.append(f'tl.fromTo("#v{n}", {{ opacity: 0 }}, {{ opacity: 1, '
                                 f'duration: {_s(fundido)}, ease: "sine.out" }}, {_s(t)});')
            animacion.append(f'tl.to({json.dumps(ids)}, {{ opacity: 0, duration: {_s(fundido)}, ease: "sine.in" }}, '
                             f'{_s(fin)});')
        t += d
        siguiente = pares[i + 1][0].get("tramo") if i + 1 < len(pares) else None
        if es_reel and el.get("tramo") == "momento" and siguiente != "momento":
            transiciones.append(max(0.0, t - TRANSICION_TAPA))

    if es_reel:
        planos.append(f'<video id="cierre" class="clip plano" src="assets/cierre.mp4" data-start="{_s(t)}" '
                      f'data-duration="{_s(pieza.CIERRE_REEL)}" data-media-start="0" data-track-index="0" '
                      f'playsinline muted></video>')
        t += pieza.CIERRE_REEL
    for k, inicio in enumerate(transiciones, 1):
        planos.append(f'<video id="t{k}" class="clip transicion" src="assets/transicion.webm" '
                      f'data-start="{_s(inicio)}" data-duration="{_s(DURACION_TRANSICION)}" '
                      f'data-media-start="0" data-track-index="4" playsinline muted></video>')
    musica = _musica(p)
    if musica is not None:
        puntos = [{"t": 0, "v": 1}, {"t": round(max(0.0, t - FUNDIDO_MUSICA), 3), "v": 1},
                  {"t": round(t, 3), "v": 0}]
        automatizacion = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": puntos}]})
        planos.append(f'<audio id="musica" src="assets/musica{musica.suffix.lower()}" data-start="0" '
                      f'data-duration="{_s(t)}" data-track-index="2" data-volume="1" '
                      f"data-automation='{automatizacion}'></audio>")

    sangria = "\n      "
    html = (PLANTILLA_REEL / "index.html").read_text(encoding="utf-8")
    html = html.replace('data-duration="__DURACION__"', f'data-duration="{_s(t)}"')
    html = html.replace("<!--PLANOS-->", "      " + sangria.join(planos))
    html = html.replace("<!--ROTULOS-->", "      " + sangria.join(rotulos))
    return html.replace("/*ANIMACION*/", "      " + sangria.join(animacion))


def _npx() -> str:
    """Ruta de npx. En Windows es npx.cmd, que subprocess no encuentra con el nombre solo."""
    ruta = shutil.which("npx")
    if ruta is None:
        raise RuntimeError("No encuentro npx: instala Node.js (que trae npx) y comprueba que está "
                           "en el PATH abriendo una terminal nueva y escribiendo «npx --version».")
    return ruta


def _hyperframes(args: list[str], proyecto: Path) -> None:
    try:
        subprocess.run([_npx(), *HYPERFRAMES, *args], check=True, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=proyecto)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"hyperframes {args[0]} ha fallado (código {e.returncode}): "
                           f"{(e.stdout or '').strip()} {(e.stderr or '').strip()}".strip()) from e


def video(p: dict, proyecto: Path, salida: Path) -> list[Path]:
    """Reel (reel.mp4 + portada.jpg) o historia en clip (historia.mp4 o historia-NN.mp4)."""
    proyecto, salida = Path(proyecto).resolve(), Path(salida).resolve()
    _exigir_preparado(p, proyecto)
    shutil.copytree(PLANTILLA_REEL, proyecto, dirs_exist_ok=True)
    for vieja in (proyecto / "assets").glob("musica.*"):
        vieja.unlink()
    musica = _musica(p)
    if musica is not None:
        shutil.copy(musica, proyecto / "assets" / f"musica{musica.suffix.lower()}")

    salida.mkdir(parents=True, exist_ok=True)
    if p["formato"] == "reel":
        tandas = [(p, "reel.mp4")]
        patrones = ("reel.mp4", "portada.jpg")
    else:  # historia clip-cta: una composición por elemento
        elementos = sorted(p["elementos"], key=lambda e: e["orden"])
        nombres = (["historia.mp4"] if len(elementos) == 1
                   else [f"historia-{i:02d}.mp4" for i in range(1, len(elementos) + 1)])
        tandas = [(p | {"elementos": [el]}, nombre) for el, nombre in zip(elementos, nombres)]
        patrones = ("historia*.mp4",)
    # Borra salidas antiguas con el mismo patrón de nombres (una pasada previa con más elementos)
    for patron in patrones:
        for viejo in salida.glob(patron):
            viejo.unlink()

    producidos = []
    for sub, nombre in tandas:
        duraciones = [pieza.duracion_elemento(e) for e in sub["elementos"]]
        (proyecto / "index.html").write_text(generar_html(sub, duraciones), encoding="utf-8")
        _hyperframes(["check"], proyecto)
        destino = salida / nombre
        _hyperframes(["render", "--output", str(destino)], proyecto)
        producidos.append(destino)
    if p["formato"] == "reel":
        portada = salida / "portada.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{SEGUNDO_PORTADA:g}",
                        "-i", str(producidos[0]), "-frames:v", "1", "-vf", "scale=1080:1920",
                        "-q:v", "2", str(portada)], check=True, capture_output=True)
        producidos.append(portada)
    return producidos


def producir(ruta_pieza: Path, proyecto: Path, salida: Path) -> list[Path]:
    """Elige la producción según el formato y la variante."""
    p = pieza.cargar_pieza(Path(ruta_pieza))
    if p["formato"] == "reel" or (p["formato"] == "historia" and p["variante"] == "clip-cta"):
        return video(p, Path(proyecto), Path(salida))
    return estaticas(p, Path(proyecto), Path(salida))


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit("Uso: python3 herramientas/piezas/producir.py <pieza.json> <proyecto> <salida>")
    for f in producir(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])):
        print(f)


if __name__ == "__main__":
    main()
