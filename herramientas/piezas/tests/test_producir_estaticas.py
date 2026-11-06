import pytest
from ayudas import escribir, pagina_renderizada
from PIL import Image
from producir import estaticas, producir


def test_deslizar_da_jpegs_1080x1440_mas_cierre(tmp_path, pieza_deslizar_preparada):
    salidas = estaticas(*pieza_deslizar_preparada(n_fotos=5), tmp_path / "out")
    assert [s.name for s in salidas] == [f"{i:02d}.jpg" for i in range(1, 7)]
    assert all(Image.open(s).size == (1080, 1440) for s in salidas)


def test_historia_foto_es_1080x1920(tmp_path, pieza_historia_preparada):
    [s] = estaticas(*pieza_historia_preparada(), tmp_path / "out")
    assert s.name == "historia.jpg" and Image.open(s).size == (1080, 1920)


def test_historia_con_varios_elementos_numera(tmp_path, pieza_historia_preparada):
    salidas = estaticas(*pieza_historia_preparada(n_fotos=2), tmp_path / "out")
    assert [s.name for s in salidas] == ["historia-01.jpg", "historia-02.jpg"]


def test_rotulo_con_caracteres_especiales_sale_literal(tmp_path, pieza_deslizar_preparada):
    p, proy = pieza_deslizar_preparada(n_fotos=5, rotulo='Sábado en "La Posadilla" & <cía>')
    estaticas(p, proy, tmp_path / "out")
    html = pagina_renderizada(proy, s=0)
    assert 'Sábado en "La Posadilla" & <cía>' in html


def test_rotulo_con_cierre_de_script_no_rompe(tmp_path, pieza_deslizar_preparada):
    p, proy = pieza_deslizar_preparada(n_fotos=5, rotulo="a </script> b")
    estaticas(p, proy, tmp_path / "out")
    assert "a </script> b" in pagina_renderizada(proy, s=0)


def test_rotulo_con_apertura_de_comentario_y_script(tmp_path, pieza_deslizar_preparada):
    p, proy = pieza_deslizar_preparada(n_fotos=5, rotulo="<!--<script>")
    estaticas(p, proy, tmp_path / "out")
    assert "<!--<script>" in pagina_renderizada(proy, s=0)


def test_borra_salidas_antiguas(tmp_path, pieza_deslizar_preparada, pieza_historia_preparada):
    out = tmp_path / "out"
    estaticas(*pieza_deslizar_preparada(n_fotos=5), out)
    (out / "notas.txt").write_text("x")
    p, proy = pieza_deslizar_preparada(n_fotos=2)
    estaticas(p, proy, out)
    assert sorted(f.name for f in out.glob("*.jpg")) == ["01.jpg", "02.jpg", "03.jpg"]
    assert (out / "notas.txt").exists()
    salida_h = tmp_path / "h"
    estaticas(*pieza_historia_preparada(n_fotos=2), salida_h)
    estaticas(*pieza_historia_preparada(n_fotos=1), salida_h)
    assert [f.name for f in salida_h.glob("*.jpg")] == ["historia.jpg"]


def test_cierre_y_variantes(tmp_path, pieza_deslizar_preparada):
    p, proy = pieza_deslizar_preparada(n_fotos=3, variante="con-rotulos")
    estaticas(p, proy, tmp_path / "out")
    cierre = pagina_renderizada(proy, s=3)
    assert "¿Cuándo os casáis?" in cierre and "WhatsApp · 625 06 42 93" in cierre
    assert "Pedir fecha" in cierre
    assert "Desliza" in pagina_renderizada(proy, s=0)
    assert pagina_renderizada(proy, s=1).splitlines()[0] == "01"
    assert pagina_renderizada(proy, s=2).splitlines()[0] == "02"


def test_foto_entera_solo_rotulo_en_portada_y_cierre(tmp_path, pieza_deslizar_preparada):
    p, proy = pieza_deslizar_preparada(n_fotos=3, rotulo="Portada")
    estaticas(p, proy, tmp_path / "out")
    assert "Portada" in pagina_renderizada(proy, s=0)
    assert pagina_renderizada(proy, s=1).strip() == ""


def test_la_plantilla_no_borra_el_material_preparado(tmp_path, pieza_deslizar_preparada):
    p, proy = pieza_deslizar_preparada(n_fotos=2)
    estaticas(p, proy, tmp_path / "out")
    assert (proy / "assets/material/01.jpg").exists() and (proy / "revision").exists()


def test_producir_rechaza_formatos_de_video(tmp_path, pieza_minima):
    ruta = escribir(tmp_path, pieza_minima("reel"))
    with pytest.raises(NotImplementedError, match="tarea 8"):
        producir(ruta, tmp_path / "p", tmp_path / "o")
