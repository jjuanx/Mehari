"""Lectura y validación de pieza.json (versión 1)."""
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rutas  # noqa: E402

sys.path.insert(0, str(rutas.MATERIAL))
from comun import EXT_VIDEO  # noqa: E402

FORMATOS = {
    "reel": ("limpio", "titular"),
    "deslizar": ("foto-entera", "con-rotulos"),
    "historia": ("foto-frase", "clip-cta"),
}
TRAMOS = ("gancho", "detalle", "prueba", "momento")
PERMISOS = ("si", "no", "pendiente")
CIERRE_REEL = 4.0
REEL_MIN, REEL_MAX = 15.0, 25.0
HISTORIA_CLIP_MAX = 15.0
RE_BODA = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9-]+$")
RE_TEMA = re.compile(r"^[a-z0-9-]+$")
# Vídeos que el resto de herramientas no sabe preparar: se rechazan en vez de tratarlos como foto
VIDEO_NO_ADMITIDO = {".m4v", ".avi", ".mkv", ".webm", ".mts", ".m2ts", ".3gp", ".wmv", ".mpg", ".mpeg"}
RETOQUES_FOTO = ("placa", "funda", "emblema")
RETOQUES_VIDEO = ("zona",)


class PiezaInvalida(Exception):
    def __init__(self, errores: list[str]):
        self.errores = errores
        super().__init__("pieza.json no es válido: " + "; ".join(errores))


def _es_numero(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def duracion_elemento(el: dict) -> float:
    """Segundos que dura un elemento: hasta - desde (clip) o duracion (foto)."""
    if "desde" in el and "hasta" in el:
        return float(el["hasta"]) - float(el["desde"])
    return float(el["duracion"])


def duracion_total(p: dict) -> float:
    """Duración del reel: suma de elementos más el cierre de marca."""
    return sum(duracion_elemento(e) for e in p["elementos"]) + CIERRE_REEL


def id_pieza(p: dict, hoy: date) -> str:
    return f"{hoy.isoformat()}_{p['formato']}_{p['tema']}"


def _duracion_valida(el: dict, i: int, errores: list[str]) -> float | None:
    """Devuelve la duración del elemento, o None si sus campos son inválidos."""
    if "desde" in el or "hasta" in el:
        d, h = el.get("desde"), el.get("hasta")
        if not (_es_numero(d) and _es_numero(h)) or d < 0 or h <= d:
            errores.append(f"elementos[{i}]: 'desde' y 'hasta' deben ser números con 0 <= desde < hasta")
            return None
        return float(h) - float(d)
    d = el.get("duracion")
    if not _es_numero(d) or d <= 0:
        errores.append(f"elementos[{i}]: falta 'desde'/'hasta' (clip) o 'duracion' (foto) positiva")
        return None
    return float(d)


def es_video(fichero: str) -> bool:
    return Path(fichero).suffix.lower() in EXT_VIDEO


def _caja_valida(caja) -> bool:
    """[x, y, ancho, alto] con cuatro números y ancho y alto positivos."""
    return (isinstance(caja, list) and len(caja) == 4 and all(_es_numero(v) for v in caja)
            and caja[2] > 0 and caja[3] > 0)


def _poligono_valido(poligono) -> bool:
    """Al menos 4 vértices [x, y] numéricos."""
    return (isinstance(poligono, list) and len(poligono) >= 4
            and all(isinstance(v, list) and len(v) == 2 and all(_es_numero(c) for c in v)
                    for v in poligono))


def _validar_retoques(el: dict, i: int, errores: list[str]) -> None:
    """Retoques de foto (placa, funda, emblema) o de vídeo (zona), según el fichero."""
    if "retoques" not in el:
        return
    retoques = el["retoques"]
    if not isinstance(retoques, list):
        errores.append(f"elementos[{i}]: 'retoques' debe ser una lista")
        return
    video = es_video(el["fichero"])
    admitidos = RETOQUES_VIDEO if video else RETOQUES_FOTO
    clase = "vídeo" if video else "foto"
    for j, r in enumerate(retoques):
        donde = f"elementos[{i}].retoques[{j}]"
        if not isinstance(r, dict):
            errores.append(f"{donde}: cada retoque debe ser un objeto")
            continue
        tipo = r.get("tipo")
        if tipo not in admitidos:
            errores.append(f"{donde}: tipo {tipo!r} no vale en un {clase} ({el['fichero']}); "
                           f"en un {clase} el tipo debe ser {' o '.join(admitidos)}")
        elif tipo in ("placa", "funda"):
            if not _poligono_valido(r.get("poligono")):
                errores.append(f"{donde}: {tipo} necesita 'poligono' con al menos 4 puntos [x, y] numéricos")
        elif tipo == "emblema":
            if not _caja_valida(r.get("caja")):
                errores.append(f"{donde}: emblema necesita 'caja' [x, y, ancho, alto] con ancho y alto > 0")
        else:  # zona
            if not _es_numero(r.get("t")):
                errores.append(f"{donde}: zona necesita 't' numérico (segundo del clip original)")
            if not _caja_valida(r.get("caja")):
                errores.append(f"{donde}: zona necesita 'caja' [x, y, ancho, alto] con ancho y alto > 0")
            for clave in ("desde", "hasta"):
                if clave in r and not _es_numero(r[clave]):
                    errores.append(f"{donde}: '{clave}' de la zona debe ser un número")


def _es_texto_lleno(x) -> bool:
    return isinstance(x, str) and bool(x.strip())


def validar(p) -> list[str]:
    if not isinstance(p, dict):
        return ["la pieza debe ser un objeto JSON"]
    errores: list[str] = []
    if p.get("version") != 1:
        errores.append("version: debe ser 1")
    formato = p.get("formato")
    if formato not in FORMATOS:
        errores.append(f"formato: debe ser uno de {', '.join(FORMATOS)}")
    elif p.get("variante") not in FORMATOS[formato]:
        errores.append(f"variante: para {formato} debe ser una de {', '.join(FORMATOS[formato])}")
    if not (isinstance(p.get("boda"), str) and RE_BODA.match(p["boda"])):
        errores.append("boda: debe tener la forma AAAA-MM-DD_lugar (minúsculas y guiones)")
    if not (isinstance(p.get("tema"), str) and RE_TEMA.match(p["tema"])):
        errores.append("tema: solo minúsculas, números y guiones")
    if p.get("permiso_caras") not in PERMISOS:
        errores.append(f"permiso_caras: debe ser uno de {', '.join(PERMISOS)}")
    if "hay_caras" in p and not isinstance(p["hay_caras"], bool):
        errores.append("hay_caras: debe ser verdadero o falso")
    if not isinstance(p.get("pendientes", []), list):
        errores.append("pendientes: debe ser una lista")
    if not isinstance(p.get("texto", ""), str):
        errores.append("texto: debe ser un texto")
    if p.get("ubicacion") is not None and not isinstance(p["ubicacion"], str):
        errores.append("ubicacion: debe ser un texto o null")
    a_mano = p.get("a_mano_despues", [])
    if not (isinstance(a_mano, list) and all(isinstance(x, str) for x in a_mano)):
        errores.append("a_mano_despues: debe ser una lista de textos")
    musica = p.get("musica")
    if musica is not None and not (isinstance(musica, dict) and _es_texto_lleno(musica.get("ruta"))
                                   and _es_texto_lleno(musica.get("licencia"))):
        errores.append("musica: debe ser null o un objeto con 'ruta' y 'licencia' (textos no vacíos)")

    els = p.get("elementos")
    if not isinstance(els, list) or not els:
        errores.append("elementos: debe ser una lista no vacía")
        return errores
    if not all(isinstance(e, dict) for e in els):
        errores.append("elementos: cada elemento debe ser un objeto")
        return errores

    n = len(els)
    if formato == "deslizar" and not 5 <= n <= 9:
        errores.append(f"elementos: deslizar admite de 5 a 9 fotos (hay {n})")
    if formato == "historia" and not 1 <= n <= 10:
        errores.append(f"elementos: historia admite de 1 a 10 (hay {n})")

    duraciones = []
    for i, e in enumerate(els):
        if not isinstance(e.get("fichero"), str) or not e["fichero"]:
            errores.append(f"elementos[{i}]: falta 'fichero'")
        elif Path(e["fichero"]).suffix.lower() in VIDEO_NO_ADMITIDO:
            errores.append(f"elementos[{i}]: la extensión de {e['fichero']} no se admite; "
                           f"los vídeos deben ser {' o '.join(sorted(EXT_VIDEO))} (conviértelo antes)")
        else:
            _validar_retoques(e, i, errores)
        if e.get("rotulo") is not None and not isinstance(e["rotulo"], str):
            errores.append(f"elementos[{i}]: 'rotulo' debe ser un texto o null")
        if formato == "reel":
            if e.get("tramo") not in TRAMOS:
                errores.append(f"elementos[{i}]: 'tramo' debe ser uno de {', '.join(TRAMOS)}")
            duraciones.append(_duracion_valida(e, i, errores))
        elif formato == "historia" and p.get("variante") == "clip-cta":
            # Cada elemento es una historia aparte: el límite de 15 s es por clip, no la suma
            d = _duracion_valida(e, i, errores)
            if d is not None and d > HISTORIA_CLIP_MAX:
                errores.append(f"elementos[{i}]: el clip dura {d:g} s y una historia no puede pasar de 15 s")

    if formato == "reel" and duraciones and None not in duraciones:
        total = sum(duraciones) + CIERRE_REEL
        if not REEL_MIN <= total <= REEL_MAX:
            errores.append(f"elementos: el reel dura {total:g} s con el cierre y debe durar de 15 a 25 s")
    return errores


def cargar_pieza(ruta: Path) -> dict:
    """Lee y valida pieza.json; lanza PiezaInvalida con todos los errores."""
    try:
        p = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise PiezaInvalida([f"no se puede leer {ruta}: {e}"])
    errores = validar(p)
    if errores:
        raise PiezaInvalida(errores)
    return p
