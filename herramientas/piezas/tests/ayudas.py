"""Funciones auxiliares que usan las pruebas de todas las tareas."""
import json
import subprocess
from pathlib import Path


def escribir(carpeta: Path, datos: dict) -> Path:
    """Guarda `datos` como carpeta/pieza.json y devuelve la ruta."""
    ruta = Path(carpeta) / "pieza.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


def leer(inventario: Path) -> dict[str, dict]:
    """Filas de inventario/inventario.jsonl indexadas por `file`."""
    filas = {}
    for linea in (Path(inventario) / "inventario.jsonl").read_text(encoding="utf-8").splitlines():
        if linea.strip():
            fila = json.loads(linea)
            filas[fila["file"]] = fila
    return filas


def _ffprobe(ruta: Path, *args: str) -> str:
    return subprocess.run(["ffprobe", "-v", "error", *args, str(ruta)],
                          capture_output=True, text=True, check=True).stdout.strip()


def ffprobe_wh(ruta: Path) -> tuple[int, int]:
    """Ancho y alto tal como se ve el vídeo (teniendo en cuenta la rotación)."""
    datos = json.loads(_ffprobe(ruta, "-select_streams", "v:0", "-show_streams", "-of", "json"))
    flujo = datos["streams"][0]
    ancho, alto = int(flujo["width"]), int(flujo["height"])
    rotacion = flujo.get("tags", {}).get("rotate")
    for lado in flujo.get("side_data_list", []):
        if "rotation" in lado:
            rotacion = lado["rotation"]
    if rotacion is not None and int(float(rotacion)) % 180 != 0:
        ancho, alto = alto, ancho
    return ancho, alto


def ffprobe_dur(ruta: Path) -> float:
    """Duración del contenedor en segundos."""
    return float(_ffprobe(ruta, "-show_entries", "format=duration", "-of", "csv=p=0"))
