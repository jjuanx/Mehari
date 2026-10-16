"""Paso 7. Genera una galería HTML filtrable (línea, coche, marca antigua, calidad y texto).

Dos versiones:
- Local (por defecto): <carpeta>/galeria.html. Miniaturas de _analisis/ y clic al ORIGINAL.
- Drive: --drive "<nombre de la carpeta de la selección>" escribe _analisis/galeria_drive.html,
  pensada para ir en 01_Material/Galeria/ junto a thumbs/ y vframes/. El clic abre la copia de
  ../<selección>/… (solo las fichas con calidad >= 4; el resto no está en Drive y no tiene enlace).

Uso:
  python 7_galeria.py "<carpeta>"
  python 7_galeria.py "<carpeta>" --drive "Seleccion"
"""
import argparse
import csv
import json
from pathlib import Path

from comun import nombre_miniatura

CARPETA = {"boda": "bodas", "coche": "coche", "detalle": "detalles", "turismo": "turismo", "otro": "otros"}

PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Galería Mehari We</title><style>
:root{--bg:#faf7f2;--fg:#2b2620;--mut:#7a7066;--card:#fff;--bd:#e6ded3;--acc:#c4621a;--warn:#b42318}
@media (prefers-color-scheme:dark){:root{--bg:#1c1915;--fg:#eee6dc;--mut:#a59a8d;--card:#27231e;--bd:#3a342d;--acc:#f0913f;--warn:#f97066}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.4 system-ui,sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--bd);padding:12px 16px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
h1{font-size:17px;margin:0 12px 0 0}select,input{background:var(--card);color:var(--fg);border:1px solid var(--bd);border-radius:6px;padding:6px 8px;font:inherit}
#n{color:var(--mut);margin-left:auto}.aviso{width:100%;color:var(--mut);font-size:12px}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;padding:16px}
.c{background:var(--card);border:1px solid var(--bd);border-radius:8px;overflow:hidden}.c img{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:#0001}
.m{padding:6px 8px;font-size:12px}.m b{color:var(--acc)}.m .x{color:var(--mut)}.w{color:var(--warn);font-weight:600}</style></head><body>
<header><h1>Mehari We · material</h1>
<select id="tipo"><option value="">Fotos y vídeos</option><option>foto</option><option>video</option></select>
<select id="linea"><option value="">Todas las líneas</option><option>boda</option><option>turismo</option><option>coche</option><option>detalle</option><option>otro</option></select>
<select id="coche"><option value="">Ambos coches</option><option>naranja</option><option>beige</option><option>ambos</option><option>sin coche</option></select>
<select id="marca"><option value="">Marca antigua: todas</option><option value="no">Sin marca antigua</option><option value="si">Con marca antigua</option><option value="revisar">Revisar</option></select>
<select id="q"><option value="1">Calidad ≥1</option><option value="3">≥3</option><option value="4" selected>≥4</option><option value="5">5</option></select>
<input id="s" placeholder="Buscar en notas (atardecer, Macarena, PROFESIONAL…)" size="34"><span id="n"></span>
<div class="aviso">__AVISO__ Antes de publicar: matrículas ilegibles, menores sin cara y nada de la marca antigua (CLAUDE.md §4).</div></header><main id="g"></main>
<script>const D=__DATOS__;const $=i=>document.getElementById(i);
function r(){const t=$("tipo").value,l=$("linea").value,c=$("coche").value,mk=$("marca").value,q=+$("q").value,s=$("s").value.toLowerCase();
const f=D.filter(d=>(!t||d.t==t)&&(!l||d.l==l)&&(!c||d.c==c)&&(!mk||d.m==mk)&&d.q>=q&&(!s||(d.n+" "+d.id).toLowerCase().includes(s)));
$("n").textContent=f.length+" de "+D.length;
$("g").innerHTML=f.slice(0,1500).map(d=>{const img=`<img loading="lazy" src="${encodeURI(d.th)}" alt="${d.id}">`;
return `<div class="c">${d.h?`<a href="${encodeURI(d.h)}" target="_blank">${img}</a>`:img}<div class="m"><b>${d.id}</b> · ${d.l} · ${d.c} · ${"★".repeat(d.q)}${d.t=="video"?" · "+d.d+" s":""}${d.m!="no"?' <span class="w">marca antigua: '+d.m+"</span>":""}<div class="x">${d.n}</div></div></div>`}).join("")}
document.querySelectorAll("select,input").forEach(e=>e.addEventListener("input",r));r();</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("--drive", metavar="SELECCION", help="nombre de la carpeta de la selección en Drive")
    a = ap.parse_args()
    raiz = Path(a.carpeta).expanduser().resolve()
    with open(raiz / "_analisis" / "clasificacion.csv", encoding="utf-8-sig") as fh:
        filas = list(csv.DictReader(fh, delimiter=";"))
    prefijo = "" if a.drive else "_analisis/"
    datos = []
    for r in filas:
        th = f"{prefijo}thumbs/{nombre_miniatura(r['archivo'])}" if r["tipo"] == "foto" else f"{prefijo}vframes/{r['id']}_1.jpg"
        enlace = r["archivo"]
        if a.drive:
            enlace = ""
            if int(r["calidad"]) >= 4:
                carpeta = f"{r['tipo']}s/{CARPETA[r['linea']]}" if r["marca_antigua"] == "no" else "para_retoque_marca_antigua"
                ext = ".jpg" if r["tipo"] == "foto" else Path(r["archivo"]).suffix.lower()
                enlace = f"../{a.drive}/{carpeta}/{r['id']}_q{r['calidad']}_{r['coche'].replace(' ', '')}{ext}"
        datos.append({"id": r["id"], "t": r["tipo"], "l": r["linea"], "c": r["coche"], "m": r["marca_antigua"],
                      "q": int(r["calidad"]), "n": r["nota"], "d": r["duracion_s"], "th": th, "h": enlace})
    aviso = ("Clic para abrir la copia de la selección (solo calidad ≥4)." if a.drive
             else "Clic para abrir el original.")
    html = PLANTILLA.replace("__DATOS__", json.dumps(datos, ensure_ascii=False)).replace("__AVISO__", aviso)
    salida = raiz / "_analisis" / "galeria_drive.html" if a.drive else raiz / "galeria.html"
    salida.write_text(html, encoding="utf-8")
    print(f"{len(datos)} fichas en {salida}")


if __name__ == "__main__":
    main()
