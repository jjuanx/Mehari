from datetime import date

import pytest

from ayudas import escribir
from pieza import PiezaInvalida, cargar_pieza, duracion_total, id_pieza


def test_pieza_valida_de_cada_formato(pieza_minima, tmp_path):
    for formato in ("reel", "deslizar", "historia"):
        ruta = escribir(tmp_path, pieza_minima(formato))
        assert cargar_pieza(ruta)["formato"] == formato


def test_junta_todos_los_errores(tmp_path):
    with pytest.raises(PiezaInvalida) as e:
        cargar_pieza(escribir(tmp_path, {"version": 1, "formato": "reel", "variante": "con-rotulos",
                                          "boda": "Boda 24:10:2026", "permiso_caras": "quizá"}))
    texto = " ".join(e.value.errores)
    assert "variante" in texto and "boda" in texto and "permiso_caras" in texto and "elementos" in texto


def test_deslizar_admite_de_5_a_9_fotos_mas_el_cierre(pieza_minima, tmp_path):
    p = pieza_minima("deslizar")
    p["elementos"] = p["elementos"][:1] * 4
    with pytest.raises(PiezaInvalida):
        cargar_pieza(escribir(tmp_path, p))


def test_reel_dura_entre_15_y_25_segundos_con_el_cierre(pieza_minima, tmp_path):
    p = pieza_minima("reel")                       # suma de elementos 12 s + 4 s de cierre = 16 s
    assert duracion_total(cargar_pieza(escribir(tmp_path, p))) == 16.0
    p["elementos"][0]["hasta"] += 10               # 26 s
    with pytest.raises(PiezaInvalida):
        cargar_pieza(escribir(tmp_path, p))


def test_historia_en_clip_no_pasa_de_15_segundos(pieza_minima, tmp_path):
    p = pieza_minima("historia")
    p["variante"] = "clip-cta"
    p["elementos"] = [{"orden": 1, "fichero": "a.mov", "desde": 0, "hasta": 16}]
    with pytest.raises(PiezaInvalida):
        cargar_pieza(escribir(tmp_path, p))


def test_id_pieza():
    assert id_pieza({"formato": "deslizar", "tema": "las-cestas"}, date(2026, 11, 6)) == "2026-11-06_deslizar_las-cestas"


def test_ayudas_de_ffprobe_con_las_fixtures_de_video(clip_mp4, clip_rotado):
    from ayudas import ffprobe_dur, ffprobe_wh
    assert ffprobe_wh(clip_mp4) == (1080, 1920)
    assert ffprobe_wh(clip_rotado) == (1080, 1920)   # 1920x1080 con rotación 90 = vertical
    assert abs(ffprobe_dur(clip_mp4) - 5.0) < 0.2


def test_fixtures_de_foto(foto_jpg, foto_rotada):
    from PIL import Image, ImageOps
    assert Image.open(foto_jpg).size == (3024, 4032)
    assert Image.open(foto_rotada).size == (4032, 3024)
    assert ImageOps.exif_transpose(Image.open(foto_rotada)).size == (3024, 4032)
