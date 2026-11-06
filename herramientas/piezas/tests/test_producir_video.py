import json
import re
import subprocess

import pytest
from comprobar import comprobar_medios
from PIL import Image
from producir import generar_html, producir, video


def _inicios(html: str, clase: str) -> list[tuple[str, float, float]]:
    """(src o id, data-start, data-duration) de los elementos con esa clase, en orden."""
    filas = []
    for m in re.finditer(r"<(?:video|img|div)\b[^>]*>", html):
        etiqueta = m.group(0)
        if f'class="{clase}"' not in etiqueta:
            continue
        src = (re.search(r'src="([^"]+)"', etiqueta) or re.search(r'id="([^"]+)"', etiqueta)).group(1)
        ini = float(re.search(r'data-start="([^"]+)"', etiqueta).group(1))
        dur = float(re.search(r'data-duration="([^"]+)"', etiqueta).group(1))
        filas.append((src, ini, dur))
    return filas


def test_html_del_reel_encadena_planos_y_cierre(pieza_minima):
    p = pieza_minima("reel")                               # 4 elementos de 3 s
    html = generar_html(p, [3, 3, 3, 3])
    assert html.count('class="clip plano"') == 5           # 4 planos + cierre
    assert 'src="assets/cierre.mp4" data-start="12"' in html
    assert "<!--PLANOS-->" not in html and "/*ANIMACION*/" not in html


def test_planos_seguidos_en_orden_y_duracion_raiz(pieza_minima):
    p = pieza_minima("reel")
    p["elementos"].reverse()                               # el orden manda, no la posición
    html = generar_html(p, [3, 3, 3, 3])
    assert _inicios(html, "clip plano") == [
        ("assets/material/01.mp4", 0, 3), ("assets/material/02.mp4", 3, 3),
        ("assets/material/03.mp4", 6, 3), ("assets/material/04.mp4", 9, 3),
        ("assets/cierre.mp4", 12, 4)]
    assert re.search(r'data-composition-id="reel"[^>]*data-duration="16"', html)
    assert 'data-media-start="0"' in html and "window.__timelines[\"reel\"] = tl" in html


def test_foto_en_el_reel_con_acercamiento_lento(pieza_minima):
    p = pieza_minima("reel")
    p["elementos"][1] = {"orden": 2, "fichero": "IMG_2.HEIC", "duracion": 2.5, "tramo": "detalle"}
    html = generar_html(p, [3, 2.5, 3, 3])
    assert '<img id="p2" class="clip plano" src="assets/material/02.jpg" data-start="3" data-duration="2.5"' in html
    assert 'tl.fromTo("#p2", { scale: 1 }, { scale: 1.06, duration: 2.5, ease: "none" }, 3);' in html
    assert 'tl.fromTo("#p1", { scale: 1 }, { scale: 1.05, duration: 3, ease: "none" }, 0);' in html


def test_transicion_041_antes_del_corte_tras_momento(pieza_minima):
    p = pieza_minima("reel")                               # momento es el último: corte con el cierre
    html = generar_html(p, [3, 3, 3, 3])
    assert _inicios(html, "clip transicion") == [("assets/transicion.webm", 11.59, 0.866)]

    p["elementos"][2]["tramo"] = "momento"                 # momento, momento y luego nada más
    p["elementos"][3]["tramo"] = "prueba"                  # momento → prueba en el segundo 9
    html = generar_html(p, [3, 3, 3, 3])
    assert _inicios(html, "clip transicion") == [("assets/transicion.webm", 8.59, 0.866)]


def test_sin_momento_no_hay_transicion(pieza_minima):
    p = pieza_minima("reel")
    p["elementos"][3]["tramo"] = "prueba"
    assert "transicion.webm" not in generar_html(p, [3, 3, 3, 3])


def test_rotulo_escapado(pieza_minima):
    p = pieza_minima("reel"); p["elementos"][0]["rotulo"] = 'Salís "de" la iglesia & <ya>'
    html = generar_html(p, [3, 3, 3, 3])
    assert "<ya>" not in html and "&lt;ya&gt;" in html and "&amp;" in html


def test_rotulo_dura_su_plano_y_variante_limpio(pieza_minima):
    p = pieza_minima("reel")
    p["elementos"][1]["rotulo"] = "Las cestas"
    html = generar_html(p, [3, 3, 3, 3])
    assert _inicios(html, "clip rotulo") == [("r2", 3, 3)]
    assert "clip rotulo rotulo-titular" not in html and "clip velo" not in html


def test_variante_titular_gancho_grande_con_velo(pieza_minima):
    p = pieza_minima("reel") | {"variante": "titular"}
    p["elementos"][0]["rotulo"] = "Así se sale"
    p["elementos"][2]["rotulo"] = "Con chófer o sin él"
    html = generar_html(p, [3, 3, 3, 3])
    assert _inicios(html, "clip rotulo rotulo-titular") == [("r1", 0, 3)]
    assert _inicios(html, "clip rotulo") == [("r3", 6, 3)]
    assert _inicios(html, "clip velo") == [("v1", 0, 3)]


def test_historia_clip_sin_cierre(pieza_minima):
    p = pieza_minima("historia") | {"variante": "clip-cta"}
    p["elementos"] = [{"orden": 1, "fichero": "a.mov", "desde": 0, "hasta": 6}]
    html = generar_html(p, [6])
    assert "cierre.mp4" not in html and "¿Cuándo os casáis?" in html


def test_historia_clip_con_rotulo_propio(pieza_minima):
    p = pieza_minima("historia") | {"variante": "clip-cta"}
    p["elementos"] = [{"orden": 1, "fichero": "a.mov", "desde": 0, "hasta": 6, "rotulo": "Escribidnos"}]
    html = generar_html(p, [6])
    assert "¿Cuándo os casáis?" not in html and "Escribidnos" in html
    assert "transicion.webm" not in html
    assert re.search(r'data-composition-id="reel"[^>]*data-duration="6"', html)


def test_musica_con_fundido_de_salida(pieza_minima):
    p = pieza_minima("reel") | {"musica": {"ruta": "/x/Pista Libre.MP3", "licencia": "cc0"}}
    html = generar_html(p, [3, 3, 3, 3])
    assert ('<audio id="musica" src="assets/musica.mp3" data-start="0" data-duration="16" '
            'data-track-index="2" data-volume="1"') in html
    lanes = json.loads(re.search(r"data-automation='([^']+)'", html).group(1))
    assert lanes["lanes"][0]["target"] == "volume"
    assert [(q["t"], q["v"]) for q in lanes["lanes"][0]["points"]] == [(0, 1), (15, 1), (16, 0)]


def test_sin_musica_no_hay_audio(pieza_minima):
    assert "<audio" not in generar_html(pieza_minima("reel"), [3, 3, 3, 3])


def test_producir_ya_no_deja_el_reel_sin_implementar(tmp_path, pieza_minima, monkeypatch):
    import producir as modulo
    llamadas = []
    monkeypatch.setattr(modulo, "video", lambda p, proy, sal: llamadas.append(p["formato"]) or [])
    from ayudas import escribir
    producir(escribir(tmp_path, pieza_minima("reel")), tmp_path / "proy", tmp_path / "out")
    assert llamadas == ["reel"]


@pytest.mark.lento
def test_render_real_del_reel(tmp_path, pieza_reel_preparada):
    [mp4, portada] = video(*pieza_reel_preparada(), tmp_path / "out")
    assert comprobar_medios("reel", "limpio", [mp4]) == []
    assert Image.open(portada).size == (1080, 1920)
    assert (mp4.name, portada.name) == ("reel.mp4", "portada.jpg")
    flujos = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name",
                             "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout
    assert "aac,audio" in flujos                           # la música entra en el MP4


@pytest.mark.lento
def test_render_real_de_historias_en_clip(tmp_path, pieza_historia_clip_preparada):
    p, proyecto = pieza_historia_clip_preparada(n_clips=2)
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "historia.mp4").write_bytes(b"vieja")   # salida antigua: se borra
    salidas = video(p, proyecto, tmp_path / "out")
    assert [s.name for s in salidas] == ["historia-01.mp4", "historia-02.mp4"]
    assert not (tmp_path / "out" / "historia.mp4").exists()
    assert comprobar_medios("historia", "clip-cta", salidas) == []


def test_video_se_niega_sin_material_preparado(tmp_path, pieza_minima):
    with pytest.raises(RuntimeError, match="preparado.json"):
        video(pieza_minima("reel"), tmp_path / "proy", tmp_path / "out")
    assert not (tmp_path / "out").exists()
