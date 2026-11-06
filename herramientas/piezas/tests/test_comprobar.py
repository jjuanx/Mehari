import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from comprobar import ResultadoTexto, comprobar_medios, comprobar_texto
from ayudas import escribir

BUENO = "Sábado en la finca.\n\nEscribidnos al 625 06 42 93.\n\n#cochedeboda #novios2027"
COMPROBAR = Path(__file__).resolve().parents[1] / "comprobar.py"


def _ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def _video(ruta, tam="1080x1920", fps=30, dur=16, codec="libx264", audio=None):
    args = ["-f", "lavfi", "-i", f"testsrc=size={tam}:rate={fps}"]
    if audio:
        args += ["-f", "lavfi", "-i", "sine=frequency=440"]
    args += ["-t", str(dur), "-c:v", codec, "-pix_fmt", "yuv420p"]
    if codec == "libx264":
        args += ["-preset", "ultrafast", "-crf", "35"]
    if audio:
        args += ["-c:a", audio]
    _ffmpeg(*args, str(ruta))
    return ruta


def _jpg(ruta, tam):
    Image.new("RGB", tam).save(ruta, "JPEG", quality=90)
    return ruta


def test_texto_bueno():
    assert comprobar_texto(BUENO) == ResultadoTexto([], [], [])


@pytest.mark.parametrize("malo", ["Nuestro Citroën", "una experiencia única", "boda — finca",
                                  BUENO + " #a #b #c #d", BUENO.replace("625 06 42 93", "")])
def test_texto_con_errores(malo):
    assert comprobar_texto(malo).errores


def test_citroen_sin_tilde_y_mayusculas():
    assert comprobar_texto(BUENO + " CITROEN").errores


def test_cinco_hashtags_valen_y_almohadilla_sola_no_cuenta():
    assert not comprobar_texto(BUENO + " #a #b #c # solo").errores


def test_sevilla_es_aviso_no_error():
    r = comprobar_texto(BUENO + "\nBoda en Sevilla.")
    assert not r.errores and r.avisos


def test_cadiz_es_aviso():
    assert comprobar_texto(BUENO + " Cádiz").avisos


def test_marcadores_son_pendientes():
    assert comprobar_texto(BUENO + " [PENDIENTE: iglesia]").pendientes == ["[PENDIENTE: iglesia]"]


def test_carrusel_debe_ser_jpeg_1080x1440(tmp_path):
    png = tmp_path / "01.png"; Image.new("RGB", (1080, 1440)).save(png)
    jpg = tmp_path / "02.jpg"; Image.new("RGB", (1080, 1350)).save(jpg)
    assert len(comprobar_medios("deslizar", "foto-entera", [png, jpg])) >= 2


def test_carrusel_valido(tmp_path):
    fs = [_jpg(tmp_path / f"{i}.jpg", (1080, 1440)) for i in range(3)]
    assert comprobar_medios("deslizar", "con-rotulos", fs) == []


def test_carrusel_png_renombrado_jpg_es_error(tmp_path):
    f = tmp_path / "x.jpg"; Image.new("RGB", (1080, 1440)).save(f, "PNG")
    g = _jpg(tmp_path / "y.jpg", (1080, 1440))
    assert any("x.jpg" in e for e in comprobar_medios("deslizar", "foto-entera", [f, g]))


def test_carrusel_numero_de_ficheros(tmp_path):
    uno = [_jpg(tmp_path / "a.jpg", (1080, 1440))]
    once = [_jpg(tmp_path / f"{i}.jpg", (1080, 1440)) for i in range(11)]
    assert comprobar_medios("deslizar", "foto-entera", uno)
    assert comprobar_medios("deslizar", "foto-entera", once)


def test_reel_de_5_segundos_no_vale(clip_mp4):
    assert any("duración" in e for e in comprobar_medios("reel", "limpio", [clip_mp4]))


def test_reel_valido_con_portada(tmp_path):
    v = _video(tmp_path / "reel.mp4")
    p = _jpg(tmp_path / "portada.jpg", (1080, 1920))
    assert comprobar_medios("reel", "titular", [v, p]) == []


def test_reel_con_audio_aac_vale_y_otro_no(tmp_path):
    assert comprobar_medios("reel", "limpio", [_video(tmp_path / "a.mp4", audio="aac")]) == []
    errores = comprobar_medios("reel", "limpio", [_video(tmp_path / "b.mp4", audio="libmp3lame")])
    assert any("audio" in e for e in errores)


def test_reel_fps_y_dimensiones_incorrectas(tmp_path):
    assert any("fps" in e for e in comprobar_medios("reel", "limpio", [_video(tmp_path / "a.mp4", fps=25)]))
    assert any("dimensiones" in e for e in
               comprobar_medios("reel", "limpio", [_video(tmp_path / "b.mp4", tam="1920x1080")]))


def test_reel_29_97_no_vale(tmp_path):
    assert any("fps" in e for e in
               comprobar_medios("reel", "limpio", [_video(tmp_path / "a.mp4", fps="30000/1001")]))


def test_reel_codec_incorrecto(tmp_path):
    v = _video(tmp_path / "a.mp4", codec="mpeg4")
    assert any("códec" in e for e in comprobar_medios("reel", "limpio", [v]))


def test_reel_otro_fichero_es_error(tmp_path):
    v = _video(tmp_path / "reel.mp4")
    o = tmp_path / "notas.txt"; o.write_text("x")
    assert any("notas.txt" in e for e in comprobar_medios("reel", "limpio", [v, o]))


def test_reel_vertical_rotado_se_acepta_como_dimension(tmp_path, clip_rotado):
    # 1920x1080 con rotación 90° se ve de 1080x1920: no debe haber error de dimensiones
    assert not any("dimensiones" in e for e in comprobar_medios("reel", "limpio", [clip_rotado]))


def test_historia_jpg_y_mp4(tmp_path):
    assert comprobar_medios("historia", "foto-frase", [_jpg(tmp_path / "h.jpg", (1080, 1920))]) == []
    assert comprobar_medios("historia", "clip-cta", [_video(tmp_path / "h.mp4", dur=10)]) == []
    assert any("duración" in e for e in
               comprobar_medios("historia", "clip-cta", [_video(tmp_path / "l.mp4", dur=16)]))
    assert comprobar_medios("historia", "foto-frase", [_jpg(tmp_path / "m.jpg", (1080, 1440))])


def test_fichero_inexistente_es_error(tmp_path):
    assert comprobar_medios("historia", "foto-frase", [tmp_path / "no.jpg"])


def test_cli(tmp_path, pieza_minima):
    p = pieza_minima("historia")
    ruta = escribir(tmp_path, p)
    jpg = _jpg(tmp_path / "h.jpg", (1080, 1920))
    r = subprocess.run([sys.executable, str(COMPROBAR), str(ruta), str(jpg)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["errores"] == []
    p["texto"] = "Nuestro Citroën"
    escribir(tmp_path, p)
    r = subprocess.run([sys.executable, str(COMPROBAR), str(ruta), str(jpg)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and json.loads(r.stdout)["errores"]
