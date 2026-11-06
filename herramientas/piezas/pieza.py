"""Lectura y validación de pieza.json (versión 1)."""
import json
import re
from datetime import date
from pathlib import Path

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
        if formato == "reel":
            if e.get("tramo") not in TRAMOS:
                errores.append(f"elementos[{i}]: 'tramo' debe ser uno de {', '.join(TRAMOS)}")
            duraciones.append(_duracion_valida(e, i, errores))
        elif formato == "historia" and p.get("variante") == "clip-cta":
            duraciones.append(_duracion_valida(e, i, errores))

    if duraciones and None not in duraciones:
        total = sum(duraciones)
        if formato == "reel":
            total += CIERRE_REEL
            if not REEL_MIN <= total <= REEL_MAX:
                errores.append(f"elementos: el reel dura {total:g} s con el cierre y debe durar de 15 a 25 s")
        elif total > HISTORIA_CLIP_MAX:
            errores.append(f"elementos: la historia en clip dura {total:g} s y no puede pasar de 15 s")
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
