"""Inventario de la carpeta de una boda: miniaturas, fecha EXIF y hojas de contacto.

Solo LEE la carpeta de la boda (Drive). Todo lo que escribe va a `trabajo/_inventario/`.

Uso: python3 herramientas/piezas/inventario.py "<carpeta boda>" "<trabajo>"
"""
import collections
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rutas  # noqa: E402

sys.path.insert(0, str(rutas.MATERIAL))
from comun import EXT_FOTO, EXT_VIDEO, ffprobe, nombre_miniatura  # noqa: E402

_spec = importlib.util.spec_from_file_location("analizar_material", rutas.MATERIAL / "1_analizar.py")
_analizar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_analizar)

POR_HOJA = 20
COLUMNAS = 5
CELDA = (300, 300)
ROTULO = 44


def _ficheros(boda: Path) -> list[Path]:
    """Fotos y vídeos de la boda, recursivo, sin ocultos."""
    salida = []
    for p in sorted(boda.rglob("*")):
        rel = p.relative_to(boda)
        if any(parte.startswith(".") for parte in rel.parts) or not p.is_file():
            continue
        if p.suffix.lower() in EXT_FOTO | EXT_VIDEO:
            salida.append(p)
    return salida


def _nombre_thumb(rel: str) -> str:
    return nombre_miniatura(rel.replace("/", "__"))


def _miniatura_video(ruta: Path, destino: Path) -> None:
    """Fotograma del segundo 1 (o del 0 si el vídeo es más corto), a 400 px."""
    with tempfile.TemporaryDirectory(dir=destino.parent) as tmp:
        bruto = Path(tmp) / "f.jpg"
        for t in ("1", "0"):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", t, "-i", str(ruta),
                            "-frames:v", "1", str(bruto)], capture_output=True)
            if bruto.exists() and bruto.stat().st_size > 0:
                break
        with Image.open(bruto) as im:
            im = im.convert("RGB")
            im.thumbnail((400, 400))
            im.save(destino, quality=80)


def _registro_video(boda: Path, rel: str, thumbs: Path) -> dict:
    r = {"file": rel, "kind": "vid"}
    try:
        r.update(ffprobe(boda / rel))
        _miniatura_video(boda / rel, thumbs / _nombre_thumb(rel))
    except Exception as e:  # noqa: BLE001 - se apunta y se sigue con el resto
        r["error"] = repr(e)
    return r


def _registro_foto(boda: Path, rel: str, thumbs: Path) -> dict:
    r = _analizar.analizar_foto((boda, rel, thumbs))
    antes = thumbs / nombre_miniatura(rel)  # nombre que usa analizar_foto (sin carpetas)
    if "error" not in r and antes.exists():
        antes.replace(thumbs / _nombre_thumb(rel))
    return {k: r[k] for k in ("file", "kind", "w", "h", "date", "error") if k in r}


def _fuente(tam: int):
    try:
        return ImageFont.load_default(size=tam)
    except TypeError:  # Pillow antiguo
        return ImageFont.load_default()


def _hojas(filas: list[dict], thumbs: Path, hojas: Path) -> None:
    for vieja in hojas.glob("hoja_*.jpg"):
        vieja.unlink()
    fuente = _fuente(16)
    ancho, alto = CELDA
    for n in range(0, len(filas), POR_HOJA):
        grupo = filas[n:n + POR_HOJA]
        filas_hoja = (len(grupo) + COLUMNAS - 1) // COLUMNAS
        hoja = Image.new("RGB", (COLUMNAS * ancho, filas_hoja * (alto + ROTULO)), (30, 30, 30))
        dib = ImageDraw.Draw(hoja)
        for i, f in enumerate(grupo):
            x, y = (i % COLUMNAS) * ancho, (i // COLUMNAS) * (alto + ROTULO)
            miniatura = thumbs / _nombre_thumb(f["file"])
            if miniatura.exists():
                with Image.open(miniatura) as im:
                    im = ImageOps.contain(im.convert("RGB"), (ancho - 8, alto - 8))
                    hoja.paste(im, (x + (ancho - im.width) // 2, y + (alto - im.height) // 2))
            else:
                dib.text((x + 10, y + 10), "sin miniatura", fill=(200, 80, 80), font=fuente)
            rotulo = Path(f["file"]).name
            if f.get("kind") == "vid" and "dur" in f:
                rotulo += f"  {f['dur']:.1f} s".replace(".", ",")
            dib.text((x + 6, y + alto + 4), rotulo[:38], fill=(235, 235, 235), font=fuente)
        hoja.save(hojas / f"hoja_{n // POR_HOJA + 1:02d}.jpg", quality=85)


def _leer_filas(jsonl: Path) -> list[dict]:
    filas = []
    if jsonl.exists():
        for linea in jsonl.read_text(encoding="utf-8").splitlines():
            try:
                filas.append(json.loads(linea))
            except json.JSONDecodeError:
                pass  # línea cortada por una ejecución interrumpida
    return filas


def inventariar(boda: Path, trabajo: Path) -> Path:
    """Escribe trabajo/_inventario/{inventario.jsonl,thumbs/,hojas/}. Reanudable."""
    boda, trabajo = Path(boda), Path(trabajo)
    inv = trabajo / "_inventario"
    thumbs, hojas = inv / "thumbs", inv / "hojas"
    thumbs.mkdir(parents=True, exist_ok=True)
    hojas.mkdir(parents=True, exist_ok=True)
    jsonl = inv / "inventario.jsonl"

    hechos = {f["file"] for f in _leer_filas(jsonl)}
    pendientes = [p.relative_to(boda).as_posix() for p in _ficheros(boda)]
    pendientes = [rel for rel in pendientes if rel not in hechos]
    with open(jsonl, "a", encoding="utf-8") as out:
        for rel in pendientes:
            if Path(rel).suffix.lower() in EXT_VIDEO:
                r = _registro_video(boda, rel, thumbs)
            else:
                r = _registro_foto(boda, rel, thumbs)
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            out.flush()
    _hojas(_leer_filas(jsonl), thumbs, hojas)
    return inv


def fecha_boda(registros: list[dict]) -> date | None:
    """La fecha EXIF más repetida («AAAA:MM:DD HH:MM:SS»)."""
    cuenta = collections.Counter()
    for r in registros:
        try:
            cuenta[datetime.strptime(str(r.get("date")), "%Y:%m:%d %H:%M:%S").date()] += 1
        except ValueError:
            pass
    return cuenta.most_common(1)[0][0] if cuenta else None


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit('Uso: python3 herramientas/piezas/inventario.py "<carpeta boda>" "<trabajo>"')
    boda = Path(sys.argv[1]).expanduser()
    if not boda.is_dir():
        sys.exit(f"No existe la carpeta: {boda}")
    inv = inventariar(boda, Path(sys.argv[2]).expanduser())
    filas = _leer_filas(inv / "inventario.jsonl")
    fecha = fecha_boda(filas)
    print(inv)
    print(f"Ficheros: {len(filas)}")
    print(f"Errores: {sum('error' in f for f in filas)}")
    print(f"Fecha de la boda: {fecha.isoformat() if fecha else 'sin fecha'}")


if __name__ == "__main__":
    main()
