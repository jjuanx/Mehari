"""Localiza la carpeta de Drive «Mehari We» y las carpetas de boda que encajan con una consulta.

Reglas de búsqueda de bodas:
- Se mira bajo `01_Material/` hasta profundidad 3. Es candidata una carpeta con fotos o vídeos
  directamente o dentro de sus subcarpetas `fotos/` y `videos/`.
- Una carpeta que se llama `fotos` o `videos` nunca es candidata (lo es su carpeta madre).
- Se ignoran las carpetas que empiezan por `_` o `.` y las de la lista EXCLUIDAS (miniaturas).
- Si una candidata contiene otras candidatas (p. ej. `Selecccion` con carpetas de boda dentro),
  se descarta: solo cuentan las carpetas más profundas.
- «la última» / «última»: solo cuentan las candidatas con una fecha reconocible en su propio
  nombre («Boda 2:11:2026», «Boda 2_11_2026», «2026-11-07_sanlucar»); de ellas, la de modificación más reciente.
- Con fecha o lugar en la consulta solo salen las que coinciden en el nombre. Gana la fecha
  sobre el lugar; a igualdad, la modificada más recientemente.
"""
import json
import os
import re
import sys
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

NOMBRE_DRIVE = "Mehari We"
EXCLUIDAS = {"galeria"}  # solo miniaturas; se compara en minúsculas
CARPETAS_GENERICAS = {"fotos", "videos"}
EXTENSIONES = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".mp4", ".mov", ".m4v", ".avi"}
PROFUNDIDAD_MAX = 3
MESES = {m: i for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(), 1)}
MESES["setiembre"] = 9
PALABRAS_VACIAS = {"boda", "bodas", "del", "de", "la", "el", "los", "las", "en", "ultima", "una", "mi", "con", "y"}

_MES = "|".join(MESES)
# «_» porque Drive para Windows cambia «:» por «_» («Boda 24:10:2026» → «Boda 24_10_2026»)
RE_ISO = re.compile(r"(?<!\d)(\d{4})[-/:._](\d{1,2})[-/:._](\d{1,2})(?!\d)")
RE_DMA = re.compile(r"(?<!\d)(\d{1,2})[-/:._](\d{1,2})[-/:._](\d{4})(?!\d)")
RE_DM = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])")
RE_TEXTO = re.compile(rf"(?<!\d)(\d{{1,2}})\s+de\s+({_MES})(?:\s+(?:de|del)\s+(\d{{4}}))?(?!\w)")


def raiz_drive(entorno: Mapping[str, str], casa: Path,
               unidades: Sequence[Path] = (Path("G:/"),)) -> Path | None:
    """Primera ruta existente: variable MEHARI_DRIVE, Drive en Mac, Drive en Windows."""
    candidatas: list[Path] = []
    if entorno.get("MEHARI_DRIVE"):
        candidatas.append(Path(entorno["MEHARI_DRIVE"]))
    nube = Path(casa) / "Library" / "CloudStorage"
    if nube.is_dir():
        for cuenta in sorted(nube.glob("GoogleDrive-*")):
            candidatas += [cuenta / "My Drive" / NOMBRE_DRIVE, cuenta / "Mi unidad" / NOMBRE_DRIVE]
    for unidad in unidades:
        candidatas += [Path(unidad) / "Mi unidad" / NOMBRE_DRIVE, Path(unidad) / "My Drive" / NOMBRE_DRIVE]
    return next((c for c in candidatas if c.exists()), None)


def _fechas(texto: str, hoy: date) -> list[tuple[date, bool]]:
    """Fechas halladas y si la consulta traía el año (si no, se usa el de `hoy`)."""
    texto = texto.lower()
    halladas: list[tuple[date, bool]] = []

    def anota(patron, orden):
        nonlocal texto
        for m in patron.finditer(texto):
            g = orden(m)
            try:
                halladas.append((date(g[0] or hoy.year, g[1], g[2]), bool(g[0])))
            except ValueError:
                pass
        texto = patron.sub(" ", texto)

    anota(RE_ISO, lambda m: (int(m[1]), int(m[2]), int(m[3])))
    anota(RE_DMA, lambda m: (int(m[3]), int(m[2]), int(m[1])))
    anota(RE_TEXTO, lambda m: (int(m[3]) if m[3] else None, MESES[m[2]], int(m[1])))
    anota(RE_DM, lambda m: (None, int(m[2]), int(m[1])))
    return halladas


def fechas_en(consulta: str, hoy: date | None = None) -> list[date]:
    """Fechas de la consulta; sin año se usa el año en curso."""
    return [f for f, _ in _fechas(consulta, hoy or date.today())]


def _normaliza(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.lower()


def _palabras_de_lugar(consulta: str) -> list[str]:
    resto = consulta.lower()
    for patron in (RE_ISO, RE_DMA, RE_TEXTO, RE_DM):
        resto = patron.sub(" ", resto)
    palabras = re.findall(r"[a-z0-9ñ]+", _normaliza(resto))
    return [p for p in palabras if p not in PALABRAS_VACIAS and not p.isdigit()]


@dataclass
class Candidata:
    ruta: Path
    relativa: str
    motivo: str


def _tiene_medios(carpeta: Path) -> bool:
    try:
        return any(f.is_file() and not f.name.startswith(".") and f.suffix.lower() in EXTENSIONES
                   for f in carpeta.iterdir())
    except OSError:
        return False


def _carpetas_con_medios(raiz: Path) -> list[Path]:
    base = raiz / "01_Material"
    encontradas: list[Path] = []

    def recorre(carpeta: Path, profundidad: int) -> None:
        try:
            hijas = sorted(h for h in carpeta.iterdir() if h.is_dir())
        except OSError:
            return
        for hija in hijas:
            nombre = hija.name
            if nombre.startswith(("_", ".")) or nombre.lower() in EXCLUIDAS:
                continue
            if nombre.lower() not in CARPETAS_GENERICAS:
                genericas = [hija / g for g in CARPETAS_GENERICAS if (hija / g).is_dir()]
                if _tiene_medios(hija) or any(_tiene_medios(g) for g in genericas):
                    encontradas.append(hija)
            if profundidad < PROFUNDIDAD_MAX:
                recorre(hija, profundidad + 1)

    if base.is_dir():
        recorre(base, 1)
    return [c for c in encontradas
            if not any(otra != c and c in otra.parents for otra in encontradas)]


def _modificacion(carpeta: Path) -> float:
    rutas = [carpeta] + [carpeta / g for g in CARPETAS_GENERICAS if (carpeta / g).is_dir()]
    def mtime(r: Path) -> float:
        try:
            return r.stat().st_mtime
        except OSError:
            return 0.0

    return max(mtime(r) for r in rutas)


def buscar_bodas(raiz: Path, consulta: str) -> list[Candidata]:
    """Carpetas de boda que encajan con la consulta, mejores primero."""
    raiz = Path(raiz)
    hoy = date.today()
    fechas = _fechas(consulta, hoy)
    lugar = _palabras_de_lugar(consulta)
    quiere_ultima = "ultima" in _normaliza(consulta).split()
    puntuadas: list[tuple[int, float, Candidata]] = []
    for carpeta in _carpetas_con_medios(raiz):
        motivos, puntos = [], 0
        en_nombre = {(f.year, f.month, f.day) for f, _ in _fechas(carpeta.name, hoy)}
        en_nombre_sin_año = {(m, d) for _, m, d in en_nombre}
        for f, con_año in fechas:
            if (f.year, f.month, f.day) in en_nombre or (not con_año and (f.month, f.day) in en_nombre_sin_año):
                motivos.append(f"fecha {f.isoformat()} en el nombre")
                puntos = 2
                break
        nombre = _normaliza(carpeta.name)
        lugar_ok = bool(lugar) and all(p in nombre for p in lugar)
        if lugar_ok:
            motivos.append(f"lugar «{' '.join(lugar)}» en el nombre")
            puntos = max(puntos, 1)
        if (fechas and not any("fecha" in m for m in motivos)) or (lugar and not lugar_ok):
            continue
        if not motivos:
            motivos.append("la más reciente" if quiere_ultima else "sin filtro")
        relativa = carpeta.relative_to(raiz).as_posix()
        puntuadas.append((puntos, _modificacion(carpeta), Candidata(carpeta, relativa, " y ".join(motivos))))
    puntuadas.sort(key=lambda t: (t[0], t[1]), reverse=True)
    if quiere_ultima:
        con_fecha = [t for t in puntuadas if _fechas(t[2].ruta.name, hoy)]
        puntuadas = sorted(con_fecha, key=lambda t: t[1], reverse=True)[:1]
    return [c for _, _, c in puntuadas]


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):  # JSON en UTF-8 también en Windows (cp1252 por defecto)
        sys.stdout.reconfigure(encoding="utf-8")
    consulta = " ".join(argv)
    drive = raiz_drive(os.environ, Path.home())
    candidatas = buscar_bodas(drive, consulta) if drive else []
    salida = {"drive": str(drive) if drive else None,
              "candidatas": [{"ruta": str(c.ruta), "relativa": c.relativa, "motivo": c.motivo} for c in candidatas]}
    print(json.dumps(salida, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
