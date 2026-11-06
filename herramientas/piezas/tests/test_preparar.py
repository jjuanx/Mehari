import shutil
import subprocess

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont
from ayudas import ffprobe_dur, ffprobe_wh
from preparar import avisos_de_difuminar, preparar


def test_ruta_con_espacios_y_dos_puntos(tmp_path, foto_jpg, pieza_minima):
    boda = tmp_path / "My Drive/Boda 24:10:2026"
    boda.mkdir(parents=True)
    shutil.copy(foto_jpg, boda / "IMG 1.jpg")
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": "IMG 1.jpg"}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    with Image.open(salida) as im:
        assert abs(im.width / im.height - 9 / 16) < 0.01


def test_orientacion_exif_y_recorte_en_coordenadas_vistas(tmp_path, foto_rotada, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(foto_rotada, boda / "r.jpg")
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": "r.jpg",
                       "recorte": {"x": 0, "y": 0, "ancho": 3024, "alto": 2000}}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    with Image.open(salida) as im:
        assert im.size == (3024, 2000)
    # El rectángulo rojo (300,400)-(900,1000) del original girado 90° a la derecha
    # queda, tal como se ve, en x 2024-2624, y 300-900.
    with Image.open(salida) as im:
        assert im.getpixel((2300, 600))[0] > 150 and im.getpixel((2300, 600))[1] < 80
        assert im.getpixel((600, 700))[1] > 200


def test_retoque_genera_antes_y_despues(tmp_path, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    img = Image.new("RGB", (3024, 4032), (120, 120, 120))
    d = ImageDraw.Draw(img)
    d.rectangle([1000, 2000, 1400, 2100], fill=(255, 255, 255))
    d.text((1020, 2020), "1234 BCD", fill=(0, 0, 0), font=ImageFont.load_default(size=60))
    img.save(boda / "f.jpg", quality=95)

    def oscuros(im):
        recorte = im.convert("L").crop((1005, 2005, 1395, 2095))
        return int((np.asarray(recorte) < 80).sum())

    assert oscuros(img) > 500
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": "f.jpg",
                       "retoques": [{"tipo": "placa",
                                     "poligono": [[1005, 2005], [1395, 2005], [1395, 2095], [1005, 2095]]}]}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    antes = tmp_path / "proy/revision/01_antes.jpg"
    despues = tmp_path / "proy/revision/01_despues.jpg"
    assert antes.exists() and despues.exists()
    with Image.open(antes) as im:
        assert max(im.size) == 800
    with Image.open(despues) as im:
        assert max(im.size) == 800
    # El recorte 9:16 centrado conserva la placa: en el asset, las letras han desaparecido.
    with Image.open(boda / "f.jpg") as o, Image.open(salida) as s:
        ancho_recorte = s.width
        x0 = (o.width - ancho_recorte) // 2
        zona = s.convert("L").crop((1005 - x0, 2005, 1395 - x0, 2095))
        assert int((np.asarray(zona) < 80).sum()) < 50
    assert not (tmp_path / "proy/_tmp").exists()
    assert not list(boda.glob("*.png"))


def test_video_rotado_sale_vertical(tmp_path, clip_rotado, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(clip_rotado, boda / "v.mp4")
    p = pieza_minima("historia")
    p["variante"] = "clip-cta"
    p["elementos"] = [{"orden": 1, "fichero": "v.mp4", "desde": 1, "hasta": 4}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    assert salida.suffix == ".mp4"
    assert ffprobe_wh(salida) == (1080, 1920) and abs(ffprobe_dur(salida) - 3) < 0.1


def test_video_con_zona_y_recorte_genera_revision(tmp_path, clip_mp4, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(clip_mp4, boda / "v.mp4")
    p = pieza_minima("historia")
    p["variante"] = "clip-cta"
    p["elementos"] = [{"orden": 1, "fichero": "v.mp4", "desde": 1, "hasta": 4,
                       "recorte": {"x": 0, "y": 0, "ancho": 1080, "alto": 1080},
                       "retoques": [{"tipo": "zona", "t": 2, "caja": [100, 100, 200, 100]}]}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    assert ffprobe_wh(salida) == (1080, 1920)
    assert (tmp_path / "proy/revision/01_antes.jpg").exists()
    assert (tmp_path / "proy/revision/01_despues.jpg").exists()
    assert (tmp_path / "proy/revision/avisos.json").read_text(encoding="utf-8").strip() == "[]"


def test_orden_repetido_falla_antes_de_trabajar(tmp_path, pieza_minima):
    p = pieza_minima("deslizar")
    p["elementos"][1]["orden"] = 1
    with pytest.raises(ValueError):
        preparar(p, tmp_path / "b", tmp_path / "proy")
    assert not (tmp_path / "proy").exists()


def test_deslizar_sin_recorte_sale_3_4(tmp_path, foto_jpg, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    Image.new("RGB", (4000, 3000), (200, 200, 200)).save(boda / "base.jpg")
    p = pieza_minima("deslizar")
    for i, e in enumerate(p["elementos"]):
        shutil.copy(boda / "base.jpg", boda / f"IMG_{i + 1}.jpg")
        e["fichero"] = f"IMG_{i + 1}.jpg"
    salidas = preparar(p, boda, tmp_path / "proy")
    assert [s.name for s in salidas] == ["01.jpg", "02.jpg", "03.jpg", "04.jpg", "05.jpg"]
    with Image.open(salidas[0]) as im:
        assert im.size == (2250, 3000)


def test_parser_de_avisos_de_difuminar():
    salida = ("Zona 1.000,10,10,50,50: peor parecido 0.31  << REVISAR\n"
              "Zona 2.000,10,10,50,50: peor parecido 0.90\n")
    avisos = avisos_de_difuminar(salida, "03", "v.mov")
    assert len(avisos) == 1 and "03" in avisos[0] and "v.mov" in avisos[0] and "0.31" in avisos[0]
    assert avisos_de_difuminar("Zona x: peor parecido 0.90\n", "03", "v.mov") == []


def test_zona_fuera_del_corte_falla_antes_de_trabajar(tmp_path, clip_mp4, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(clip_mp4, boda / "v.mp4")
    p = pieza_minima("historia")
    p["variante"] = "clip-cta"
    p["elementos"] = [{"orden": 1, "fichero": "v.mp4", "desde": 1, "hasta": 4,
                       "retoques": [{"tipo": "zona", "t": 4.5, "caja": [100, 100, 200, 100]}]}]
    with pytest.raises(ValueError, match="t=4.5"):
        preparar(p, boda, tmp_path / "proy")
    assert not (tmp_path / "proy").exists()


@pytest.mark.parametrize("recorte", [
    {"x": -1, "y": 0, "ancho": 100, "alto": 100},
    {"x": 0, "y": 0, "ancho": 0, "alto": 100},
    {"x": 3000, "y": 0, "ancho": 100, "alto": 100},
])
def test_recorte_invalido_falla(tmp_path, foto_jpg, pieza_minima, recorte):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(foto_jpg, boda / "f.jpg")
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": "f.jpg", "recorte": recorte}]
    with pytest.raises(ValueError, match="recorte"):
        preparar(p, boda, tmp_path / "proy")


def test_despues_de_foto_con_recorte_no_9_16_muestra_el_encuadre_9_16(tmp_path, foto_jpg, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(foto_jpg, boda / "f.jpg")
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": "f.jpg",
                       "recorte": {"x": 0, "y": 0, "ancho": 3000, "alto": 2000}}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    with Image.open(salida) as im:
        assert im.size == (3000, 2000)
    with Image.open(tmp_path / "proy/revision/01_despues.jpg") as im:
        assert abs(im.width / im.height - 9 / 16) < 0.01 and max(im.size) == 800


def _energia(im: Image.Image, caja) -> float:
    x0, y0, x1, y1 = caja
    a = np.asarray(im.convert("L").crop((x0, y0, x1, y1)), dtype=float)
    return float(np.abs(np.diff(a, axis=1)).mean())


def _frame(video, t, destino):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(video),
                    "-frames:v", "1", str(destino)], check=True)
    return Image.open(destino).convert("RGB")


def test_zona_en_clip_rotado_con_recorte_se_difumina_donde_toca(tmp_path, pieza_minima):
    # Fuente 1920x1080 con ruido y, en el centro, un tablero amarillo y azul; rotación 90.
    rng = np.random.default_rng(3)
    base = rng.integers(0, 255, (1080, 1920, 3), dtype=np.uint8)
    yy, xx = np.mgrid[860:1060, 440:640]
    celdas = ((yy // 20 + xx // 20) % 2 == 0)
    base[440:640, 860:1060] = np.where(celdas[..., None], (255, 255, 0), (0, 0, 255)).astype(np.uint8)
    png, plano, rotado = tmp_path / "s.png", tmp_path / "plano.mp4", tmp_path / "v.mp4"
    Image.fromarray(base).save(png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", str(png),
                    "-t", "3", "-pix_fmt", "yuv420p", "-crf", "10", str(plano)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-display_rotation", "90", "-i", str(plano),
                    "-c", "copy", str(rotado)], check=True)
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(rotado, boda / "v.mp4")

    # Posición del tablero tal como se ve (1080x1920): máscara amarilla en un fotograma.
    vista = np.asarray(_frame(boda / "v.mp4", 1, tmp_path / "vista.png")).astype(int)
    assert vista.shape[:2] == (1920, 1080)
    amarillo = (vista[..., 0] > 200) & (vista[..., 1] > 200) & (vista[..., 2] < 80)
    ys, xs = np.where(amarillo)
    caja = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min()), int(ys.max() - ys.min())]

    recorte = {"x": 90, "y": 100, "ancho": 900, "alto": 1600}
    resultados = {}
    for nombre, retoques in (("sin", []), ("con", [{"tipo": "zona", "t": 1, "caja": caja}])):
        p = pieza_minima("historia")
        p["variante"] = "clip-cta"
        p["elementos"] = [{"orden": 1, "fichero": "v.mp4", "desde": 0, "hasta": 3,
                           "recorte": recorte, "retoques": retoques}]
        [salida] = preparar(p, boda, tmp_path / nombre)
        resultados[nombre] = _frame(salida, 1.5, tmp_path / f"{nombre}.png")

    # Caja transformada: el recorte 900x1600 ya es 9:16; escala 1.2.
    s = 1080 / 900
    destino = (round((caja[0] - 90) * s), round((caja[1] - 100) * s),
               round((caja[0] + caja[2] - 90) * s), round((caja[1] + caja[3] - 100) * s))
    assert _energia(resultados["sin"], destino) > 20
    assert _energia(resultados["con"], destino) < 0.4 * _energia(resultados["sin"], destino)


# ---------------------------------------------------------------- retoques desconocidos (C1) y zonas fuera (M1)

def test_tipo_de_retoque_desconocido_no_se_salta():
    from preparar import _argumentos_retoque
    with pytest.raises(ValueError, match="matricula"):
        _argumentos_retoque([{"tipo": "matricula", "poligono": [[0, 0], [1, 0], [1, 1], [0, 1]]}])


@pytest.mark.parametrize("fichero,retoque", [
    ("v.mp4", {"tipo": "placa", "poligono": [[0, 0], [9, 0], [9, 9], [0, 9]]}),
    ("f.jpg", {"tipo": "zona", "t": 1, "caja": [0, 0, 10, 10]}),
    ("f.jpg", {"tipo": "Placa", "poligono": [[0, 0], [9, 0], [9, 9], [0, 9]]}),
])
def test_retoque_que_no_encaja_con_el_fichero_falla_antes_de_trabajar(tmp_path, foto_jpg, clip_mp4,
                                                                      pieza_minima, fichero, retoque):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(clip_mp4 if fichero.endswith(".mp4") else foto_jpg, boda / fichero)
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": fichero, "retoques": [retoque]}]
    with pytest.raises(ValueError, match="retoque"):
        preparar(p, boda, tmp_path / "proy")
    assert not (tmp_path / "proy/assets/material").exists()


def test_zonas_finales_separa_las_que_quedan_fuera_del_encuadre():
    from preparar import _zonas_finales
    dentro = {"tipo": "zona", "t": 2, "caja": [100, 100, 200, 100]}
    fuera = {"tipo": "zona", "t": 2, "caja": [100, 1500, 200, 100]}
    args, descartadas = _zonas_finales([dentro, fuera], 1, 4, (0, 0, 1080, 1080))
    assert len(args) == 1 and args[0].startswith("1.000,")
    assert descartadas == [fuera]


def test_zona_fuera_del_encuadre_deja_aviso(tmp_path, clip_mp4, pieza_minima):
    import json
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(clip_mp4, boda / "v.mp4")
    p = pieza_minima("historia")
    p["variante"] = "clip-cta"
    p["elementos"] = [{"orden": 1, "fichero": "v.mp4", "desde": 1, "hasta": 3,
                       "recorte": {"x": 0, "y": 0, "ancho": 1080, "alto": 1080},
                       "retoques": [{"tipo": "zona", "t": 2, "caja": [100, 1500, 200, 100]}]}]
    preparar(p, boda, tmp_path / "proy")
    avisos = json.loads((tmp_path / "proy/revision/avisos.json").read_text(encoding="utf-8"))
    assert len(avisos) == 1 and "01" in avisos[0] and "fuera del encuadre" in avisos[0]


# ---------------------------------------------------------------- material desfasado (I1)

def test_preparar_vacia_lo_anterior_y_deja_la_huella(tmp_path, foto_jpg, pieza_minima):
    import json
    from pieza import huella_material
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(foto_jpg, boda / "f.jpg")
    proy = tmp_path / "proy"
    for viejo in ("assets/material/09.jpg", "revision/07_antes.jpg", "revision/07_despues.jpg"):
        (proy / viejo).parent.mkdir(parents=True, exist_ok=True)
        (proy / viejo).write_bytes(b"viejo")
    (proy / "revision/avisos.json").write_text('["viejo"]', encoding="utf-8")
    (proy / "index.html").write_text("plantilla", encoding="utf-8")
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": "f.jpg"}]
    preparar(p, boda, proy)
    assert sorted(f.name for f in (proy / "assets/material").iterdir()) == ["01.jpg"]
    assert sorted(f.name for f in (proy / "revision").iterdir()) == ["avisos.json", "preparado.json"]
    assert json.loads((proy / "revision/avisos.json").read_text(encoding="utf-8")) == []
    assert json.loads((proy / "revision/preparado.json").read_text(encoding="utf-8")) == {
        "huella": huella_material(p)}
    assert (proy / "index.html").read_text(encoding="utf-8") == "plantilla"   # solo material y revisión


def test_si_preparar_falla_no_queda_material_anterior_valido(tmp_path, foto_jpg, pieza_minima):
    boda = tmp_path / "b"
    boda.mkdir()
    shutil.copy(foto_jpg, boda / "f.jpg")
    proy = tmp_path / "proy"
    p = pieza_minima("historia")
    p["elementos"] = [{"orden": 1, "fichero": "f.jpg"}]
    preparar(p, boda, proy)
    p["elementos"][0]["recorte"] = {"x": 0, "y": 0, "ancho": 99999, "alto": 10}
    with pytest.raises(ValueError):
        preparar(p, boda, proy)
    assert not (proy / "revision/preparado.json").exists()
    assert not (proy / "revision/avisos.json").exists()
    assert not any((proy / "assets/material").glob("*"))


def test_sondear_descuenta_el_recorte_de_los_live_photos(monkeypatch):
    # Los Live Photos del iPhone traen FrameCropping: FFmpeg lo aplica al decodificar,
    # así que el fotograma real (y la rejilla) mide 1308×1744, no 1440×1920.
    import json
    import types
    import preparar as mod
    sonda = {"streams": [{"width": 1920, "height": 1440, "side_data_list": [
        {"side_data_type": "Frame Cropping", "crop_top": 66, "crop_bottom": 66,
         "crop_left": 88, "crop_right": 88},
        {"side_data_type": "Display Matrix", "rotation": -90}]}],
        "format": {"duration": "2.866667"}}
    monkeypatch.setattr(mod, "_ejecutar", lambda cmd: types.SimpleNamespace(stdout=json.dumps(sonda)))
    datos = mod.sondear("x.mov")
    assert (datos["ancho"], datos["alto"]) == (1308, 1744)


def test_sin_zscale_el_error_dice_que_instalar(monkeypatch):
    import types
    import preparar as mod
    sin = " ... colorspace        V->V       Convert between colorspaces.\n .S tonemap           V->V       x\n"
    monkeypatch.setattr(mod, "_ejecutar", lambda cmd: types.SimpleNamespace(stdout=sin))
    with pytest.raises(RuntimeError, match="ffmpeg-full"):
        mod._exigir_zscale()
    con = sin + " .. zscale            V->V       Apply resizing, colorspace and bit depth conversion.\n"
    monkeypatch.setattr(mod, "_ejecutar", lambda cmd: types.SimpleNamespace(stdout=con))
    mod._exigir_zscale()
