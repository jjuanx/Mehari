# Herramientas de piezas sueltas

Scripts que convierten la carpeta de una boda en Drive en una pieza de Instagram (reel, carrusel «deslizar» o historia) lista en `02_Produccion`. Los orquesta la skill [`pieza-boda`](../../.claude/skills/pieza-boda/SKILL.md); el sistema completo está en [`docs/planes/sistema-piezas-boda.md`](../../docs/planes/sistema-piezas-boda.md).

Claude decide y lo escribe en `pieza.json`; los scripts solo leen ese fichero. Nunca escriben en `01_Material/` de Drive: el trabajo intermedio va a `.trabajo/` (en la raíz del repositorio, fuera de Git).

## Instalación (una vez en cada ordenador)

Hace falta Python 3.10 o superior, Node.js 22 o superior y FFmpeg en el PATH **con el filtro `zscale`** (libzimg). Sin él no se pueden pasar a SDR los vídeos HDR del iPhone y `preparar.py` se para con un aviso.

- **Mac**: el `ffmpeg` normal de Homebrew no trae `zscale`. Instala `brew install ffmpeg-full` (va aparte y no sustituye al otro) y lanza los scripts con `PATH="/opt/homebrew/opt/ffmpeg-full/bin:$PATH"` delante, o añade esa ruta al principio del PATH en tu `~/.zshrc`.
- **Windows**: `winget install Gyan.FFmpeg` (el build «full» de gyan.dev ya trae `zscale`).

Para comprobarlo: `ffmpeg -hide_banner -filters | grep zscale` tiene que devolver una línea.

```bash
pip install -r herramientas/piezas/requirements.txt
cd herramientas/piezas && npm install && npx playwright install chromium
```

`requirements.txt` incluye el de `herramientas/material/` (Pillow, pillow-heif, OpenCV…) y pytest. `npm install` instala Playwright, que exporta los carruseles y las historias en foto con Chromium. HyperFrames no se instala: `producir.py` lo lanza con `npx --yes hyperframes@0.8.174`, que lo descarga la primera vez (necesita internet una vez).

En Windows se usa `python` en lugar de `python3`.

## Scripts, en el orden de uso

Todos se lanzan desde la raíz del repositorio. En los ejemplos:

```bash
ORIGEN="$HOME/Library/CloudStorage/GoogleDrive-…/My Drive/Mehari We/01_Material/Selecccion/Boda 24:10:2026"
P=".trabajo/2026-10-24_la-posadilla/2026-11-06_deslizar_las-cestas"
```

| Script | Qué hace |
|---|---|
| `localizar.py` | Encuentra `Mehari We` en Drive (Mac, Windows en `G:`, o la variable `MEHARI_DRIVE`) y las carpetas de boda que encajan con la consulta |
| `inventario.py` | Miniaturas, datos técnicos, fecha EXIF y hojas de contacto de la carpeta de la boda. Reanudable |
| `rejilla.py` | Rejilla de coordenadas sobre una foto o un fotograma, para leer recortes y retoques |
| `preparar.py` | Convierte, retoca, recorta y deja el material en `proyecto/assets/material/`, con el antes y después y `revision/avisos.json` |
| `producir.py` | Rellena la plantilla del formato y renderiza los ficheros finales en `salida/` |
| `comprobar.py` | Controles automáticos de formato y de texto |
| `entregar.py` | Copia la pieza a `02_Produccion/<boda>/<id_pieza>/` con `texto.txt`, `revision.html` y `cola-metricool.json` |
| `pieza.py`, `rutas.py`, `exportar.mjs` | Validación de `pieza.json`, rutas del repositorio y exportación con Playwright (los usan los demás) |

### localizar.py

```bash
python3 herramientas/piezas/localizar.py la posadilla
python3 herramientas/piezas/localizar.py la última
MEHARI_DRIVE="/ruta/a/Mehari We" python3 herramientas/piezas/localizar.py 24 de octubre
```

Imprime un JSON con `drive` y `candidatas` (`ruta`, `relativa` a `Mehari We` y `motivo`). Con 0 o varias candidatas, la skill pregunta.

Busca `Mehari We` en `~/Library/CloudStorage/GoogleDrive-*/My Drive/` (o `Mi unidad/`) en Mac y en `G:\My Drive\` (o `G:\Mi unidad\`) en Windows. Si Drive para escritorio usa otra letra de unidad, o la carpeta está en una unidad compartida, define `MEHARI_DRIVE` con la ruta completa de `Mehari We`; en Git Bash, por ejemplo, `export MEHARI_DRIVE="/h/My Drive/Mehari We"` (unidad H:) o `export MEHARI_DRIVE="/g/Unidades compartidas/Mehari We"` (unidad compartida). Las fechas con «_» («Boda 24_10_2026», como escribe Drive para Windows los «:») también se reconocen.

### inventario.py

```bash
python3 herramientas/piezas/inventario.py "$ORIGEN" .trabajo/2026-10-24_la-posadilla
```

Escribe `<trabajo>/_inventario/` (`inventario.jsonl`, `thumbs/` y `hojas/hoja_NN.jpg` con 20 miniaturas por hoja) e imprime la carpeta, el número de ficheros, los errores y la fecha de la boda (la fecha EXIF más repetida). Un fichero ilegible queda con `error` y no para el resto; al relanzarlo se reintenta.

### rejilla.py

```bash
python3 herramientas/piezas/rejilla.py "$ORIGEN/IMG_4101.HEIC" "$P/rejilla/04.jpg"
python3 herramientas/piezas/rejilla.py "$ORIGEN/IMG_4101.HEIC" "$P/rejilla/04_zoom.jpg" --zona 700,1300,500,500 --paso 25
python3 herramientas/piezas/rejilla.py "$ORIGEN/videos/IMG_4120.MOV" "$P/rejilla/07.jpg" --t 2.4
```

Las coordenadas son las del original tal como se ve (orientación EXIF o rotación del vídeo aplicadas) y siempre absolutas, también con `--zona`. `--paso` es la separación de las líneas (100 por defecto) y `--t`, el segundo del fotograma en los vídeos. Son las coordenadas que espera `pieza.json`.

### preparar.py

```bash
python3 herramientas/piezas/preparar.py "$P/pieza.json" "$ORIGEN" "$P/proyecto"
```

Valida `pieza.json` (también cada retoque: en fotos `placa`, `funda` o `emblema`; en vídeos, solo `zona`) y, antes de procesar nada, que cada recorte cabe en la imagen y que cada zona de vídeo cae dentro de su corte. Empieza vaciando `proyecto/assets/material/` y `proyecto/revision/`. Deja `proyecto/assets/material/NN.jpg` o `NN.mp4` (1080×1920 y 30 fps en los vídeos), `proyecto/revision/NN_antes.jpg` y `NN_despues.jpg` en los elementos con recorte o retoque, y siempre `proyecto/revision/avisos.json` (lista vacía si el difuminado ha ido bien; un aviso si el seguimiento puede haberse perdido o si una zona queda fuera del encuadre) y `proyecto/revision/preparado.json`, con la huella de lo que decide el material.

### producir.py

```bash
python3 herramientas/piezas/producir.py "$P/pieza.json" "$P/proyecto" "$P/salida"
```

Deslizar e historia en foto: copia `marca/plantillas/estaticas/` y exporta con Chromium (`01.jpg…NN.jpg` de 1080×1440, con la diapositiva de cierre añadida, o `historia.jpg` / `historia-NN.jpg` de 1080×1920). Reel e historia en clip: copia `marca/plantillas/reel/`, pasa `hyperframes check` y renderiza (`reel.mp4` + `portada.jpg`, o `historia.mp4` / `historia-NN.mp4`). Borra antes las salidas antiguas con el mismo patrón de nombre. Se niega si `proyecto/revision/preparado.json` falta o no corresponde al `pieza.json` (se ha cambiado el material sin volver a preparar). Para el reel y la historia en clip busca `npx` en el PATH (en Windows, `npx.cmd`).

### comprobar.py

```bash
python3 herramientas/piezas/comprobar.py "$P/pieza.json" "$P"/salida/*
```

Imprime `errores`, `avisos` y `pendientes` en JSON y sale con código 1 si hay errores. Formato: dimensiones, códec, fps, duración y audio AAC; carrusel de 2 a 10 JPEG. Texto: sin «Citroën», sin la marca antigua («Tour Sur», «toursur», «Mehari Experiences»), sin «—», sin «experiencia única», como máximo 5 hashtags y con el 625 06 42 93. Los rótulos, la ubicación y las líneas de `a_mano_despues` siguen las mismas reglas salvo el teléfono y los hashtags, y sus `[…]` cuentan como pendientes. «Sevilla», «sevillano/a/os/as» o «Cádiz» (con o sin tilde) son avisos, no errores.

### entregar.py

```bash
python3 herramientas/piezas/entregar.py "$P/pieza.json" "$P/proyecto" "$P/salida"
python3 herramientas/piezas/entregar.py "$P/pieza.json" "$P/proyecto" "$P/salida" --produccion "/ruta/a/Mehari We/02_Produccion"
```

Sin `--produccion`, busca `Mehari We/02_Produccion` como `localizar.py`. Crea `02_Produccion/<boda>/<id_pieza>/` (o `_PENDIENTE`, con `-2`, `-3`… si ya existe) e imprime la ruta. No entrega nada si falla un control automático (formato o textos), si falta o está mal `proyecto/revision/avisos.json`, si `proyecto/revision/preparado.json` falta o no corresponde al `pieza.json`, si falta el antes y después de un elemento recortado o retocado, o si los ficheros de `salida/` no son exactamente los de la pieza. Sale `NO PUBLICAR` si hay caras sin permiso, datos pendientes o avisos de difuminado.

## Plantillas

En `marca/plantillas/`: `estaticas/` (HTML para carrusel e historia en foto) y `reel/` (proyecto de HyperFrames para reel e historia en clip, con el cierre y la transición de marca). Usan los valores de color y tipografía de `marca/tokens.css`, copiados en cada plantilla: si cambian los tokens, hay que cambiarlos también ahí.

## Pruebas

```bash
python3 -m pytest herramientas/piezas/tests -m "not lento" -q
python3 -m pytest herramientas/piezas/tests -q
```

Las rápidas no renderizan con HyperFrames. Las marcadas `lento` hacen un render real (varios minutos).
