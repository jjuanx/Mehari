import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from localizar import buscar_bodas, fechas_en, raiz_drive


def test_drive_por_variable_de_entorno(tmp_path):
    (tmp_path / "X").mkdir()
    assert raiz_drive({"MEHARI_DRIVE": str(tmp_path / "X")}, casa=tmp_path / "casa") == tmp_path / "X"


def test_drive_en_mac_mi_unidad(tmp_path):
    d = tmp_path / "Library/CloudStorage/GoogleDrive-a@b.com/Mi unidad/Mehari We"
    d.mkdir(parents=True)
    assert raiz_drive({}, casa=tmp_path, unidades=()) == d


def test_drive_en_windows(tmp_path):
    d = tmp_path / "G/My Drive/Mehari We"
    d.mkdir(parents=True)
    assert raiz_drive({}, casa=tmp_path / "casa", unidades=(tmp_path / "G",)) == d


def test_drive_inexistente(tmp_path):
    assert raiz_drive({}, casa=tmp_path, unidades=()) is None


def test_fechas_en_varios_formatos():
    for txt in ("2026-10-24", "24-10-2026", "boda 24:10:2026", "24/10/2026", "el 24 de octubre"):
        assert date(2026, 10, 24) in fechas_en(txt)


def test_fecha_sin_año_usa_el_año_en_curso():
    assert fechas_en("24/10", hoy=date(2027, 3, 1)) == [date(2027, 10, 24)]
    assert fechas_en("24 de setiembre", hoy=date(2027, 3, 1)) == [date(2027, 9, 24)]
    assert fechas_en("sin fecha") == []
    assert fechas_en("31/02/2026") == []


def test_busca_por_fecha_en_nombre_antiguo_y_por_lugar(drive_falso):
    assert [c.relativa for c in buscar_bodas(drive_falso, "boda del 24 de octubre")] == [
        "01_Material/Selecccion/Boda 24:10:2026"]
    assert buscar_bodas(drive_falso, "sanlúcar")[0].relativa == "01_Material/Bodas/2026-11-07_sanlucar"


def test_motivo_y_ruta(drive_falso):
    c = buscar_bodas(drive_falso, "2026-11-07")[0]
    assert c.motivo == "fecha 2026-11-07 en el nombre"
    assert c.ruta == drive_falso / "01_Material/Bodas/2026-11-07_sanlucar"
    assert buscar_bodas(drive_falso, "sanlucar")[0].motivo == "lugar «sanlucar» en el nombre"


def test_ignora_carpetas_internas(drive_falso):
    resultado = buscar_bodas(drive_falso, "")
    assert resultado
    assert not [c for c in resultado if "/_" in c.relativa]
    assert not [c for c in resultado if c.relativa.endswith(("/fotos", "/videos"))]
    assert not [c for c in resultado if "Galeria" in c.relativa]


def test_la_ultima(drive_falso):
    import os
    antigua = drive_falso / "01_Material/Selecccion/Boda 24:10:2026"
    os.utime(antigua, (1, 1))
    os.utime(antigua / "IMG_1.HEIC", (1, 1))
    r = buscar_bodas(drive_falso, "la última")
    assert len(r) == 1 and r[0].relativa != "01_Material/Selecccion/Boda 24:10:2026"


def test_sin_coincidencias(drive_falso):
    assert buscar_bodas(drive_falso, "marbella") == []


def test_cli(drive_falso):
    salida = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[1] / "localizar.py"), "sanlúcar"],
        capture_output=True, text=True, check=True, env={"MEHARI_DRIVE": str(drive_falso), "PATH": ""})
    datos = json.loads(salida.stdout)
    assert datos["drive"] == str(drive_falso)
    assert datos["candidatas"][0]["relativa"] == "01_Material/Bodas/2026-11-07_sanlucar"
