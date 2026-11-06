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


def test_historia_en_clip_el_limite_es_por_clip(pieza_minima, tmp_path):
    p = pieza_minima("historia") | {"variante": "clip-cta"}
    p["elementos"] = [{"orden": i, "fichero": f"c{i}.mov", "desde": 0, "hasta": 6} for i in (1, 2, 3)]
    assert cargar_pieza(escribir(tmp_path, p))["variante"] == "clip-cta"   # 18 s en total, 6 s cada uno
    p["elementos"][1]["hasta"] = 16
    with pytest.raises(PiezaInvalida, match=r"elementos\[1\]"):
        cargar_pieza(escribir(tmp_path, p))


# ---------------------------------------------------------------- retoques (C1, M6)

POLIGONO = [[10, 10], [60, 10], [60, 40], [10, 40]]


def _con_retoques(pieza_minima, fichero, retoques):
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": fichero, "retoques": retoques}]
    if fichero.lower().endswith((".mov", ".mp4")):
        p["variante"] = "clip-cta"
        p["elementos"][0] |= {"desde": 0, "hasta": 3}
    return p


@pytest.mark.parametrize("fichero,retoques", [
    ("IMG_1.HEIC", [{"tipo": "placa", "poligono": POLIGONO}]),
    ("IMG_1.jpg", [{"tipo": "funda", "poligono": POLIGONO + [[5, 25], [8, 20]]}]),
    ("IMG_1.jpg", [{"tipo": "emblema", "caja": [10, 10, 50.5, 30]}]),
    ("v.MOV", [{"tipo": "zona", "t": 1.5, "caja": [10, 10, 50, 30]}]),
    ("v.mp4", [{"tipo": "zona", "t": 1, "caja": [10, 10, 50, 30], "desde": 0.5, "hasta": 2}]),
    ("v.mp4", []),
])
def test_retoques_validos(pieza_minima, tmp_path, fichero, retoques):
    cargar_pieza(escribir(tmp_path, _con_retoques(pieza_minima, fichero, retoques)))


@pytest.mark.parametrize("fichero,retoques,pista", [
    ("IMG_1.jpg", [{"tipo": "matricula", "poligono": POLIGONO}], "tipo"),
    ("IMG_1.jpg", [{"tipo": "Placa", "poligono": POLIGONO}], "tipo"),
    ("v.mp4", [{"tipo": "placa", "poligono": POLIGONO}], "vídeo"),
    ("IMG_1.jpg", [{"tipo": "zona", "t": 1, "caja": [10, 10, 50, 30]}], "foto"),
    ("IMG_1.jpg", [{"tipo": "placa", "poligono": POLIGONO[:3]}], "poligono"),
    ("IMG_1.jpg", [{"tipo": "placa", "poligono": [[10, 10], [60, "x"], [60, 40], [10, 40]]}], "poligono"),
    ("IMG_1.jpg", [{"tipo": "funda", "caja": [10, 10, 50, 30]}], "poligono"),
    ("IMG_1.jpg", [{"tipo": "emblema", "caja": [10, 10, 0, 30]}], "caja"),
    ("IMG_1.jpg", [{"tipo": "emblema", "caja": [10, 10, 50]}], "caja"),
    ("v.mp4", [{"tipo": "zona", "caja": [10, 10, 50, 30]}], "'t'"),
    ("v.mp4", [{"tipo": "zona", "t": 1, "caja": [10, 10, -5, 30]}], "caja"),
    ("v.mp4", [{"tipo": "zona", "t": 1, "caja": [10, 10, 50, 30], "desde": "0"}], "desde"),
    ("IMG_1.jpg", {"tipo": "placa", "poligono": POLIGONO}, "lista"),
    ("IMG_1.jpg", ["placa"], "objeto"),
])
def test_retoques_invalidos(pieza_minima, tmp_path, fichero, retoques, pista):
    with pytest.raises(PiezaInvalida) as e:
        cargar_pieza(escribir(tmp_path, _con_retoques(pieza_minima, fichero, retoques)))
    assert pista in str(e.value)


@pytest.mark.parametrize("fichero", ["v.m4v", "v.AVI", "v.mkv"])
def test_video_con_extension_no_admitida(pieza_minima, tmp_path, fichero):
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": fichero}]
    with pytest.raises(PiezaInvalida, match="extensión"):
        cargar_pieza(escribir(tmp_path, p))


# ---------------------------------------------------------------- música y textos (M2, I2)

@pytest.mark.parametrize("musica", [{"licencia": "cc0"}, {"ruta": "", "licencia": "cc0"},
                                    {"ruta": "m.mp3"}, {"ruta": "m.mp3", "licencia": " "}, "m.mp3"])
def test_musica_exige_ruta_y_licencia(pieza_minima, tmp_path, musica):
    p = pieza_minima("reel") | {"musica": musica}
    with pytest.raises(PiezaInvalida, match="musica"):
        cargar_pieza(escribir(tmp_path, p))


def test_musica_valida_o_nula(pieza_minima, tmp_path):
    for musica in (None, {"ruta": "m.mp3", "licencia": "cc0", "titulo": "Pista"}):
        cargar_pieza(escribir(tmp_path, pieza_minima("reel") | {"musica": musica}))


@pytest.mark.parametrize("cambio,pista", [
    ({"texto": None}, "texto"), ({"ubicacion": 3}, "ubicacion"),
    ({"a_mano_despues": "Etiquetar"}, "a_mano_despues"), ({"a_mano_despues": [1]}, "a_mano_despues"),
])
def test_campos_de_texto_con_tipo_incorrecto(pieza_minima, tmp_path, cambio, pista):
    with pytest.raises(PiezaInvalida, match=pista):
        cargar_pieza(escribir(tmp_path, pieza_minima("deslizar") | cambio))


def test_rotulo_debe_ser_texto(pieza_minima, tmp_path):
    p = pieza_minima("deslizar")
    p["elementos"][0]["rotulo"] = ["a"]
    with pytest.raises(PiezaInvalida, match="rotulo"):
        cargar_pieza(escribir(tmp_path, p))
