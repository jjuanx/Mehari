"""Paso 4. Asigna un código a cada fichero y genera hojas de contacto para que Claude las clasifique.

- Fotos: F0001, F0002… ordenadas por fecha EXIF. Hojas de 5x5 miniaturas con el número grande
  (_analisis/hojas/fotos_001.jpg…).
- Vídeos: V001, V002… Cuatro fotogramas por vídeo (10 %, 37 %, 63 % y 90 %), seis vídeos por hoja
  (_analisis/hojas/videos_01.jpg…).
- Guarda los códigos en _analisis/ids_fotos.json e ids_videos.json. Si ya existen, NO los cambia
  (así no se desordena una clasificación hecha); para numerar de nuevo hay que borrarlos.

Uso: python 4_hojas_contacto.py "<carpeta de material>"
"""
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont

from comun import EXT_FOTO, EXT_VIDEO, carpeta_raiz, ficheros_sueltos, leer_analisis, nombre_miniatura


def fuente(tam):
    for f in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def ids(ruta, ficheros, prefijo, digitos, clave):
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    orden = sorted(ficheros, key=clave)
    asignados = {f"{prefijo}{i + 1:0{digitos}d}": f for i, f in enumerate(orden)}
    ruta.write_text(json.dumps(asignados, indent=0, ensure_ascii=False), encoding="utf-8")
    return asignados


def main():
    raiz = carpeta_raiz()
    datos = leer_analisis(raiz)
    analisis = raiz / "_analisis"
    hojas = analisis / "hojas"
    vframes = analisis / "vframes"
    hojas.mkdir(exist_ok=True)
    vframes.mkdir(exist_ok=True)
    f22 = fuente(22)

    fotos = [f for f in ficheros_sueltos(raiz, EXT_FOTO) if f in datos and "error" not in datos[f]]
    idf = ids(analisis / "ids_fotos.json", fotos, "F", 4, lambda f: (datos[f].get("date") or "9999", f))
    lado, cols = 310, 5
    items = list(idf.items())
    for p in range(0, len(items), 25):
        hoja = Image.new("RGB", (lado * cols, lado * 5), "white")
        d = ImageDraw.Draw(hoja)
        for k, (codigo, f) in enumerate(items[p:p + 25]):
            m = analisis / "thumbs" / nombre_miniatura(f)
            if not m.exists():
                continue
            t = Image.open(m)
            t.thumbnail((lado - 6, lado - 6))
            x, y = (k % cols) * lado, (k // cols) * lado
            hoja.paste(t, (x, y))
            d.rectangle([x, y, x + 78, y + 28], fill="black")
            d.text((x + 4, y + 2), codigo[1:], fill="yellow", font=f22)
        hoja.save(hojas / f"fotos_{p // 25 + 1:03d}.jpg", quality=82)

    videos = [v for v in ficheros_sueltos(raiz, EXT_VIDEO) if v in datos and "error" not in datos[v]]
    idv = ids(analisis / "ids_videos.json", videos, "V", 3, lambda v: (datos[v].get("date") or "", v))
    for codigo, v in idv.items():
        dur = datos[v]["dur"]
        for k, pos in enumerate((0.1, 0.37, 0.63, 0.9)):
            salida = vframes / f"{codigo}_{k}.jpg"
            if not salida.exists():
                subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{dur * pos:.2f}", "-i", str(raiz / v),
                                "-frames:v", "1", "-vf", "scale=360:360:force_original_aspect_ratio=decrease",
                                "-q:v", "4", str(salida)])
    celda = 250
    items = list(idv.items())
    f20 = fuente(20)
    for p in range(0, len(items), 6):
        hoja = Image.new("RGB", (celda * 8 + 20, (celda + 6) * 3), "white")
        d = ImageDraw.Draw(hoja)
        for k, (codigo, v) in enumerate(items[p:p + 6]):
            x0, y0 = (k % 2) * (celda * 4 + 20), (k // 2) * (celda + 6)
            for j in range(4):
                fp = vframes / f"{codigo}_{j}.jpg"
                if fp.exists():
                    t = Image.open(fp)
                    t.thumbnail((celda - 4, celda - 4))
                    hoja.paste(t, (x0 + j * celda, y0))
            d.rectangle([x0, y0, x0 + 150, y0 + 26], fill="black")
            d.text((x0 + 4, y0 + 2), f"{codigo} {datos[v]['dur']:.0f}s", fill="yellow", font=f20)
        hoja.save(hojas / f"videos_{p // 6 + 1:02d}.jpg", quality=80)
    print(f"{len(idf)} fotos y {len(idv)} vídeos numerados. Hojas en {hojas}")


if __name__ == "__main__":
    main()
