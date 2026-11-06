"""Prepara el material elegido en pieza.json: convierte, retoca, recorta y deja cada
elemento listo para el render.

Uso:
    python3 herramientas/piezas/preparar.py <pieza.json> "<carpeta boda>" <proyecto>

Salida (dentro de <proyecto>):
    assets/material/NN.jpg | NN.mp4   un fichero por elemento (NN = orden con dos cifras)
    revision/NN_antes.jpg, NN_despues.jpg   solo en elementos con recorte o retoques (800 px)

Las coordenadas de recorte y retoque se refieren al original tal como se ve (con la
orientación EXIF o la rotación del vídeo ya aplicada), igual que en rejilla.py.
Nunca se escribe en la carpeta de la boda.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pieza  # noqa: E402
import rutas  # noqa: E402

sys.path.insert(0, str(rutas.MATERIAL))
from comun import EXT_VIDEO  # noqa: E402,F401  (registra también pillow_heif)

LADO_REVISION = 800
ANCHO_FINAL, ALTO_FINAL = 1080, 1920
# Filtro HLG -> SDR BT.709 de la cabecera de difuminar.py
FILTRO_HLG = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
ETIQUETAS_BT709 = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]


def _ejecutar(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], check=True, capture_output=True, text=True)


def _ffmpeg(*args) -> None:
    _ejecutar(["ffmpeg", "-y", "-loglevel", "error", *args])


def _abs(ruta: Path) -> str:
    return str(Path(ruta).resolve())


# ---------------------------------------------------------------- utilidades de vídeo

def sondear(video: Path) -> dict:
    """Ancho y alto tal como se ve (con la rotación), duración y función de transferencia."""
    datos = json.loads(_ejecutar(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                  "-show_streams", "-show_format", "-of", "json",
                                  _abs(video)]).stdout)
    flujo = datos["streams"][0]
    ancho, alto = int(flujo["width"]), int(flujo["height"])
    rotacion = flujo.get("tags", {}).get("rotate")
    for lado in flujo.get("side_data_list", []):
        if "rotation" in lado:
            rotacion = lado["rotation"]
    if rotacion is not None and int(float(rotacion)) % 180 != 0:
        ancho, alto = alto, ancho
    duracion = float(datos.get("format", {}).get("duration") or flujo.get("duration") or 0)
    return {"ancho": ancho, "alto": alto, "duracion": duracion,
            "transfer": flujo.get("color_transfer")}


def _fotograma(video: Path, t: float, destino: Path, hlg: bool) -> Image.Image:
    cmd = ["-ss", f"{max(t, 0):.3f}", "-i", _abs(video), "-frames:v", "1"]
    if hlg:
        cmd += ["-vf", FILTRO_HLG]
    _ffmpeg(*cmd, _abs(destino))
    with Image.open(destino) as im:
        return im.convert("RGB")


def _caja_9_16(ancho: int, alto: int, caja: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Recorta al centro la caja (x, y, an, al) hasta 9:16 (cover), con medidas pares."""
    x, y, an, al = caja
    if an * 16 > al * 9:      # demasiado ancha
        nuevo = int(al * 9 / 16) // 2 * 2
        x += (an - nuevo) // 2
        an = nuevo
    else:                     # demasiado alta
        nuevo = int(an * 16 / 9) // 2 * 2
        y += (al - nuevo) // 2
        al = nuevo
    return x, y, an - an % 2, al - al % 2


def _caja_recorte(el: dict, ancho: int, alto: int) -> tuple[int, int, int, int]:
    r = el.get("recorte")
    if not r:
        return 0, 0, ancho, alto
    x = max(0, int(round(r["x"])))
    y = max(0, int(round(r["y"])))
    an = min(int(round(r["ancho"])), ancho - x)
    al = min(int(round(r["alto"])), alto - y)
    return x, y, an, al


def _zonas_para_corte(zonas: list, desde: float, hasta: float, id_el: str) -> list[str]:
    """Pasa las zonas (tiempos del original) a argumentos --zona (tiempos del corte)."""
    salida = []
    for z in zonas:
        t = float(z["t"])
        if not desde <= t <= hasta:
            print(f"AVISO: elemento {id_el}: la zona en t={t:g} s queda fuera del corte "
                  f"{desde:g}-{hasta:g} s y se omite", file=sys.stderr)
            continue
        x, y, an, al = (int(round(v)) for v in z["caja"])
        texto = f"{t - desde:.3f},{x},{y},{an},{al}"
        if "desde" in z or "hasta" in z:
            zd = min(max(float(z.get("desde", desde)), desde), hasta) - desde
            zh = min(max(float(z.get("hasta", hasta)), desde), hasta) - desde
            texto += f",{zd:.3f},{zh:.3f}"
        salida.append(texto)
    return salida


def _preparar_video(el: dict, origen: Path, destino: Path, tmp: Path, id_el: str,
                    revision: Path | None) -> None:
    info = sondear(origen)
    hlg = info["transfer"] == "arib-std-b67"
    desde = float(el.get("desde", 0))
    hasta = float(el.get("hasta", info["duracion"]))
    dur = hasta - desde

    # 1) HLG -> SDR (si hace falta) y corte, conservando resolución y orientación visibles
    corte = tmp / f"{id_el}_corte.mp4"
    cmd = ["-ss", f"{desde:.3f}", "-i", _abs(origen), "-t", f"{dur:.3f}", "-an"]
    if hlg:
        cmd += ["-vf", FILTRO_HLG, *ETIQUETAS_BT709]
    _ffmpeg(*cmd, "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p",
            _abs(corte))

    # 2) retoques de zona con difuminar.py (tiempos desplazados por -desde)
    zonas_orig = [r for r in el.get("retoques", []) if r.get("tipo") == "zona"]
    zonas = _zonas_para_corte(zonas_orig, desde, hasta, id_el)
    fuente = corte
    if zonas:
        difuminado = tmp / f"{id_el}_difuminado.mp4"
        cmd = [sys.executable, rutas.MATERIAL / "difuminar.py", _abs(corte), _abs(difuminado)]
        for z in zonas:
            cmd += ["--zona", z]
        _ejecutar(cmd)
        fuente = difuminado

    # 3) recorte, 9:16 cover, 1080x1920, 30 fps, H.264 CRF 15, sin audio
    ancho, alto = info["ancho"], info["alto"]
    x, y, an, al = _caja_9_16(ancho, alto, _caja_recorte(el, ancho, alto))
    _ffmpeg("-i", _abs(fuente), "-an",
            "-vf", f"crop={an}:{al}:{x}:{y},scale={ANCHO_FINAL}:{ALTO_FINAL},setsar=1",
            "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "15",
            "-pix_fmt", "yuv420p", *ETIQUETAS_BT709, _abs(destino))

    if revision is not None:
        validas = [z for z in zonas_orig if desde <= float(z["t"]) <= hasta]
        t_orig = float(validas[0]["t"]) if validas else desde + dur / 2
        t_final = t_orig - desde
        tope = max(dur - 0.05, 0)
        antes = _fotograma(origen, min(t_orig, desde + tope), tmp / f"{id_el}_antes.png", hlg)
        despues = _fotograma(destino, min(t_final, tope), tmp / f"{id_el}_despues.png", False)
        _guardar_revision(antes, despues, revision, id_el)


# ---------------------------------------------------------------- fotos

def _argumentos_retoque(retoques: list) -> list[str]:
    args = []
    for r in retoques:
        if r["tipo"] in ("placa", "funda"):
            puntos = ",".join(str(int(round(v))) for p in r["poligono"] for v in p)
            args.append(f"--{r['tipo']}={puntos}")
        elif r["tipo"] == "emblema":
            args.append("--emblema=" + ",".join(str(int(round(v))) for v in r["caja"]))
    return args


def _preparar_foto(el: dict, origen: Path, destino: Path, tmp: Path, id_el: str,
                   formato: str, revision: Path | None) -> None:
    with Image.open(origen) as im:
        original = ImageOps.exif_transpose(im).convert("RGB")
    ancho, alto = original.size

    imagen = original
    args = _argumentos_retoque(el.get("retoques", []))
    if args:
        base = tmp / f"{id_el}_base.png"
        retocada = tmp / f"{id_el}_retocada.png"
        original.save(base)  # PNG sin EXIF: cv2 y Pillow ven la misma orientación
        _ejecutar([sys.executable, rutas.MATERIAL / "retocar_foto.py",
                   _abs(base), _abs(retocada), *args])
        with Image.open(retocada) as im:
            imagen = im.convert("RGB")

    if el.get("recorte"):
        x, y, an, al = _caja_recorte(el, ancho, alto)
    else:
        prop = (3, 4) if formato == "deslizar" else (9, 16)
        an, al = ancho, alto
        if an * prop[1] > al * prop[0]:
            an = int(al * prop[0] / prop[1])
        else:
            al = int(an * prop[1] / prop[0])
        x, y = (ancho - an) // 2, (alto - al) // 2
    final = imagen.crop((x, y, x + an, y + al))
    final.save(destino, "JPEG", quality=92)

    if revision is not None:
        _guardar_revision(original, final, revision, id_el)


def _a_lado(im: Image.Image, lado: int = LADO_REVISION) -> Image.Image:
    k = lado / max(im.size)
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


def _guardar_revision(antes: Image.Image, despues: Image.Image, carpeta: Path, id_el: str) -> None:
    _a_lado(antes).save(carpeta / f"{id_el}_antes.jpg", "JPEG", quality=90)
    _a_lado(despues).save(carpeta / f"{id_el}_despues.jpg", "JPEG", quality=90)


# ---------------------------------------------------------------- principal

def preparar(p: dict, boda: Path, proyecto: Path) -> list[Path]:
    """Prepara todos los elementos de la pieza y devuelve sus ficheros, por orden."""
    elementos = sorted(p["elementos"], key=lambda e: e["orden"])
    ordenes = [e["orden"] for e in elementos]
    if len(set(ordenes)) != len(ordenes):
        repetidos = sorted({o for o in ordenes if ordenes.count(o) > 1})
        raise ValueError(f"orden repetido en elementos: {repetidos}")

    boda, proyecto = Path(boda), Path(proyecto)
    material = proyecto / "assets/material"
    revision = proyecto / "revision"
    tmp = proyecto / "_tmp"
    for carpeta in (material, revision, tmp):
        carpeta.mkdir(parents=True, exist_ok=True)

    salidas = []
    try:
        for el in elementos:
            id_el = f"{int(el['orden']):02d}"
            origen = boda / el["fichero"]
            es_video = origen.suffix.lower() in EXT_VIDEO
            destino = material / f"{id_el}{'.mp4' if es_video else '.jpg'}"
            toca = bool(el.get("recorte") or el.get("retoques"))
            rev = revision if toca else None
            if es_video:
                _preparar_video(el, origen, destino, tmp, id_el, rev)
            else:
                _preparar_foto(el, origen, destino, tmp, id_el, p["formato"], rev)
            salidas.append(destino)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return salidas


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit('Uso: python3 herramientas/piezas/preparar.py <pieza.json> "<carpeta boda>" <proyecto>')
    p = pieza.cargar_pieza(Path(sys.argv[1]))
    for f in preparar(p, Path(sys.argv[2]), Path(sys.argv[3])):
        print(f)


if __name__ == "__main__":
    main()
