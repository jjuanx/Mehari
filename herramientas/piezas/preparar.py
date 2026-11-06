"""Prepara el material elegido en pieza.json: convierte, retoca, recorta y deja cada
elemento listo para el render.

Uso:
    python3 herramientas/piezas/preparar.py <pieza.json> "<carpeta boda>" <proyecto>

Salida (dentro de <proyecto>):
    assets/material/NN.jpg | NN.mp4   un fichero por elemento (NN = orden con dos cifras)
    revision/NN_antes.jpg, NN_despues.jpg   solo en elementos con recorte o retoques (800 px)
    revision/avisos.json   lista de avisos (difuminado dudoso, zona fuera del encuadre); [] si no hay
    revision/preparado.json   huella de pieza.json (pieza.huella_material): producir.py y
                           entregar.py se niegan si no coincide con el pieza.json que reciben

Al empezar vacía assets/material/ y revision/, para que nunca quede material de una pasada
anterior: si algo falla, no queda preparado.json y no se puede producir ni entregar.

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
from comun import EXT_VIDEO  # noqa: E402  (también registra pillow_heif)

LADO_REVISION = 800
ANCHO_FINAL, ALTO_FINAL = 1080, 1920
# Filtro HLG -> SDR BT.709 de la cabecera de difuminar.py
FILTRO_HLG = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
ETIQUETAS_BT709 = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]


def _ejecutar(cmd: list) -> subprocess.CompletedProcess:
    cmd = [str(c) for c in cmd]
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except subprocess.CalledProcessError as e:
        nombre = Path(cmd[1]).name if Path(cmd[0]).name.startswith("python") else Path(cmd[0]).name
        raise RuntimeError(f"{nombre} ha fallado (código {e.returncode}): "
                           f"{(e.stderr or '').strip()} {(e.stdout or '').strip()}".strip()) from e


def _ffmpeg(*args) -> None:
    _ejecutar(["ffmpeg", "-y", "-loglevel", "error", *args])


def _abs(ruta: Path) -> str:
    return str(Path(ruta).resolve())


def avisos_de_difuminar(salida: str, id_el: str, fichero: str) -> list[str]:
    """Una advertencia por cada línea «<< REVISAR» que imprime difuminar.py."""
    return [f"Elemento {id_el} ({fichero}): el seguimiento del difuminado puede haberse perdido "
            f"({linea.strip()}). Revisa el vídeo antes de publicar."
            for linea in salida.splitlines() if "<< REVISAR" in linea]


# ---------------------------------------------------------------- utilidades de vídeo

def sondear(video: Path) -> dict:
    """Ancho y alto tal como se ve (con el recorte del contenedor y la rotación), duración
    y función de transferencia.

    Los Live Photos del iPhone traen un recorte (FrameCropping) que FFmpeg aplica al
    decodificar: hay que descontarlo para que estas medidas coincidan con los fotogramas
    reales y con las coordenadas que enseña rejilla.py.
    """
    datos = json.loads(_ejecutar(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                  "-show_streams", "-show_format", "-of", "json",
                                  _abs(video)]).stdout)
    flujo = datos["streams"][0]
    ancho, alto = int(flujo["width"]), int(flujo["height"])
    rotacion = flujo.get("tags", {}).get("rotate")
    for lado in flujo.get("side_data_list", []):
        if "rotation" in lado:
            rotacion = lado["rotation"]
        # Se detecta por las claves: el nombre cambia («Frame Cropping», «FrameCropping»).
        if any(k in lado for k in ("crop_left", "crop_right", "crop_top", "crop_bottom")):
            ancho -= int(lado.get("crop_left", 0)) + int(lado.get("crop_right", 0))
            alto -= int(lado.get("crop_top", 0)) + int(lado.get("crop_bottom", 0))
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


def _cubrir(caja: tuple[int, int, int, int], prop: tuple[int, int]) -> tuple[int, int, int, int]:
    """Caja (x, y, an, al) centrada dentro de `caja` con la proporción prop (cover)."""
    x, y, an, al = caja
    if an * prop[1] > al * prop[0]:   # demasiado ancha
        nuevo = int(al * prop[0] / prop[1])
        return x + (an - nuevo) // 2, y, nuevo, al
    nuevo = int(an * prop[1] / prop[0])
    return x, y + (al - nuevo) // 2, an, nuevo


def _validar_recorte(el: dict, ancho: int, alto: int, id_el: str) -> tuple[int, int, int, int]:
    """Caja de recorte (o el cuadro entero) comprobada contra el tamaño visible."""
    r = el.get("recorte")
    if not r:
        return 0, 0, ancho, alto
    x, y, an, al = (int(round(r[k])) for k in ("x", "y", "ancho", "alto"))
    if x < 0 or y < 0 or an <= 0 or al <= 0 or x + an > ancho or y + al > alto:
        raise ValueError(f"Elemento {id_el} ({el['fichero']}): el recorte x={x}, y={y}, ancho={an}, "
                         f"alto={al} no cabe en la imagen visible de {ancho}x{alto}; márcalo de nuevo")
    return x, y, an, al


def _tamano_visible(origen: Path) -> tuple[int, int, float | None]:
    """Ancho y alto tal como se ven, y duración (None en las fotos)."""
    if origen.suffix.lower() in EXT_VIDEO:
        info = sondear(origen)
        return info["ancho"], info["alto"], info["duracion"]
    with Image.open(origen) as im:
        ancho, alto = im.size
        if im.getexif().get(0x0112) in (5, 6, 7, 8):
            ancho, alto = alto, ancho
    return ancho, alto, None


def _corte(el: dict, duracion: float) -> tuple[float, float]:
    return float(el.get("desde", 0)), float(el.get("hasta", duracion))


def _validar_tipos(el: dict, id_el: str) -> None:
    """Cada retoque tiene que ser de un tipo que se aplica a ese fichero: nunca se salta uno."""
    video = pieza.es_video(el["fichero"])
    admitidos = pieza.RETOQUES_VIDEO if video else pieza.RETOQUES_FOTO
    for r in el.get("retoques", []):
        tipo = r.get("tipo") if isinstance(r, dict) else r
        if tipo not in admitidos:
            raise ValueError(f"Elemento {id_el} ({el['fichero']}): el retoque de tipo {tipo!r} no se puede "
                             f"aplicar a un {'vídeo' if video else 'foto'} (admite {', '.join(admitidos)})")


def _validar(elementos: list, boda: Path) -> None:
    """Comprueba retoques, recortes y zonas contra los ficheros reales antes de procesar nada."""
    for el in elementos:
        _validar_tipos(el, f"{int(el['orden']):02d}")
    for el in elementos:
        retoques = el.get("retoques", [])
        if not el.get("recorte") and not any(r.get("tipo") == "zona" for r in retoques):
            continue
        id_el = f"{int(el['orden']):02d}"
        ancho, alto, duracion = _tamano_visible(boda / el["fichero"])
        _validar_recorte(el, ancho, alto, id_el)
        if duracion is None:
            continue
        desde, hasta = _corte(el, duracion)
        for z in retoques:
            if z.get("tipo") == "zona" and not desde <= float(z["t"]) <= hasta:
                raise ValueError(
                    f"Elemento {id_el} ({el['fichero']}): la zona en t={float(z['t']):g} s queda "
                    f"fuera del corte {desde:g}-{hasta:g} s; vuelve a marcarla dentro del corte")


def _zonas_finales(zonas: list, desde: float, hasta: float,
                   caja: tuple[int, int, int, int]) -> tuple[list[str], list[dict]]:
    """Argumentos --zona para el vídeo ya recortado y escalado a 1080x1920, y zonas descartadas.

    Los tiempos pasan a ser relativos al corte y las cajas, del original visible al
    espacio de salida. Una zona parcial se recorta; una que queda fuera del encuadre se
    descarta y se devuelve aparte para avisar (puede ser una caja mal marcada).
    """
    cx, cy, can, cal = caja
    sx, sy = ANCHO_FINAL / can, ALTO_FINAL / cal
    salida, descartadas = [], []
    for z in zonas:
        x, y, an, al = z["caja"]
        x0, y0 = max(0, round((x - cx) * sx)), max(0, round((y - cy) * sy))
        x1 = min(ANCHO_FINAL, round((x + an - cx) * sx))
        y1 = min(ALTO_FINAL, round((y + al - cy) * sy))
        if x1 <= x0 or y1 <= y0:
            descartadas.append(z)
            continue
        texto = f"{float(z['t']) - desde:.3f},{x0},{y0},{x1 - x0},{y1 - y0}"
        if "desde" in z or "hasta" in z:
            zd = min(max(float(z.get("desde", desde)), desde), hasta) - desde
            zh = min(max(float(z.get("hasta", hasta)), desde), hasta) - desde
            texto += f",{zd:.3f},{zh:.3f}"
        salida.append(texto)
    return salida, descartadas


def _preparar_video(el: dict, origen: Path, destino: Path, tmp: Path, id_el: str,
                    revision: Path | None) -> list[str]:
    info = sondear(origen)
    hlg = info["transfer"] == "arib-std-b67"
    desde, hasta = _corte(el, info["duracion"])
    dur = hasta - desde
    ancho, alto = info["ancho"], info["alto"]

    # Encuadre: recorte pedido y, dentro de él, 9:16 centrado (cover); medidas pares
    x, y, an, al = _cubrir(_validar_recorte(el, ancho, alto, id_el), (9, 16))
    caja = (x, y, an // 2 * 2, al // 2 * 2)
    x, y, an, al = caja

    # 1) HLG -> SDR (si hace falta), corte, recorte y escala a 1080x1920 a 30 fps.
    #    Se hace antes de difuminar.py, que guarda todos los fotogramas en memoria.
    filtros = ([FILTRO_HLG] if hlg else []) + [
        f"crop={an}:{al}:{x}:{y}", f"scale={ANCHO_FINAL}:{ALTO_FINAL}:flags=lanczos",
        "setsar=1", "fps=30"]
    intermedio = tmp / f"{id_el}_intermedio.mp4"
    _ffmpeg("-ss", f"{desde:.3f}", "-i", _abs(origen), "-t", f"{dur:.3f}", "-an",
            "-vf", ",".join(filtros), "-c:v", "libx264", "-preset", "fast", "-crf", "12",
            "-pix_fmt", "yuv420p", *ETIQUETAS_BT709, _abs(intermedio))

    # 2) retoques de zona con difuminar.py, ya en el espacio de salida
    zonas_orig = [r for r in el.get("retoques", []) if r.get("tipo") == "zona"]
    zonas, descartadas = _zonas_finales(zonas_orig, desde, hasta, caja)
    fuente = intermedio
    avisos = [f"Elemento {id_el} ({el['fichero']}): la zona en t={float(z['t']):g} s con caja "
              f"{z['caja']} queda fuera del encuadre final y no se ha difuminado. Comprueba que "
              f"está bien marcada y que lo que tapaba no sale en el vídeo." for z in descartadas]
    if zonas:
        difuminado = tmp / f"{id_el}_difuminado.mp4"
        radio = max(8, round(60 * ANCHO_FINAL / an))
        cmd = [sys.executable, rutas.MATERIAL / "difuminar.py", _abs(intermedio), _abs(difuminado),
               "--radio", radio]
        for z in zonas:
            cmd += ["--zona", z]
        avisos += avisos_de_difuminar(_ejecutar(cmd).stdout, id_el, el["fichero"])
        fuente = difuminado

    # 3) codificación final: H.264 CRF 15, 30 fps, sin audio
    _ffmpeg("-i", _abs(fuente), "-an", "-r", "30", "-c:v", "libx264", "-preset", "slow",
            "-crf", "15", "-pix_fmt", "yuv420p", *ETIQUETAS_BT709, _abs(destino))

    if revision is not None:
        t_orig = float(zonas_orig[0]["t"]) if zonas_orig else desde + dur / 2
        t_final = t_orig - desde
        tope = max(dur - 0.05, 0)
        antes = _fotograma(origen, min(t_orig, desde + tope), tmp / f"{id_el}_antes.png", hlg)
        despues = _fotograma(destino, min(t_final, tope), tmp / f"{id_el}_despues.png", False)
        _guardar_revision(antes, despues, revision, id_el)
    return avisos


# ---------------------------------------------------------------- fotos

def _argumentos_retoque(retoques: list) -> list[str]:
    args = []
    for r in retoques:
        if r["tipo"] in ("placa", "funda"):
            puntos = ",".join(str(int(round(v))) for p in r["poligono"] for v in p)
            args.append(f"--{r['tipo']}={puntos}")
        elif r["tipo"] == "emblema":
            args.append("--emblema=" + ",".join(str(int(round(v))) for v in r["caja"]))
        else:
            raise ValueError(f"retoque de foto de tipo desconocido: {r['tipo']!r}")
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

    prop = (3, 4) if formato == "deslizar" else (9, 16)
    caja = _validar_recorte(el, ancho, alto, id_el)
    if not el.get("recorte"):
        caja = _cubrir(caja, prop)
    x, y, an, al = caja
    final = imagen.crop((x, y, x + an, y + al))
    final.save(destino, "JPEG", quality=92)

    if revision is not None:
        vista = final
        if formato != "deslizar" and abs(an / al - 9 / 16) > 0.005:
            # lo que verá la plantilla: 9:16 centrado dentro del recorte
            cx, cy, can, cal = _cubrir((0, 0, an, al), prop)
            vista = final.crop((cx, cy, cx + can, cy + cal))
        _guardar_revision(original, vista, revision, id_el)


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
    for carpeta in (material, revision):   # nada de una pasada anterior
        shutil.rmtree(carpeta, ignore_errors=True)
        if carpeta.exists():
            raise RuntimeError(f"no se puede vaciar {carpeta}; ciérralo en otros programas y repite")
    _validar(elementos, boda)
    for carpeta in (material, revision, tmp):
        carpeta.mkdir(parents=True, exist_ok=True)

    salidas, avisos = [], []
    try:
        for el in elementos:
            id_el = f"{int(el['orden']):02d}"
            origen = boda / el["fichero"]
            es_video = origen.suffix.lower() in EXT_VIDEO
            destino = material / f"{id_el}{'.mp4' if es_video else '.jpg'}"
            toca = bool(el.get("recorte") or el.get("retoques"))
            rev = revision if toca else None
            if es_video:
                avisos += _preparar_video(el, origen, destino, tmp, id_el, rev)
            else:
                _preparar_foto(el, origen, destino, tmp, id_el, p["formato"], rev)
            salidas.append(destino)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    (revision / "avisos.json").write_text(json.dumps(avisos, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    (proyecto / pieza.PREPARADO).write_text(json.dumps({"huella": pieza.huella_material(p)}),
                                            encoding="utf-8")
    for aviso in avisos:
        print(f"AVISO: {aviso}", file=sys.stderr)
    return salidas


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit('Uso: python3 herramientas/piezas/preparar.py <pieza.json> "<carpeta boda>" <proyecto>')
    p = pieza.cargar_pieza(Path(sys.argv[1]))
    for f in preparar(p, Path(sys.argv[2]), Path(sys.argv[3])):
        print(f)


if __name__ == "__main__":
    main()
