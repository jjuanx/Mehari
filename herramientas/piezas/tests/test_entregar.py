import json
from datetime import date

import pytest

from comprobar import ResultadoTexto
from entregar import (entregar, generar_cola, generar_revision, generar_texto,
                      modo_metricool, motivos_no_lista)

VACIO = ResultadoTexto([], [], [])
HOY = date(2026, 11, 6)


def test_lista_sin_caras_y_sin_pendientes(pieza_minima):
    p = pieza_minima("deslizar") | {"hay_caras": False, "permiso_caras": "pendiente"}
    assert motivos_no_lista(p, VACIO) == []


def test_caras_sin_permiso_no_se_publica(pieza_minima):
    p = pieza_minima("deslizar") | {"hay_caras": True, "permiso_caras": "pendiente"}
    assert motivos_no_lista(p, VACIO) == ["falta permiso de caras"]


def test_pendientes_y_avisos_de_difuminado_son_motivos(pieza_minima):
    p = pieza_minima("deslizar") | {"pendientes": ["[ASÍ]"]}
    m = motivos_no_lista(p, ResultadoTexto([], [], ["[X]"]), ["01: se pierde la matrícula"])
    assert m[0].startswith("datos pendientes: ") and "[X]" in m[0] and "[ASÍ]" in m[0]
    assert m[1] == "difuminado por revisar: 01: se pierde la matrícula"


def test_modos(pieza_minima):
    assert modo_metricool(pieza_minima("reel") | {"musica": {"ruta": "m.mp3", "licencia": "x"}}) == "automatico"
    assert modo_metricool(pieza_minima("reel") | {"musica": None}) == "aviso"
    assert modo_metricool(pieza_minima("historia")) == "aviso"
    assert modo_metricool(pieza_minima("deslizar")) == "automatico"


def test_cola_sigue_el_formato_de_metricool(pieza_minima):
    c = generar_cola(pieza_minima("deslizar"), "2026-11-06_deslizar_las-cestas", ["01.jpg", "02.jpg"])
    pub = c["publicaciones"][0]
    assert c["aprobacion"]["estado"] == "pendiente" and c["zona_horaria"] == "Europe/Madrid"
    assert pub["fecha"] is None and pub["tipo"] == "carrusel" and pub["medios"] == ["01.jpg", "02.jpg"]
    assert "portada" not in pub and pub["id"] == "2026-11-06_deslizar_las-cestas"
    assert list(pub)[:7] == ["id", "fecha", "red", "tipo", "modo", "ficha", "medios"]


def test_cola_historias_una_por_fichero_y_reel_con_portada(pieza_minima):
    c = generar_cola(pieza_minima("historia"), "d", ["a.jpg", "b.jpg"])
    assert [x["id"] for x in c["publicaciones"]] == ["d-01", "d-02"]
    assert [x["tipo"] for x in c["publicaciones"]] == ["story", "story"]
    c = generar_cola(pieza_minima("reel"), "d", ["reel.mp4", "portada.jpg"])
    pub = c["publicaciones"][0]
    assert pub["medios"] == ["reel.mp4"] and pub["portada"] == "portada.jpg"


def test_texto_estado_y_copy(pieza_minima):
    p = pieza_minima("deslizar") | {"a_mano_despues": ["Etiquetar"]}
    t = generar_texto(p, [])
    assert t.startswith("Estado: LISTA\n\n") and t.endswith("\n") and "Música: sin música" in t
    assert "- Etiquetar" in t
    assert generar_texto(p, ["a", "b"]).startswith("Estado: NO PUBLICAR · a; b\n")


def test_no_sobrescribe_y_marca_pendiente(tmp_path, entrega_preparada):
    a = entregar(*entrega_preparada(pendiente=True), produccion=tmp_path, hoy=HOY)
    b = entregar(*entrega_preparada(pendiente=True), produccion=tmp_path, hoy=HOY)
    assert a.name == "2026-11-06_deslizar_las-cestas_PENDIENTE" and b.name.endswith("_PENDIENTE-2")
    assert (a / "texto.txt").read_text().startswith("Estado: NO PUBLICAR")
    assert a.parent == tmp_path / "2026-10-24_la-posadilla"


def test_entrega_completa_lista(tmp_path, entrega_preparada):
    d = entregar(*entrega_preparada(), produccion=tmp_path, hoy=HOY)
    assert d.name == "2026-11-06_deslizar_las-cestas"
    for n in ("01.jpg", "02.jpg", "texto.txt", "revision.html", "cola-metricool.json",
              "pieza.json", "revision/01_antes.jpg", "revision/01_despues.jpg"):
        assert (d / n).is_file(), n
    cola = json.loads((d / "cola-metricool.json").read_text(encoding="utf-8"))
    assert cola["publicaciones"][0]["ubicacion"] == "Finca La Posadilla"
    assert cola["publicaciones"][0]["a_mano_despues"] == ["Etiquetar a la finca"]
    h = (d / "revision.html").read_text(encoding="utf-8")
    assert "LISTA" in h and 'src="revision/01_antes.jpg"' in h and "funda de rueda" in h


def test_avisos_de_difuminado_bloquean_y_salen_en_la_revision(tmp_path, entrega_preparada):
    d = entregar(*entrega_preparada(avisos=["01: se pierde el seguimiento <matrícula>"]),
                 produccion=tmp_path, hoy=HOY)
    assert d.name.endswith("_PENDIENTE")
    h = (d / "revision.html").read_text(encoding="utf-8")
    assert "NO PUBLICAR" in h and "&lt;matrícula&gt;" in h


def test_se_niega_con_errores_de_texto_o_medios(tmp_path, entrega_preparada):
    ruta, salidas, proyecto = entrega_preparada()
    p = json.loads(ruta.read_text(encoding="utf-8"))
    p["texto"] = "Un Citroën. 625 06 42 93"
    ruta.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        entregar(ruta, salidas, proyecto, tmp_path / "prod", HOY)
    assert "Citroën" in str(e.value) and not (tmp_path / "prod").exists()
    ruta, salidas, proyecto = entrega_preparada()
    with pytest.raises(SystemExit):
        entregar(ruta, salidas[:1], proyecto, tmp_path / "prod", HOY)


def test_reel_sin_mp4_se_rechaza(tmp_path, pieza_minima):
    from PIL import Image
    from ayudas import escribir
    carpeta = tmp_path / "r"
    carpeta.mkdir()
    ruta = escribir(carpeta, pieza_minima("reel"))
    portada = carpeta / "portada.jpg"
    Image.new("RGB", (1080, 1920)).save(portada)
    with pytest.raises(SystemExit) as e:
        entregar(ruta, [portada], carpeta / "proyecto", tmp_path / "prod", HOY)
    assert "mp4" in str(e.value)


def test_revision_escapa_el_texto(pieza_minima):
    p = pieza_minima("deslizar")
    p["texto"] = 'Boda <script>alert(1)</script> & "finca"'
    p["elementos"][0]["revision_marca"] = "<b>x</b>"
    h = generar_revision(p, ["a<b>.jpg"], [("revision/01_antes.jpg", "revision/01_despues.jpg")],
                         ResultadoTexto([], ["<i>aviso</i>"], []), ["<u>m</u>"])
    assert "<script>alert" not in h and "<b>x</b>" not in h and "<i>aviso" not in h
    assert "&lt;script&gt;" in h and "http" not in h


def test_cli_sin_drive_da_mensaje_claro(tmp_path, monkeypatch, pieza_minima):
    import entregar as m
    monkeypatch.setattr(m, "raiz_drive", lambda *a, **k: None)
    with pytest.raises(SystemExit) as e:
        m.main(["p.json", "proy", str(tmp_path)])
    assert "--produccion" in str(e.value) and "MEHARI_DRIVE" in str(e.value)
