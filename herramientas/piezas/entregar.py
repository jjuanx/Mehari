"""Entrega de una pieza terminada en Drive: 02_Produccion/<boda>/<pieza>/.

Uso:
    python3 herramientas/piezas/entregar.py <pieza.json> <proyecto> <carpeta salidas> [--produccion <ruta>]

Copia los ficheros de la pieza y deja al lado el estado (texto.txt), el copy listo para pegar,
una página de revisión autónoma (revision.html) y la cola de Metricool. Nunca sobrescribe.
"""
import argparse
import html
import json
import os
import shutil
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from comprobar import ResultadoTexto, comprobar_medios, comprobar_texto  # noqa: E402
from localizar import raiz_drive  # noqa: E402
from pieza import cargar_pieza, id_pieza  # noqa: E402

TIPOS_METRICOOL = {"deslizar": "carrusel", "reel": "reel", "historia": "story"}
NOTA_COLA = ("Pieza suelta de pieza-boda. Pon la fecha y la aprobación del cliente "
             "antes de lanzar programar-metricool.")
EXT_VIDEO = (".mp4",)


def motivos_no_lista(p: dict, r: ResultadoTexto, avisos: Sequence[str] = ()) -> list[str]:
    """Razones por las que la pieza NO se puede publicar todavía (vacío = lista)."""
    motivos = []
    # Sin la clave «hay_caras» se supone que hay caras (por prudencia)
    if p.get("hay_caras", True) and p.get("permiso_caras") != "si":
        motivos.append("falta permiso de caras")
    pendientes = list(r.pendientes) + list(p.get("pendientes", []))
    if pendientes:
        motivos.append("datos pendientes: " + ", ".join(str(x) for x in pendientes))
    for aviso in avisos:
        motivos.append(f"difuminado por revisar: {aviso}")
    return motivos


def modo_metricool(p: dict) -> str:
    if p["formato"] == "deslizar":
        return "automatico"
    if p["formato"] == "reel" and p.get("musica"):
        return "automatico"
    return "aviso"


def generar_cola(p: dict, id_carpeta: str, medios: list[str]) -> dict:
    tipo = TIPOS_METRICOOL[p["formato"]]
    modo = modo_metricool(p)
    portada = "portada.jpg" if p["formato"] == "reel" and "portada.jpg" in medios else None
    if p["formato"] == "reel":
        medios = [m for m in medios if m != "portada.jpg"]
    grupos = [[m] for m in medios] if p["formato"] == "historia" else [medios]
    publicaciones = []
    for i, grupo in enumerate(grupos, 1):
        pub = {
            "id": f"{id_carpeta}-{i:02d}" if len(grupos) > 1 else id_carpeta,
            "fecha": None,
            "red": "instagram",
            "tipo": tipo,
            "modo": modo,
            "ficha": None,
            "medios": list(grupo),
        }
        if p["formato"] == "reel":
            pub["portada"] = portada
        pub.update({
            "texto": p.get("texto", ""),
            "ubicacion": p.get("ubicacion"),
            "a_mano_despues": list(p.get("a_mano_despues", [])),
            "metricool_id": None,
            "estado": "pendiente",
        })
        publicaciones.append(pub)
    return {
        "boda": p["boda"],
        "zona_horaria": "Europe/Madrid",
        "aprobacion": {"estado": "pendiente", "lote_enviado": None, "aprobado_el": None,
                       "aprobado_por": None, "nota": NOTA_COLA},
        "publicaciones": publicaciones,
    }


def generar_texto(p: dict, motivos: list[str]) -> str:
    estado = "Estado: NO PUBLICAR · " + "; ".join(motivos) if motivos else "Estado: LISTA"
    a_mano = p.get("a_mano_despues", [])
    lista = "\n".join(f"- {x}" for x in a_mano) if a_mano else "- nada"
    musica = p.get("musica")
    if musica:
        musica_txt = f"{musica.get('titulo') or musica.get('ruta', '')} (licencia: {musica.get('licencia', '')})"
    else:
        musica_txt = "sin música"
    return (f"{estado}\n\n{p.get('texto', '')}\n\nA mano en la app:\n{lista}\n\n"
            f"Música: {musica_txt}\n")


CSS = """
body{font-family:system-ui,sans-serif;background:#faf8f5;color:#222;max-width:960px;margin:0 auto;padding:16px;line-height:1.45}
h1{font-size:1.4rem}h2{font-size:1.1rem;margin-top:1.8rem;border-bottom:1px solid #ddd;padding-bottom:4px}
.estado{padding:18px;border-radius:8px;font-size:1.3rem;font-weight:700;color:#fff}
.lista{background:#2e7d32}.nopublicar{background:#c62828}
.estado ul{font-size:1rem;font-weight:400;margin:8px 0 0}
.medios{display:flex;flex-wrap:wrap;gap:8px}.medios img,.medios video{max-width:220px;max-height:400px;border:1px solid #ccc;background:#fff}
pre{white-space:pre-wrap;background:#fff;border:1px solid #ddd;padding:12px;border-radius:6px}
.par{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px}.par figure{margin:0}.par img{max-width:420px;width:100%;border:1px solid #ccc}
.aviso{background:#fff3cd;border:1px solid #e0a800;padding:10px;border-radius:6px;margin:8px 0}
.aviso-difuminado{background:#ffe0b2;border:2px solid #e65100;font-weight:700}
"""


def _e(x) -> str:
    return html.escape(str(x), quote=True)


def generar_revision(p: dict, medios: list[str], pares: list[tuple[str, str]],
                     r: ResultadoTexto, motivos: list[str],
                     avisos_difuminado: Sequence[str] = ()) -> str:
    out = ["<!doctype html>", '<html lang="es"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           f"<title>Revisión · {_e(p.get('tema', ''))}</title><style>{CSS}</style></head><body>",
           f"<h1>Revisión de la pieza: {_e(p.get('formato', ''))} · {_e(p.get('tema', ''))}</h1>"]
    if motivos:
        out.append('<div class="estado nopublicar">NO PUBLICAR<ul>'
                   + "".join(f"<li>{_e(m)}</li>" for m in motivos) + "</ul></div>")
    else:
        out.append('<div class="estado lista">LISTA para publicar</div>')
    if avisos_difuminado:
        out.append("<h2>Difuminado por revisar</h2>" + "".join(
            f'<div class="aviso aviso-difuminado">{_e(a)}</div>' for a in avisos_difuminado))

    out.append('<h2>La pieza</h2><div class="medios">')
    for m in medios:
        if m.lower().endswith(EXT_VIDEO):
            out.append(f'<video controls src="{_e(m)}"></video>')
        else:
            out.append(f'<img src="{_e(m)}" alt="{_e(m)}">')
    out.append("</div>")

    out.append(f"<h2>Texto</h2><pre>{_e(p.get('texto', ''))}</pre>")

    out.append("<h2>Antes y después</h2>")
    if not pares:
        out.append("<p>Ningún elemento tiene recorte ni retoque.</p>")
    notas = {f"{int(e['orden']):02d}": e.get("revision_marca")
             for e in p.get("elementos", []) if isinstance(e.get("orden"), int)}
    for antes, despues in pares:
        nn = Path(antes).name.split("_")[0]
        out.append(f'<div class="par"><figure><img src="{_e(antes)}" alt="antes"><figcaption>Antes</figcaption></figure>'
                   f'<figure><img src="{_e(despues)}" alt="después"><figcaption>Después</figcaption></figure></div>')
        if notas.get(nn):
            out.append(f"<p><b>Elemento {_e(nn)}:</b> {_e(notas[nn])}</p>")
    sin_par = [(k, v) for k, v in notas.items() if v and not any(Path(a).name.startswith(k + "_") for a, _ in pares)]
    for k, v in sin_par:
        out.append(f"<p><b>Elemento {_e(k)}:</b> {_e(v)}</p>")

    out.append("<h2>Avisos</h2>")
    out.append("".join(f'<div class="aviso">{_e(a)}</div>' for a in r.avisos) or "<p>Sin avisos.</p>")
    out.append("<h2>Pendientes</h2>")
    pend = list(r.pendientes) + list(p.get("pendientes", []))
    out.append("<ul>" + "".join(f"<li>{_e(x)}</li>" for x in pend) + "</ul>" if pend else "<p>Sin pendientes.</p>")

    out.append("<h2>Antes de publicar, mirad</h2><ul>"
               "<li>Matrículas: ninguna legible, ni de nuestros coches ni de otros.</li>"
               "<li>La funda de rueda de la marca antigua «@MEHARI_TOURSUR» y cualquier pegatina o logo viejo.</li>"
               "<li>Chevrones o logos del fabricante a la vista.</li>"
               "<li>Caras de menores: ninguna reconocible.</li></ul>")
    out.append("</body></html>")
    return "\n".join(out)


def _jpgs_esperados(p: dict) -> list[str] | None:
    """Nombres exactos de los JPEG que debe tener la pieza, o None si no se fijan por nombre."""
    n = len(p["elementos"])
    if p["formato"] == "deslizar":
        return [f"{i:02d}.jpg" for i in range(1, n + 2)]  # + la diapositiva de cierre
    if p["formato"] == "historia" and p["variante"] == "foto-frase":
        return ["historia.jpg"] if n == 1 else [f"historia-{i:02d}.jpg" for i in range(1, n + 1)]
    return None


def _errores_de_conjunto(p: dict, salidas: list[Path]) -> list[str]:
    """Comprueba que las salidas son exactamente las de esta pieza (sin restos ni faltas)."""
    nombres = sorted(s.name for s in salidas)
    esperado = _jpgs_esperados(p)
    if esperado is not None:
        if nombres != sorted(esperado):
            return [f"salidas: se esperaban {', '.join(esperado)} y hay {', '.join(nombres) or 'ninguna'}"]
    elif p["formato"] == "historia":
        if len(nombres) != len(p["elementos"]):
            return [f"salidas: se esperaban {len(p['elementos'])} ficheros y hay {len(nombres)}: {', '.join(nombres)}"]
    elif p["formato"] == "reel":
        videos = [n for n in nombres if n.lower().endswith(".mp4")]
        otros = [n for n in nombres if not n.lower().endswith(".mp4")]
        if len(videos) != 1 or any(o != "portada.jpg" for o in otros):
            return [f"salidas: se esperaba un único .mp4 (y opcionalmente portada.jpg) y hay {', '.join(nombres) or 'ninguna'}"]
    return []


def _leer_avisos(proyecto: Path) -> list[str]:
    ruta = proyecto / "revision" / "avisos.json"
    if not ruta.is_file():
        sys.exit(f"No se entrega la pieza: falta {ruta}. preparar.py siempre lo escribe; "
                 "¿no se ha ejecutado o se ha pasado otro proyecto?")
    try:
        avisos = json.loads(ruta.read_text(encoding="utf-8"))
    except ValueError as e:
        sys.exit(f"No se entrega la pieza: {ruta} no es JSON válido ({e}).")
    if not isinstance(avisos, list) or not all(isinstance(a, str) for a in avisos):
        sys.exit(f"No se entrega la pieza: {ruta} debe ser una lista de textos.")
    return avisos


def _carpeta_libre(base: Path, nombre: str) -> Path:
    destino, n = base / nombre, 1
    while destino.exists():
        n += 1
        destino = base / f"{nombre}-{n}"
    return destino


def entregar(ruta_pieza: Path, salidas: list[Path], proyecto: Path, produccion: Path,
             hoy: date) -> Path:
    p = cargar_pieza(Path(ruta_pieza))
    salidas = [Path(s) for s in salidas]
    proyecto, produccion = Path(proyecto), Path(produccion)

    errores = _errores_de_conjunto(p, salidas)
    errores += comprobar_medios(p["formato"], p["variante"], salidas)
    r = comprobar_texto(p.get("texto", ""))
    errores += r.errores
    if errores:
        sys.exit("No se entrega la pieza:\n" + "\n".join(f"- {e}" for e in errores))

    revision = proyecto / "revision"
    avisos = _leer_avisos(proyecto)
    motivos = motivos_no_lista(p, r, avisos)

    nombre = id_pieza(p, hoy) + ("_PENDIENTE" if motivos else "")
    base = produccion / p["boda"]
    base.mkdir(parents=True, exist_ok=True)
    destino = _carpeta_libre(base, nombre)
    destino.mkdir()

    medios = []
    for s in salidas:
        shutil.copy2(s, destino / s.name)
        medios.append(s.name)

    pares = []
    if revision.is_dir():
        (destino / "revision").mkdir()
        for f in sorted(revision.iterdir()):
            if f.is_file():
                shutil.copy2(f, destino / "revision" / f.name)
        for antes in sorted(revision.glob("*_antes.jpg")):
            despues = antes.with_name(antes.name.replace("_antes.jpg", "_despues.jpg"))
            if despues.is_file():
                pares.append((f"revision/{antes.name}", f"revision/{despues.name}"))

    (destino / "texto.txt").write_text(generar_texto(p, motivos), encoding="utf-8")
    (destino / "revision.html").write_text(
        generar_revision(p, medios, pares, r, motivos, avisos), encoding="utf-8")
    cola = generar_cola(p, destino.name, medios)
    (destino / "cola-metricool.json").write_text(
        json.dumps(cola, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(ruta_pieza, destino / "pieza.json")
    return destino


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Entrega una pieza en 02_Produccion de Drive.")
    ap.add_argument("pieza")
    ap.add_argument("proyecto")
    ap.add_argument("salidas", help="carpeta con los ficheros producidos")
    ap.add_argument("--produccion", help="carpeta 02_Produccion (si no, se busca en Drive)")
    a = ap.parse_args(argv)
    if a.produccion:
        produccion = Path(a.produccion)
    else:
        raiz = raiz_drive(os.environ, Path.home())
        if raiz is None:
            sys.exit("No encuentro la carpeta «Mehari We» de Drive. Pasa --produccion <ruta> "
                     "o define la variable MEHARI_DRIVE con la ruta de «Mehari We».")
        produccion = raiz / "02_Produccion"
    carpeta = Path(a.salidas)
    ficheros = sorted(f for f in carpeta.iterdir()
                      if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".mp4"))
    print(entregar(Path(a.pieza), ficheros, Path(a.proyecto), produccion, date.today()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
