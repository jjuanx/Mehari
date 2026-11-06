import json
import shutil
import subprocess
import sys
from datetime import date

from PIL import Image

from ayudas import leer
from inventario import fecha_boda, inventariar
from rejilla import rejilla
from rutas import MATERIAL


def test_inventario_recursivo_y_sin_escribir_en_la_boda(tmp_path, foto_jpg, clip_mp4):
    boda = tmp_path / "Boda 24:10:2026"; (boda / "fotos").mkdir(parents=True); (boda / "videos").mkdir()
    shutil.copy(foto_jpg, boda / "fotos/IMG 1.jpg"); shutil.copy(clip_mp4, boda / "videos/V1.mp4")
    antes = sorted(p.relative_to(boda) for p in boda.rglob("*"))
    inv = inventariar(boda, tmp_path / "trabajo")
    filas = [json.loads(l) for l in (inv / "inventario.jsonl").read_text().splitlines()]
    assert {f["file"] for f in filas} == {"fotos/IMG 1.jpg", "videos/V1.mp4"}
    assert sorted(p.relative_to(boda) for p in boda.rglob("*")) == antes
    assert list((inv / "hojas").glob("hoja_*.jpg"))


def test_fichero_vacio_se_apunta_y_se_sigue(tmp_path, foto_jpg):
    boda = tmp_path / "b"; boda.mkdir(); (boda / "roto.heic").write_bytes(b""); shutil.copy(foto_jpg, boda / "ok.jpg")
    filas = leer(inventariar(boda, tmp_path / "t"))
    assert "error" in filas["roto.heic"] and "error" not in filas["ok.jpg"]


def test_fecha_boda_es_la_mas_repetida():
    regs = [{"date": "2026:10:24 14:06:00"}] * 3 + [{"date": "2026:10:25 10:00:00"}]
    assert fecha_boda(regs) == date(2026, 10, 24)


def test_rejilla_respeta_la_orientacion_exif(tmp_path, foto_rotada):
    salida = rejilla(foto_rotada, tmp_path / "r.jpg")
    with Image.open(salida) as im: assert im.height > im.width   # 3024×4032 tal como se ve


def test_analizar_por_linea_de_comandos_no_cambia(tmp_path, foto_jpg):
    shutil.copy(foto_jpg, tmp_path / "a.jpg")
    subprocess.run([sys.executable, str(MATERIAL / "1_analizar.py"), str(tmp_path)], check=True)
    assert (tmp_path / "_analisis/thumbs/a.jpg.jpg").exists()
