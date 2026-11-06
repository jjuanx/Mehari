# Sistema de piezas por boda — Plan de implementación

> **Para agentes:** SUB-SKILL OBLIGATORIA: usa superpowers:subagent-driven-development (recomendado) o superpowers:executing-plans para ejecutar este plan tarea a tarea. Los pasos usan casillas (`- [ ]`) para el seguimiento.

**Objetivo:** con la orden «reel», «deslizar» o «historia» y una boda, dejar en Drive (`02_Produccion/`) la pieza terminada con su texto, su revisión y su cola de Metricool.

**Arquitectura:** la skill `pieza-boda` decide (material, variante, rótulos y texto) y lo escribe en `pieza.json`. Unos scripts de Python en `herramientas/piezas/` hacen el trabajo mecánico leyendo solo ese fichero: inventario, preparación, render y entrega. Los estáticos salen de una plantilla HTML exportada con Playwright; el reel y la historia en clip salen de una plantilla de HyperFrames que `producir.py` rellena.

**Tecnología:** Python 3 (Pillow, pillow-heif, OpenCV, pytest), FFmpeg/ffprobe, Node 22+ con Playwright (Chromium) y HyperFrames `0.8.174`.

**Especificación:** [`docs/planes/sistema-piezas-boda.md`](sistema-piezas-boda.md). Léela entera antes de empezar: este plan la desarrolla y no repite su porqué.

## Restricciones globales

- Todo en español: código (nombres), comentarios, mensajes, commits y documentación.
- Commits en imperativo y en español; todos terminan con la línea `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Rama `feature/sistema-piezas-boda`; nunca commit en `main` ni en `Desarrollo`.
- **Nunca se escribe en `01_Material/`** de Drive. El trabajo intermedio va a `.trabajo/` (raíz del repositorio, fuera de Git).
- Ninguna foto, vídeo ni render entra en Git. Sí se versionan las plantillas y sus fuentes, el SVG del logo, `gsap.min.js`, `cierre.mp4` y `transicion.webm` (ligeros y de marca).
- Rutas siempre como `pathlib.Path`, y a `subprocess` siempre como lista de argumentos, nunca con `shell=True`. Las carpetas de Drive tienen espacios, tildes y «:» («Boda 24:10:2026», «Mi unidad»).
- Formatos de salida: reel `1080×1920`, H.264, 30 fps, 15–25 s, AAC si hay música; carrusel `1080×1440` JPEG calidad 90, de 2 a 10 ficheros; historia `1080×1920` JPEG, o MP4 de ≤15 s.
- Texto: teléfono `625 06 42 93`, como máximo **5** hashtags, sin «Citroën», sin «—» y sin «experiencia única».
- Cierre del reel: `marca/animaciones/renders/cierre.mp4` (4,0 s). Transición: `marca/animaciones/renders/transicion.webm` (0,866 s, con alfa).
- Tokens de color y tipografía: los valores de `marca/tokens.css`, sin inventar colores.
- Formatos y variantes válidos: `reel` → `limpio`, `titular` · `deslizar` → `foto-entera`, `con-rotulos` · `historia` → `foto-frase`, `clip-cta`.
- HyperFrames siempre con versión fija: `npx --yes hyperframes@0.8.174 …`.

## Puntos que vigilar en la revisión

Cinco entradas que la especificación no menciona y que es fácil que fallen en el uso real, de la más a la menos probable. Cada una tiene su prueba en la tarea indicada.

1. **Rutas con espacios, «:» y tildes** (`My Drive/Mehari We/01_Material/Selecccion/Boda 24:10:2026/IMG 1.HEIC`): todo funciona igual. Prueba en la tarea 5.
2. **Fotos con orientación EXIF** (iPhone en vertical, guardada en horizontal con la etiqueta 6): las coordenadas de recorte y retoque se refieren a la foto *tal como se ve*, igual que en `rejilla.py`. Prueba en las tareas 3 y 5.
3. **Ficheros ilegibles o vacíos** (0 bytes, HEIC corrupto, fichero de Drive «solo en la nube» que falla al bajar): el inventario lo apunta con `error` y sigue con el resto. Prueba en la tarea 3.
4. **Rótulos y textos con comillas, `&`, `<` o «»** (`Sábado en "La Posadilla" & <cía>`): salen literales en el JPEG, el reel y `revision.html`, sin romper el HTML. Pruebas en las tareas 6, 7 y 8.
5. **Vídeo con rotación en los metadatos** (vertical guardado como 1920×1080 con rotación de 90°): se trata como vertical. Prueba en la tarea 5.

---

## Estructura de ficheros

```
herramientas/piezas/
├─ README.md                 uso de cada script (tarea 10)
├─ requirements.txt          pytest + lo de herramientas/material
├─ package.json              playwright (exportar.mjs)
├─ rutas.py                  raíz del repo, .trabajo/ y plantillas
├─ pieza.py                  cargar y validar pieza.json
├─ localizar.py              Drive y carpetas de boda (CLI)
├─ inventario.py             miniaturas, EXIF, hojas de contacto (CLI)
├─ rejilla.py                recorte con rejilla de coordenadas para marcar retoques (CLI)
├─ preparar.py               material → assets/ (CLI)
├─ producir.py               plantilla + assets → ficheros finales (CLI)
├─ exportar.mjs              HTML → JPEG con Playwright
├─ comprobar.py              controles automáticos (CLI)
├─ entregar.py               → 02_Produccion/ (CLI)
└─ tests/                    pytest; conftest.py crea fotos y vídeos de prueba
marca/plantillas/
├─ estaticas/index.html      deslizar e historia en foto (lee datos.json)
├─ estaticas/assets/         fuentes y logos
└─ reel/index.html           reel e historia en clip (marcadores que rellena producir.py)
   reel/assets/              fuentes, logo, gsap.min.js, cierre.mp4, transicion.webm
.claude/skills/pieza-boda/SKILL.md
```

Modificados: `herramientas/material/1_analizar.py` (un parámetro opcional), `.claude/skills/programar-metricool/SKILL.md`, `docs/planes/publicacion-metricool.md`, `.gitignore`, `SKILLS.md`, `CLAUDE.md`, `docs/decisiones.md`.

---

### Tarea 1: Base y validación de `pieza.json`

**Ficheros:**
- Crear: `herramientas/piezas/requirements.txt`, `herramientas/piezas/package.json`, `herramientas/piezas/rutas.py`, `herramientas/piezas/pieza.py`, `herramientas/piezas/tests/conftest.py`
- Modificar: `.gitignore` (añadir `.trabajo/` y `herramientas/piezas/node_modules/`)
- Prueba: `herramientas/piezas/tests/test_pieza.py`

**Interfaces:**
- Produce:
  - `rutas.REPO: Path`, `rutas.TRABAJO: Path` (`REPO / ".trabajo"`), `rutas.PLANTILLAS: Path` (`REPO / "marca/plantillas"`), `rutas.MATERIAL: Path` (`REPO / "herramientas/material"`)
  - `pieza.FORMATOS: dict[str, tuple[str, ...]]`, con los valores de las restricciones globales
  - `pieza.PiezaInvalida(Exception)`, con el atributo `errores: list[str]`
  - `pieza.cargar_pieza(ruta: Path) -> dict`: lee y valida el fichero; lanza `PiezaInvalida` con **todos** los errores a la vez
  - `pieza.duracion_elemento(el: dict) -> float`: `hasta - desde` si es un clip; `duracion` si es una foto dentro de un reel
  - `pieza.duracion_total(p: dict) -> float`: suma de los elementos + 4,0 s de cierre (solo `reel`)
  - `pieza.id_pieza(p: dict, hoy: date) -> str`: `"<hoy ISO>_<formato>_<tema>"`
  - `conftest.py`, fixtures: `foto_jpg(tmp_path) -> Path` (3024×4032 con un rectángulo de color conocido), `foto_rotada(tmp_path) -> Path` (JPEG de 4032×3024 con EXIF Orientation=6), `clip_mp4(tmp_path) -> Path` (5 s, 1080×1920, `testsrc`), `clip_rotado(tmp_path) -> Path` (1920×1080 con `-display_rotation 90`), `pieza_minima(formato) -> dict` (pieza válida mínima de cada formato; la del reel tiene 4 clips de 3 s)
  - Helpers de `conftest.py` que usan las pruebas de todas las tareas: `escribir(carpeta: Path, datos: dict) -> Path` (guarda `pieza.json`), `leer(inventario: Path) -> dict[str, dict]` (filas del JSONL por `file`), `ffprobe_wh(ruta: Path) -> tuple[int, int]` (teniendo en cuenta la rotación) y `ffprobe_dur(ruta: Path) -> float`. Las fixtures `*_preparada` de las tareas 6–8 las añade a `conftest.py` la tarea que las usa: ejecutan `preparar` sobre `foto_jpg`/`clip_mp4` y devuelven `(pieza, proyecto)`; `entrega_preparada` devuelve `(ruta_pieza, salidas, proyecto)`

Campos de `pieza.json` (versión 1): los de la especificación §3.2, más `hay_caras: bool` (lo pone Claude si algún elemento muestra caras de los novios), `ubicacion: str | null` y, en el reel, por elemento: `tramo` ∈ {`gancho`, `detalle`, `prueba`, `momento`} y `desde`/`hasta` (clip) o `duracion` (foto).

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
def test_pieza_valida_de_cada_formato(pieza_minima, tmp_path):
    for formato in ("reel", "deslizar", "historia"):
        ruta = escribir(tmp_path, pieza_minima(formato))
        assert cargar_pieza(ruta)["formato"] == formato

def test_junta_todos_los_errores(tmp_path):
    with pytest.raises(PiezaInvalida) as e:
        cargar_pieza(escribir(tmp_path, {"version": 1, "formato": "reel", "variante": "con-rotulos",
                                          "boda": "Boda 24:10:2026", "permiso_caras": "quizá"}))
    texto = " ".join(e.value.errores)
    assert "variante" in texto and "boda" in texto and "permiso_caras" in texto and "elementos" in texto

def test_deslizar_admite_de_5_a_9_fotos_mas_el_cierre(pieza_minima, tmp_path):
    p = pieza_minima("deslizar"); p["elementos"] = p["elementos"][:1] * 4
    with pytest.raises(PiezaInvalida): cargar_pieza(escribir(tmp_path, p))

def test_reel_dura_entre_15_y_25_segundos_con_el_cierre(pieza_minima, tmp_path):
    p = pieza_minima("reel")                       # suma de elementos 12 s + 4 s de cierre = 16 s
    assert duracion_total(cargar_pieza(escribir(tmp_path, p))) == 16.0
    p["elementos"][0]["hasta"] += 10               # 26 s
    with pytest.raises(PiezaInvalida): cargar_pieza(escribir(tmp_path, p))

def test_historia_en_clip_no_pasa_de_15_segundos(pieza_minima, tmp_path):
    p = pieza_minima("historia"); p["variante"] = "clip-cta"
    p["elementos"] = [{"orden": 1, "fichero": "a.mov", "desde": 0, "hasta": 16}]
    with pytest.raises(PiezaInvalida): cargar_pieza(escribir(tmp_path, p))

def test_id_pieza():
    assert id_pieza({"formato": "deslizar", "tema": "las-cestas"}, date(2026, 11, 6)) == "2026-11-06_deslizar_las-cestas"
```

- [ ] **Paso 2: Ejecutarlas y comprobar que fallan**

Ejecutar: `python3 -m pytest herramientas/piezas/tests/test_pieza.py -v`
Resultado esperado: FALLA con `ModuleNotFoundError: No module named 'pieza'`.

- [ ] **Paso 3: Implementar `rutas.py`, `pieza.py`, `conftest.py`, `requirements.txt` y `package.json`**

`requirements.txt`: `-r ../material/requirements.txt` y `pytest`. `package.json`: privado, `"type": "module"` y `playwright` como dependencia. `conftest.py` añade `herramientas/piezas` a `sys.path` y crea los vídeos con `ffmpeg -f lavfi -i testsrc=size=1080x1920:rate=30 -t 5`. Reglas de validación: `boda` cumple `^\d{4}-\d{2}-\d{2}_[a-z0-9-]+$`; `tema` cumple `^[a-z0-9-]+$`; `permiso_caras` ∈ {`si`, `no`, `pendiente`}; elementos de `deslizar`: de 5 a 9; elementos de `historia`: de 1 a 10.

- [ ] **Paso 4: Instalar dependencias, ejecutar las pruebas y comprobar que pasan**

Ejecutar: `pip install -r herramientas/piezas/requirements.txt && (cd herramientas/piezas && npm install) && python3 -m pytest herramientas/piezas/tests/test_pieza.py -v`
Resultado esperado: 6 pasan.

- [ ] **Paso 5: Commit**

```bash
git add .gitignore herramientas/piezas
git commit -m "Añade la base de herramientas/piezas y la validación de pieza.json"
```

---

### Tarea 2: Localizar Drive y la boda

**Ficheros:**
- Crear: `herramientas/piezas/localizar.py`
- Prueba: `herramientas/piezas/tests/test_localizar.py`

**Interfaces:**
- Produce:
  - `raiz_drive(entorno: Mapping[str, str], casa: Path, unidades: Sequence[Path] = (Path("G:/"),)) -> Path | None`. Orden de búsqueda: `entorno["MEHARI_DRIVE"]`; `casa/Library/CloudStorage/GoogleDrive-*/{My Drive,Mi unidad}/Mehari We`; `<unidad>/{Mi unidad,My Drive}/Mehari We`. Devuelve la primera ruta que existe
  - `@dataclass Candidata: ruta: Path; relativa: str; motivo: str`
  - `buscar_bodas(raiz: Path, consulta: str) -> list[Candidata]`: busca carpetas bajo `raiz/01_Material` (profundidad ≤3) que contengan fotos o vídeos, directamente o en `fotos/` y `videos/`. Ignora las que empiezan por `_` o `.`. Ordena por coincidencia
  - `fechas_en(consulta: str) -> list[date]`: entiende `2026-10-24`, `24-10-2026`, `24:10:2026`, `24/10/2026`, `24/10` (año en curso) y `24 de octubre`
  - CLI: `python3 herramientas/piezas/localizar.py "<consulta>"` → JSON `{"drive": str | null, "candidatas": [{ruta, relativa, motivo}]}`. «la última» o «última» → la carpeta con la modificación más reciente

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
def test_drive_por_variable_de_entorno(tmp_path):
    (tmp_path / "X").mkdir()
    assert raiz_drive({"MEHARI_DRIVE": str(tmp_path / "X")}, casa=tmp_path / "casa") == tmp_path / "X"

def test_drive_en_mac_mi_unidad(tmp_path):
    d = tmp_path / "Library/CloudStorage/GoogleDrive-a@b.com/Mi unidad/Mehari We"; d.mkdir(parents=True)
    assert raiz_drive({}, casa=tmp_path, unidades=()) == d

def test_drive_en_windows(tmp_path):
    d = tmp_path / "G/My Drive/Mehari We"; d.mkdir(parents=True)
    assert raiz_drive({}, casa=tmp_path / "casa", unidades=(tmp_path / "G",)) == d

def test_fechas_en_varios_formatos():
    for txt in ("2026-10-24", "24-10-2026", "boda 24:10:2026", "24/10/2026", "el 24 de octubre"):
        assert date(2026, 10, 24) in fechas_en(txt)

def test_busca_por_fecha_en_nombre_antiguo_y_por_lugar(drive_falso):
    # drive_falso: 01_Material/Selecccion/Boda 24:10:2026/IMG_1.HEIC y 01_Material/Bodas/2026-11-07_sanlucar/fotos/a.jpg
    assert [c.relativa for c in buscar_bodas(drive_falso, "boda del 24 de octubre")] == ["01_Material/Selecccion/Boda 24:10:2026"]
    assert buscar_bodas(drive_falso, "sanlúcar")[0].relativa == "01_Material/Bodas/2026-11-07_sanlucar"

def test_ignora_carpetas_internas(drive_falso):
    assert not [c for c in buscar_bodas(drive_falso, "") if "/_" in c.relativa]
```

- [ ] **Paso 2: Ejecutarlas y comprobar que fallan**

Ejecutar: `python3 -m pytest herramientas/piezas/tests/test_localizar.py -v` → FALLA (no existe el módulo).

- [ ] **Paso 3: Implementar `localizar.py`**

Al comparar el lugar se quitan tildes y mayúsculas (`unicodedata.normalize("NFKD")`). Añade la fixture `drive_falso` a `conftest.py`.

- [ ] **Paso 4: Ejecutar las pruebas** → pasan todas.

- [ ] **Paso 5: Commit** — `Añade localizar.py: Drive en Mac y Windows y búsqueda de bodas`

---

### Tarea 3: Inventario y rejilla de coordenadas

**Ficheros:**
- Modificar: `herramientas/material/1_analizar.py` (`analizar_foto`)
- Crear: `herramientas/piezas/inventario.py`, `herramientas/piezas/rejilla.py`
- Prueba: `herramientas/piezas/tests/test_inventario.py`

**Interfaces:**
- Consume: `rutas.MATERIAL`; `comun.ffprobe`, `comun.EXT_FOTO`, `comun.EXT_VIDEO` y `analizar_foto` de `1_analizar.py` (se importa con `importlib`, porque el nombre empieza por un número)
- Cambio en `1_analizar.analizar_foto(args)`: `args` admite una tercera posición opcional, `carpeta_miniaturas: Path`. Si no se pasa, se comporta igual que hoy (`raiz/_analisis/thumbs`). El uso por línea de comandos de `1_analizar.py` no cambia
- Produce:
  - `inventariar(boda: Path, trabajo: Path) -> Path`: escribe `trabajo/_inventario/inventario.jsonl` (una línea por fichero: `file` como ruta relativa a `boda` con `/`, `kind`, `w`, `h`, `date`, `dur` y `error` si lo hay), `trabajo/_inventario/thumbs/` y `trabajo/_inventario/hojas/hoja_NN.jpg` (20 miniaturas por hoja, con el nombre del fichero debajo; en los vídeos, el fotograma del segundo 1 y la duración). Devuelve la carpeta `_inventario`. Es reanudable: no repite los ficheros que ya están en el JSONL
  - `fecha_boda(registros: list[dict]) -> date | None`: la fecha EXIF más repetida
  - `rejilla(entrada: Path, salida: Path, zona: tuple[int, int, int, int] | None = None, paso: int = 100) -> Path`: recorte (en píxeles de la foto tal como se ve, después de `exif_transpose`) con líneas y números de coordenadas cada `paso` px, para que Claude lea los vértices de una matrícula o una funda. En vídeo, con `--t <segundos>` toma ese fotograma
  - CLI: `python3 herramientas/piezas/inventario.py "<carpeta boda>" "<trabajo>"` imprime la ruta de `_inventario`, cuántos ficheros hay, cuántos errores y la fecha de la boda. `python3 herramientas/piezas/rejilla.py <fichero> <salida.jpg> [--zona X,Y,AN,AL] [--paso 50] [--t 1.2]`

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
def test_inventario_recursivo_y_sin_escribir_en_la_boda(tmp_path, foto_jpg, clip_mp4):
    boda = tmp_path / "Boda 24:10:2026"; (boda / "fotos").mkdir(parents=True); (boda / "videos").mkdir()
    shutil.copy(foto_jpg, boda / "fotos/IMG 1.jpg"); shutil.copy(clip_mp4, boda / "videos/V1.mp4")
    antes = sorted(p.relative_to(boda) for p in boda.rglob("*"))
    inv = inventariar(boda, tmp_path / "trabajo")
    filas = [json.loads(l) for l in (inv / "inventario.jsonl").read_text().splitlines()]
    assert {f["file"] for f in filas} == {"fotos/IMG 1.jpg", "videos/V1.mp4"}
    assert sorted(p.relative_to(boda) for p in boda.rglob("*")) == antes
    assert list((inv / "hojas").glob("hoja_*.jpg"))

def test_fichero_vacio_se_apunta_y_se_sigue(tmp_path, foto_jpg):
    boda = tmp_path / "b"; boda.mkdir(); (boda / "roto.heic").write_bytes(b""); shutil.copy(foto_jpg, boda / "ok.jpg")
    filas = leer(inventariar(boda, tmp_path / "t"))
    assert "error" in filas["roto.heic"] and "error" not in filas["ok.jpg"]

def test_fecha_boda_es_la_mas_repetida():
    regs = [{"date": "2026:10:24 14:06:00"}] * 3 + [{"date": "2026:10:25 10:00:00"}]
    assert fecha_boda(regs) == date(2026, 10, 24)

def test_rejilla_respeta_la_orientacion_exif(tmp_path, foto_rotada):
    salida = rejilla(foto_rotada, tmp_path / "r.jpg")
    with Image.open(salida) as im: assert im.height > im.width   # 3024×4032 tal como se ve

def test_analizar_por_linea_de_comandos_no_cambia(tmp_path, foto_jpg):
    shutil.copy(foto_jpg, tmp_path / "a.jpg")
    subprocess.run([sys.executable, str(MATERIAL / "1_analizar.py"), str(tmp_path)], check=True)
    assert (tmp_path / "_analisis/thumbs/a.jpg.jpg").exists()
```

- [ ] **Paso 2: Ejecutarlas** → FALLAN.

- [ ] **Paso 3: Implementar** el parámetro opcional de `analizar_foto`, `inventario.py` (miniaturas con nombre `file` en el que `/` se cambia por `__` y se aplica `nombre_miniatura`) y `rejilla.py`.

- [ ] **Paso 4: Ejecutar** `python3 -m pytest herramientas/piezas/tests/test_inventario.py -v` → pasan todas.

- [ ] **Paso 5: Commit** — `Añade el inventario de una boda y la rejilla para marcar retoques`

---

### Tarea 4: Controles automáticos

**Ficheros:**
- Crear: `herramientas/piezas/comprobar.py`
- Prueba: `herramientas/piezas/tests/test_comprobar.py`

**Interfaces:**
- Produce:
  - `@dataclass ResultadoTexto: errores: list[str]; avisos: list[str]; pendientes: list[str]`
  - `comprobar_texto(texto: str) -> ResultadoTexto`. Errores: contiene «citroën» o «citroen» (sin distinguir mayúsculas); contiene «—»; contiene «experiencia única»; tiene más de 5 hashtags (`#\w+`); no contiene `625 06 42 93`. Avisos: «sevilla», «sevillano», «sevillana» o «cádiz». Pendientes: cada `[...]`
  - `comprobar_medios(formato: str, variante: str, ficheros: list[Path]) -> list[str]` (errores), con los formatos de las restricciones globales. Usa ffprobe para códec (`h264`), fps (30), duración y dimensiones, y Pillow para el JPEG
  - CLI: `python3 herramientas/piezas/comprobar.py <pieza.json> <fichero>...` imprime JSON `{"errores", "avisos", "pendientes"}` y sale con código 1 si hay errores

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
BUENO = "Sábado en la finca.\n\nEscribidnos al 625 06 42 93.\n\n#cochedeboda #novios2027"

def test_texto_bueno(): assert comprobar_texto(BUENO) == ResultadoTexto([], [], [])

@pytest.mark.parametrize("malo", ["Nuestro Citroën", "una experiencia única", "boda — finca",
                                  BUENO + " #a #b #c #d", BUENO.replace("625 06 42 93", "")])
def test_texto_con_errores(malo): assert comprobar_texto(malo).errores

def test_sevilla_es_aviso_no_error():
    r = comprobar_texto(BUENO + "\nBoda en Sevilla.")
    assert not r.errores and r.avisos

def test_marcadores_son_pendientes():
    assert comprobar_texto(BUENO + " [PENDIENTE: iglesia]").pendientes == ["[PENDIENTE: iglesia]"]

def test_carrusel_debe_ser_jpeg_1080x1440(tmp_path):
    png = tmp_path / "01.png"; Image.new("RGB", (1080, 1440)).save(png)
    jpg = tmp_path / "02.jpg"; Image.new("RGB", (1080, 1350)).save(jpg)
    assert len(comprobar_medios("deslizar", "foto-entera", [png, jpg])) >= 2

def test_reel_de_5_segundos_no_vale(clip_mp4):
    assert any("duración" in e for e in comprobar_medios("reel", "limpio", [clip_mp4]))
```

- [ ] **Paso 2: Ejecutarlas** → FALLAN.
- [ ] **Paso 3: Implementar `comprobar.py`.**
- [ ] **Paso 4: Ejecutar** `python3 -m pytest herramientas/piezas/tests/test_comprobar.py -v` → pasan todas.
- [ ] **Paso 5: Commit** — `Añade los controles automáticos de formato y texto`

---

### Tarea 5: Preparar el material

**Ficheros:**
- Crear: `herramientas/piezas/preparar.py`
- Prueba: `herramientas/piezas/tests/test_preparar.py`

**Interfaces:**
- Consume: `pieza.cargar_pieza`, `rutas.MATERIAL` (`retocar_foto.py` y `difuminar.py` se llaman por `subprocess`)
- Produce:
  - `preparar(p: dict, boda: Path, proyecto: Path) -> list[Path]`: un fichero por elemento, en `proyecto/assets/material/NN.jpg` o `NN.mp4` (NN = `orden` con dos cifras). Guarda también `proyecto/revision/NN_antes.jpg` y `NN_despues.jpg` (a 800 px) en cada elemento con recorte o retoque
  - Fotos: abrir (HEIC incluido) → `exif_transpose` → retoques (coordenadas de la foto tal como se ve) → `recorte` → guardar JPEG de calidad 92 en la resolución original del recorte
  - Retoques de foto: `{"tipo": "placa" | "funda", "poligono": [[x, y], ...]}` → `retocar_foto.py --placa/--funda`; `{"tipo": "emblema", "caja": [x, y, an, al]}` → `--emblema`
  - Vídeos (`.mov`, `.mp4`): si ffprobe da `color_transfer == "arib-std-b67"`, convertir a SDR con el filtro `zscale…tonemap=mobius` de la cabecera de `difuminar.py` → cortar `desde`–`hasta` → retoques `{"tipo": "zona", "t", "caja", "desde"?, "hasta"?}` con `difuminar.py --zona` → `recorte` → escalar y recortar a 1080×1920 → H.264 a 30 fps, CRF 15, sin audio
  - Si un elemento no tiene `recorte`, se encuadra al centro con la proporción del formato (3:4 en `deslizar`, 9:16 en lo demás)
  - CLI: `python3 herramientas/piezas/preparar.py <pieza.json> "<carpeta boda>" <proyecto>`

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
def test_ruta_con_espacios_y_dos_puntos(tmp_path, foto_jpg, pieza_minima):
    boda = tmp_path / "My Drive/Boda 24:10:2026"; boda.mkdir(parents=True); shutil.copy(foto_jpg, boda / "IMG 1.jpg")
    p = pieza_minima("historia"); p["elementos"] = [{"orden": 1, "fichero": "IMG 1.jpg"}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    with Image.open(salida) as im: assert abs(im.width / im.height - 9 / 16) < 0.01

def test_orientacion_exif_y_recorte_en_coordenadas_vistas(tmp_path, foto_rotada, pieza_minima):
    boda = tmp_path / "b"; boda.mkdir(); shutil.copy(foto_rotada, boda / "r.jpg")
    p = pieza_minima("historia"); p["elementos"] = [{"orden": 1, "fichero": "r.jpg",
         "recorte": {"x": 0, "y": 0, "ancho": 3024, "alto": 2000}}]
    [salida] = preparar(p, boda, tmp_path / "proy")
    with Image.open(salida) as im: assert im.size == (3024, 2000)

def test_retoque_genera_antes_y_despues(tmp_path, foto_jpg, pieza_minima):
    # foto_jpg lleva un rectángulo blanco con letras negras en (1000,2000)-(1400,2100)
    p = pieza_minima("historia"); p["elementos"] = [{"orden": 1, "fichero": "f.jpg",
         "retoques": [{"tipo": "placa", "poligono": [[1005,2005],[1395,2005],[1395,2095],[1005,2095]]}]}]
    ...  # copiar, preparar
    assert (tmp_path / "proy/revision/01_antes.jpg").exists() and (tmp_path / "proy/revision/01_despues.jpg").exists()

def test_video_rotado_sale_vertical(tmp_path, clip_rotado, pieza_minima):
    p = pieza_minima("historia"); p["variante"] = "clip-cta"
    p["elementos"] = [{"orden": 1, "fichero": "v.mp4", "desde": 1, "hasta": 4}]
    ...  # copiar, preparar
    assert ffprobe_wh(salida) == (1080, 1920) and abs(ffprobe_dur(salida) - 3) < 0.1
```

- [ ] **Paso 2: Ejecutarlas** → FALLAN.
- [ ] **Paso 3: Implementar `preparar.py`.** Las dimensiones de un vídeo se leen teniendo en cuenta la rotación (`side_data_list[].rotation`): con ±90 se intercambian ancho y alto. FFmpeg ya aplica la rotación al recodificar.
- [ ] **Paso 4: Ejecutar** `python3 -m pytest herramientas/piezas/tests/test_preparar.py -v` → pasan todas.
- [ ] **Paso 5: Commit** — `Añade preparar.py: conversión, retoque y recorte del material elegido`

---

### Tarea 6: Plantilla estática y producción de carrusel e historia en foto

**Ficheros:**
- Crear: `marca/plantillas/estaticas/index.html`, `marca/plantillas/estaticas/assets/` (copiar `Fraunces.woff2` y `Jost.woff2` de `redes/instagram/reels/sin-fecha_pov-conducis-vosotros/assets/fonts/`, y `mehari-we-blanco.svg` y `mehari-we-naranja.svg` de `marca/logo/`), `herramientas/piezas/exportar.mjs`, `herramientas/piezas/producir.py`
- Prueba: `herramientas/piezas/tests/test_producir_estaticas.py`

**Interfaces:**
- Consume: los ficheros de `preparar` en `proyecto/assets/material/`
- Produce:
  - `index.html` lee `datos.json` (lo escribe `producir.py`) con `{"formato", "variante", "ancho", "alto", "diapositivas": [{"foto": "assets/material/01.jpg", "rotulo": str | null, "tipo": "portada" | "paso" | "cierre" | "historia"}]}` y, con `?s=<n>`, pinta solo esa diapositiva a tamaño real; sin parámetros, todas en pequeño. Diseño: el de `bodas/2026-10-24_la-posadilla/piezas.html` (velo, logo, rótulo y cierre con costillas, CTA y `WhatsApp · 625 06 42 93`), con colores y fuentes de `marca/tokens.css`. Variante `foto-entera`: rótulo solo en la portada y el cierre. Los textos se insertan con `textContent`, nunca con `innerHTML`
  - `exportar.mjs <proyecto> <n> <ancho> <alto> <carpeta salida> <prefijo>`: abre `index.html?s=i` en Chromium, espera a `document.fonts.ready` y a que carguen las imágenes, y guarda `<prefijo>NN.jpg` en calidad 90
  - `producir.estaticas(p: dict, proyecto: Path, salida: Path) -> list[Path]`: copia la plantilla en `proyecto`, escribe `datos.json` y llama a `node exportar.mjs`. `deslizar` añade la diapositiva de cierre al final → `01.jpg … NN.jpg`. `historia` (`foto-frase`) → `historia.jpg` o `historia-01.jpg …`
  - `producir.producir(ruta_pieza: Path, proyecto: Path, salida: Path) -> list[Path]`: según el formato y la variante, llama a `estaticas` o a `video` (tarea 8). CLI: `python3 herramientas/piezas/producir.py <pieza.json> <proyecto> <salida>`

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
def test_deslizar_da_jpegs_1080x1440_mas_cierre(tmp_path, pieza_deslizar_preparada):
    salidas = estaticas(*pieza_deslizar_preparada(n_fotos=5), tmp_path / "out")
    assert [s.name for s in salidas] == [f"{i:02d}.jpg" for i in range(1, 7)]
    assert all(Image.open(s).size == (1080, 1440) for s in salidas)

def test_historia_foto_es_1080x1920(tmp_path, pieza_historia_preparada):
    [s] = estaticas(*pieza_historia_preparada(), tmp_path / "out")
    assert s.name == "historia.jpg" and Image.open(s).size == (1080, 1920)

def test_rotulo_con_caracteres_especiales_sale_literal(tmp_path, pieza_deslizar_preparada):
    p, proy = pieza_deslizar_preparada(n_fotos=5, rotulo='Sábado en "La Posadilla" & <cía>')
    estaticas(p, proy, tmp_path / "out")
    html = pagina_renderizada(proy, s=0)   # Playwright: innerText de la diapositiva
    assert 'Sábado en "La Posadilla" & <cía>' in html
```

- [ ] **Paso 2: Ejecutarlas** → FALLAN.
- [ ] **Paso 3: Implementar la plantilla, `exportar.mjs` y `producir.estaticas`.**
- [ ] **Paso 4: Ejecutar** `python3 -m pytest herramientas/piezas/tests/test_producir_estaticas.py -v` → pasan todas. Abre `marca/plantillas/estaticas/index.html` del proyecto de prueba en el navegador y comprueba a ojo que la portada y el cierre se parecen a los de La Posadilla.
- [ ] **Paso 5: Commit** — `Añade la plantilla estática y la producción de carruseles e historias en foto`

---

### Tarea 7: Entrega en Drive

**Ficheros:**
- Crear: `herramientas/piezas/entregar.py`
- Prueba: `herramientas/piezas/tests/test_entregar.py`

**Interfaces:**
- Consume: `pieza.cargar_pieza`, `pieza.id_pieza`, `comprobar.comprobar_texto`, y `proyecto/revision/*_antes.jpg` y `*_despues.jpg` (tarea 5)
- Produce:
  - `motivos_no_lista(p: dict, r: ResultadoTexto) -> list[str]`: `"falta permiso de caras"` si `hay_caras` y `permiso_caras != "si"`; `"datos pendientes: …"` si hay `r.pendientes` o `p["pendientes"]`
  - `modo_metricool(p: dict) -> str`: `deslizar` → `automatico`; `reel` con `musica` → `automatico`; `reel` sin música → `aviso`; `historia` → `aviso`
  - `generar_cola(p: dict, id_carpeta: str, medios: list[str]) -> dict`: el formato de `publicacion-metricool.md` §4, con `boda`, `zona_horaria: "Europe/Madrid"`, `aprobacion: {estado: "pendiente", lote_enviado: null, aprobado_el: null, aprobado_por: null, nota}` y `publicaciones`. Una publicación por pieza (en `historia`, una por cada fichero): `id`, `fecha: null`, `red: "instagram"`, `tipo` (`deslizar`→`carrusel`, `reel`→`reel`, `historia`→`story`), `modo`, `ficha: null`, `medios`, `portada` (solo en el reel), `texto`, `ubicacion`, `a_mano_despues`, `metricool_id: null`, `estado: "pendiente"`
  - `generar_texto(p: dict, motivos: list[str]) -> str`: primera línea `Estado: LISTA` o `Estado: NO PUBLICAR · <motivos unidos con "; ">`; después una línea en blanco, el copy, `A mano en la app:` con la lista y `Música:` (título y licencia, o «sin música»)
  - `generar_revision(p: dict, medios: list[str], pares: list[tuple[str, str]], r: ResultadoTexto, motivos: list[str]) -> str`: HTML autónomo con la pieza (imágenes y `<video controls>` con rutas relativas), los antes y después, los `revision_marca` de cada elemento, los avisos y los pendientes. Todo el texto escapado con `html.escape`
  - `entregar(ruta_pieza: Path, salidas: list[Path], proyecto: Path, produccion: Path, hoy: date) -> Path`: crea `produccion/<boda>/<id_pieza>[_PENDIENTE][-2…]/` y copia los ficheros, `revision/`, `texto.txt`, `revision.html`, `cola-metricool.json` y `pieza.json`. **Nunca sobrescribe.** Se niega (`SystemExit`) si `comprobar_medios` da errores
  - CLI: `python3 herramientas/piezas/entregar.py <pieza.json> <proyecto> <carpeta salidas>`. La `produccion` sale de `raiz_drive(...) / "02_Produccion"`, o de `--produccion <ruta>`

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
def test_lista_sin_caras_y_sin_pendientes(pieza_minima):
    p = pieza_minima("deslizar") | {"hay_caras": False, "permiso_caras": "pendiente"}
    assert motivos_no_lista(p, ResultadoTexto([], [], [])) == []

def test_caras_sin_permiso_no_se_publica(pieza_minima):
    p = pieza_minima("deslizar") | {"hay_caras": True, "permiso_caras": "pendiente"}
    assert motivos_no_lista(p, ResultadoTexto([], [], [])) == ["falta permiso de caras"]

def test_modos(pieza_minima):
    assert modo_metricool(pieza_minima("reel") | {"musica": {"ruta": "m.mp3", "licencia": "x"}}) == "automatico"
    assert modo_metricool(pieza_minima("reel") | {"musica": None}) == "aviso"
    assert modo_metricool(pieza_minima("historia")) == "aviso"

def test_cola_sigue_el_formato_de_metricool(pieza_minima):
    c = generar_cola(pieza_minima("deslizar"), "2026-11-06_deslizar_las-cestas", ["01.jpg", "02.jpg"])
    pub = c["publicaciones"][0]
    assert c["aprobacion"]["estado"] == "pendiente" and c["zona_horaria"] == "Europe/Madrid"
    assert pub["fecha"] is None and pub["tipo"] == "carrusel" and pub["medios"] == ["01.jpg", "02.jpg"]

def test_no_sobrescribe_y_marca_pendiente(tmp_path, entrega_preparada):
    a = entregar(*entrega_preparada(pendiente=True), produccion=tmp_path, hoy=date(2026, 11, 6))
    b = entregar(*entrega_preparada(pendiente=True), produccion=tmp_path, hoy=date(2026, 11, 6))
    assert a.name == "2026-11-06_deslizar_las-cestas_PENDIENTE" and b.name.endswith("_PENDIENTE-2")
    assert (a / "texto.txt").read_text().startswith("Estado: NO PUBLICAR")

def test_revision_escapa_el_texto(pieza_minima):
    p = pieza_minima("deslizar"); p["texto"] = 'Boda <script>alert(1)</script> & "finca"'
    assert "<script>alert" not in generar_revision(p, [], [], ResultadoTexto([], [], []), [])
```

- [ ] **Paso 2: Ejecutarlas** → FALLAN.
- [ ] **Paso 3: Implementar `entregar.py`.**
- [ ] **Paso 4: Ejecutar** `python3 -m pytest herramientas/piezas/tests/test_entregar.py -v` → pasan todas.
- [ ] **Paso 5: Commit** — `Añade entregar.py: carpeta en 02_Produccion con texto, revisión y cola de Metricool`

---

### Tarea 8: Plantilla del reel e historia en clip

**Ficheros:**
- Crear: `marca/plantillas/reel/index.html`, `marca/plantillas/reel/hyperframes.json`, `marca/plantillas/reel/package.json` (el mismo que el del reel del 11-11, con `hyperframes@0.8.174`), `marca/plantillas/reel/assets/` (`gsap.min.js` y `mehari-we-blanco.svg` del reel `2026-11-11_salis-de-la-iglesia`; fuentes; `cierre.mp4` y `transicion.webm` de `marca/animaciones/renders/`)
- Modificar: `herramientas/piezas/producir.py` (añadir `video`), `.gitignore` (excepción `!marca/plantillas/reel/assets/cierre.mp4`)
- Prueba: `herramientas/piezas/tests/test_producir_video.py`

**Interfaces:**
- Consume: `proyecto/assets/material/NN.mp4|jpg` (tarea 5), `pieza.duracion_elemento`
- Produce:
  - `index.html` con tres marcadores que solo rellena `producir.py`: `<!--PLANOS-->` (elementos `<video class="clip plano">` y `<img class="clip plano">` en la pista 0, con `data-start`, `data-duration` y `data-media-start="0"`), `<!--ROTULOS-->` (`<div class="clip rotulo">` en la pista 1) y `/*ANIMACION*/` (las llamadas `tl.fromTo` de cada plano y rótulo). La estructura es la del `index.html` del reel del 11-11: `#root` con `data-composition-id="reel"`, `window.__timelines["reel"] = tl`
  - `generar_html(p: dict, duraciones: list[float]) -> str`: sustituye los marcadores. Los planos van seguidos; en el reel, el cierre (`assets/cierre.mp4`, 4,0 s) va al final y la transición (`assets/transicion.webm`) se pone 0,41 s antes de cada corte entre `momento` y el siguiente tramo, como en el reel del 11-11. Las fotos llevan un acercamiento lento (escala 1,0 → 1,06 durante su duración). Variante `limpio`: rótulos de 56 px abajo, a 1500 px de `top`, centrados y en un ancho de 864 px (el 80 %). Variante `titular`: el rótulo del gancho a 104 px a 300 px de `top`, con el velo superior del reel del 11-11, y el resto como en `limpio`. `historia` (`clip-cta`): un plano y el rótulo «¿Cuándo os casáis?» salvo que la pieza traiga otro, sin cierre ni transición. Los rótulos se escapan con `html.escape`
  - Música: si `p["musica"]`, copia `musica.ruta` a `assets/musica.<ext>` y añade `<audio id="musica" src="assets/musica.<ext>" data-start="0" data-duration="<total>" data-track-index="2" data-volume="1">` con un fundido de salida en el último segundo
  - `producir.video(p: dict, proyecto: Path, salida: Path) -> list[Path]`: copia la plantilla, escribe `index.html`, ejecuta `npx --yes hyperframes@0.8.174 check` (si falla, lanza la excepción con su salida) y `npx --yes hyperframes@0.8.174 render --output <salida>/reel.mp4` (o `historia.mp4`). En el reel, además, `portada.jpg`: el fotograma del segundo 1,0 sacado con ffmpeg, a 1080×1920

- [ ] **Paso 1: Escribir las pruebas que fallan**

```python
def test_html_del_reel_encadena_planos_y_cierre(pieza_minima):
    p = pieza_minima("reel")                               # 4 elementos de 3 s
    html = generar_html(p, [3, 3, 3, 3])
    assert html.count('class="clip plano"') == 5           # 4 planos + cierre
    assert 'src="assets/cierre.mp4" data-start="12"' in html
    assert "<!--PLANOS-->" not in html and "/*ANIMACION*/" not in html

def test_rotulo_escapado(pieza_minima):
    p = pieza_minima("reel"); p["elementos"][0]["rotulo"] = 'Salís "de" la iglesia & <ya>'
    html = generar_html(p, [3, 3, 3, 3])
    assert "<ya>" not in html and "&lt;ya&gt;" in html and "&amp;" in html

def test_historia_clip_sin_cierre(pieza_minima):
    p = pieza_minima("historia") | {"variante": "clip-cta"}
    p["elementos"] = [{"orden": 1, "fichero": "a.mov", "desde": 0, "hasta": 6}]
    html = generar_html(p, [6])
    assert "cierre.mp4" not in html and "¿Cuándo os casáis?" in html

@pytest.mark.lento
def test_render_real_del_reel(tmp_path, pieza_reel_preparada):
    [mp4, portada] = video(*pieza_reel_preparada(), tmp_path / "out")
    assert comprobar_medios("reel", "limpio", [mp4]) == []
    assert Image.open(portada).size == (1080, 1920)
```

- [ ] **Paso 2: Ejecutarlas** → FALLAN.
- [ ] **Paso 3: Implementar la plantilla, `generar_html` y `producir.video`.** Registra la marca `lento` en `herramientas/piezas/tests/conftest.py` (`pytest_configure`).
- [ ] **Paso 4: Ejecutar las rápidas y la lenta**

Ejecutar: `python3 -m pytest herramientas/piezas/tests/test_producir_video.py -v -m "not lento"` → pasan. Después, `python3 -m pytest herramientas/piezas/tests/test_producir_video.py -v -m lento` → pasa (varios minutos la primera vez, mientras se descarga HyperFrames). Mira el MP4 de prueba: los rótulos quedan dentro de la zona segura y el cierre se ve completo.

- [ ] **Paso 5: Commit** — `Añade la plantilla del reel y la producción de reels e historias en clip`

---

### Tarea 9: `programar-metricool` acepta colas de `02_Produccion`

**Ficheros:**
- Modificar: `.claude/skills/programar-metricool/SKILL.md` (tabla de entradas, pasos 1, 2 y 4), `docs/planes/publicacion-metricool.md` (§1 y §4)

Es un cambio de texto (especificación §5.2), sin código:

- [ ] **Paso 1:** En «Entradas», la cola puede ser `redes/instagram/bodas/<boda>/cola-metricool.json` o la de una carpeta de pieza en Drive (`Mehari We/02_Produccion/<boda>/<pieza>/cola-metricool.json`), con los `medios` relativos a la carpeta de la cola.
- [ ] **Paso 2:** En el paso 1, nueva comprobación: si alguna publicación tiene `fecha: null`, para y pide la fecha. En las colas de `02_Produccion` no hay ficha: se usa en su lugar el `revision.html` de la carpeta, y `texto.txt` tiene que empezar por `Estado: LISTA`.
- [ ] **Paso 3:** En el paso 2, si la cola ya está en `02_Produccion`, los medios ya están en Drive: se comparten desde ahí.
- [ ] **Paso 4:** En el paso 4, si la cola no está en el repositorio, se actualizan `metricool_id` y `estado` en el propio fichero y **no se hace commit**.
- [ ] **Paso 5:** En `publicacion-metricool.md` §1, una línea con el segundo origen de colas (piezas sueltas de `pieza-boda`, enlazando a `sistema-piezas-boda.md`). En §4, `fecha` puede llegar como `null` y se rellena al aprobar.
- [ ] **Paso 6: Commit** — `Permite programar en Metricool las piezas sueltas de 02_Produccion`

---

### Tarea 10: Skill `pieza-boda` y documentación

**Ficheros:**
- Crear: `.claude/skills/pieza-boda/SKILL.md`, `herramientas/piezas/README.md`
- Modificar: `SKILLS.md`, `CLAUDE.md` (§5 mapa: `herramientas/piezas/`, `marca/plantillas/`, `.trabajo/`; §7: una viñeta «Piezas sueltas»), `docs/decisiones.md` (las cuatro decisiones de partida de la especificación §1, con fecha 2026-11-06), `docs/planes/sistema-piezas-boda.md` (versión «1, aprobada» cuando se fusione)

**Contenido de `SKILL.md`.** Cabecera:

```yaml
name: pieza-boda
description: Produce una pieza suelta de Instagram (reel, «deslizar» o carrusel, o historia) a partir de la carpeta de una boda en Drive y la deja lista en 02_Produccion con su texto, su revisión y su cola de Metricool. Úsala cuando alguien diga «reel de la boda de…», «deslizar de…», «historia de…» o pida una pieza concreta de una boda.
```

El cuerpo remite a `docs/planes/sistema-piezas-boda.md` («si algo choca, manda el documento») y sigue el flujo de su §5 con los comandos exactos de las tareas 2–7:
1. Interpretar la orden (§2 de la especificación).
2. Localizar (preguntar si hay 0 o varias candidatas).
3. Inventariar en `.trabajo/<boda>/<id_pieza>/` y leer la ficha y las piezas anteriores de `02_Produccion/<boda>/`.
4. Ver las hojas de contacto y elegir (sin retoque > recorte > retoque). Pasar `revision-marca` a cada elemento. Usar `rejilla.py` para leer las coordenadas de cada retoque.
5. Música para el reel: primero `Mehari We/03_Marca/musica/`, donde cada pista lleva su `licencia.txt`. Si no hay, `npx hyperframes media-use resolve --type bgm` (necesita el CLI de `heygen`). Si tampoco, sin música, en modo `aviso`, y se dice en el resumen.
6. Escribir `pieza.json` → `preparar.py` → `producir.py` → `comprobar.py`. Si `producir.py` falla, leer la salida de `hyperframes check`, corregir y repetir **una vez**. Si vuelve a fallar, no entregar nada y explicar el error.
7. Mirar cada JPEG o un fotograma por plano del MP4 (`ffmpeg -ss <t> -frames:v 1`) buscando matrícula, funda, chevrones y menores. Si hay algo, corregir `pieza.json` y volver al paso 6.
8. `entregar.py`.
9. Resumen de tres líneas.

Incluye la plantilla de `pieza.json` de la especificación §3.2, la tabla de casos de §6.2 y una checklist final.

- [ ] **Paso 1:** Escribir `SKILL.md` y `README.md` (instalación con `pip install -r` y `npm install`, y un ejemplo de cada script).
- [ ] **Paso 2:** Registrar la skill en la tabla de `SKILLS.md` y quitar `ingesta-material` y `lote-semanal` de «Ideas de próximas skills» (las cubre esta).
- [ ] **Paso 3:** Actualizar `CLAUDE.md` y `docs/decisiones.md`.
- [ ] **Paso 4:** Ejecutar todas las pruebas rápidas: `python3 -m pytest herramientas/piezas/tests -m "not lento" -v` → pasan todas.
- [ ] **Paso 5: Commit** — `Añade la skill pieza-boda y documenta el sistema de piezas`

---

### Tarea 11: Prueba real con La Posadilla

Es la prueba de aceptación de la especificación §7. No lleva código nuevo: si algo falla, el arreglo va en la tarea correspondiente, con su prueba.

- [ ] **Paso 1:** En una sesión nueva de Claude Code (para que cargue la skill), pedir «deslizar de la boda de La Posadilla». Anotar el tiempo.
- [ ] **Paso 2:** Pedir «reel de la boda de La Posadilla» y «historia de la boda de La Posadilla». Anotar los tiempos.
- [ ] **Paso 3:** Comprobar en `02_Produccion/2026-10-24_la-posadilla/` que hay tres carpetas, cada una con su `texto.txt`, `revision.html`, `cola-metricool.json` y `pieza.json`. Que `comprobar.py` pasa sin errores. Que ninguna repite portada ni gancho. Que el estado es `NO PUBLICAR · falta permiso de caras` si hay caras, porque esa boda no tiene ficha. Y que cada pieza ha tardado menos de unos 15 minutos.
- [ ] **Paso 4:** Abrir los tres `revision.html` y revisarlos a ojo: ni funda, ni matrícula, ni chevrones.
- [ ] **Paso 5:** Apuntar los resultados (tiempos y problemas) en la descripción del PR #29, sacarlo de borrador y pedir revisión a Alejandro o Nico.
