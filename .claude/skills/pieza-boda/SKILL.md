---
name: pieza-boda
description: Produce una pieza suelta de Instagram (reel, «deslizar» o carrusel, o historia) a partir de la carpeta de una boda en Drive y la deja lista en 02_Produccion con su texto, su revisión y su cola de Metricool. Úsala cuando alguien diga «reel de la boda de…», «deslizar de…», «historia de…» o pida una pieza concreta de una boda.
---

# Pieza suelta de una boda

El sistema está en [`docs/planes/sistema-piezas-boda.md`](../../../docs/planes/sistema-piezas-boda.md). **Léelo antes de empezar**: esta skill solo lo aplica. Si algo choca, manda el documento.

Tú **decides** (material, recortes, retoques, rótulos, texto) y lo escribes en `pieza.json`. Los scripts de `herramientas/piezas/` solo **producen** a partir de ese fichero. Instalación y ejemplos de cada script: [`herramientas/piezas/README.md`](../../../herramientas/piezas/README.md).

Reglas que no se saltan:
- **Nunca se escribe en `01_Material/`** de Drive. Todo el trabajo intermedio va a `.trabajo/` (fuera de Git).
- Ninguna foto, vídeo ni render entra en Git. Una pieza suelta no genera ficha ni PR.
- Las reglas de `CLAUDE.md` §2 y §4 mandan: sin marca antigua, sin «Citroën», sin matrículas legibles, sin caras de menores, sin datos inventados y sin atar la marca a una ciudad.

Todos los comandos se lanzan desde la raíz del repositorio. En Windows, Claude Code usa Git Bash: los comandos son los mismos, con `python` en lugar de `python3`.

## Paso 1. Interpretar la orden

Saca de la orden (§2 del documento) tres cosas:

| Parte | Valores | Si no la dice |
|---|---|---|
| Formato | `reel` · `deslizar` (carrusel) · `historia` (o «N historias») | Pregunta |
| Boda | Fecha, lugar o «la última» | Pregunta |
| Indicaciones | Tema, coche, «sin caras», «sin música», variante | Decides tú |

Variantes: `reel` → `limpio` (cortes secos, rótulos pequeños) o `titular` (rótulo grande en el gancho). `deslizar` → `foto-entera` (sin rótulos salvo portada) o `con-rotulos` (una frase en 2–4 diapositivas). `historia` → `foto-frase` (foto con frase) o `clip-cta` (clip con «¿Cuándo os casáis?»). Si no se pide una, alterna con las piezas anteriores de esa boda (paso 3).

## Paso 2. Localizar la boda

```bash
python3 herramientas/piezas/localizar.py la posadilla
python3 herramientas/piezas/localizar.py 24 de octubre
python3 herramientas/piezas/localizar.py la última
```

Devuelve un JSON con `drive` (la carpeta `Mehari We`) y `candidatas` (`ruta`, `relativa` a `Mehari We` y `motivo`).

- **`drive` es `null`**: Drive no está sincronizado o está en otra ruta. Pide la ruta de `Mehari We` y vuelve a lanzarlo con `MEHARI_DRIVE="<ruta>"` delante.
- **0 candidatas**: pide la ruta de la carpeta de la boda.
- **2 o más**: enséñalas (relativa y motivo) y pregunta. **Nunca adivines.**
- **1**: sigue. `relativa` es el `carpeta_origen` de `pieza.json`.

## Paso 3. Inventario, ficha y piezas anteriores

La carpeta de trabajo de cada boda es `.trabajo/<boda>/`, con `<boda>` = `AAAA-MM-DD_<lugar>`. La **fecha sale del EXIF** (o de la ficha), nunca del nombre de la carpeta de Drive: «Boda 24:10:2026» tiene la boda del 31-10. El lugar sale de la ficha, del nombre de la carpeta o de las piezas anteriores; si no consta, pregunta. Minúsculas y guiones: `2026-10-24_la-posadilla`.

1. Si ya hay piezas de esa carpeta (mira el `carpeta_origen` de los `pieza.json` de `.trabajo/*/*/` o de `02_Produccion/*/*/`), usa el mismo `<boda>` e inventaria directamente en `.trabajo/<boda>`.
2. Si es la primera vez, inventaria en una carpeta provisional, lee la fecha y renómbrala:
   ```bash
   python3 herramientas/piezas/inventario.py "<ruta de la candidata>" .trabajo/_nueva
   mv .trabajo/_nueva .trabajo/2026-10-24_la-posadilla
   ```
   Si `.trabajo/<boda>` ya existía, borra `.trabajo/_nueva` y lanza el inventario sobre `.trabajo/<boda>`. El inventario imprime la carpeta `_inventario/`, el número de ficheros, los errores y `Fecha de la boda`. Es reanudable: si se corta o algún fichero falla («solo en la nube», HEIC dañado), se vuelve a lanzar y solo repite lo que falta. Un fichero con `error` se queda fuera, pero no para el resto.
3. Crea la carpeta de la pieza: `.trabajo/<boda>/<id_pieza>/`, con `<id_pieza>` = `<AAAA-MM-DD de hoy>_<formato>_<tema>` (por ejemplo `2026-11-06_deslizar_las-cestas`). El tema va en minúsculas, números y guiones; si la orden no lo dice, decídelo ya y, si cambia al elegir el material, renombra la carpeta. Los comandos de esta skill usan estas variables:
   ```bash
   ORIGEN="<ruta de la candidata del paso 2>"
   B=".trabajo/2026-10-24_la-posadilla"
   P="$B/2026-11-06_deslizar_las-cestas"
   mkdir -p "$P"
   ```
   Dentro de `$P` quedan `pieza.json`, `proyecto/` (material preparado, revisión y render), `salida/` (solo los ficheros finales), `rejilla/` y `control/`. Todo se puede borrar y regenerar desde `pieza.json`.
4. **Ficha**: si la carpeta de la boda tiene una ficha, léela. De ahí salen el permiso de caras, los nombres, la iglesia, la hacienda, las flores y el fotógrafo. Lo que no esté en la ficha ni se lea en la foto va como `[PENDIENTE: …]`.
5. **Piezas anteriores**: lee los `pieza.json` de `02_Produccion/<boda>/*/`. No repitas la foto de portada del carrusel ni el plano del gancho del reel, y alterna las variantes.

## Paso 4. Ver y elegir

1. Mira las hojas de contacto de `.trabajo/<boda>/_inventario/hojas/hoja_NN.jpg` (20 miniaturas por hoja, con el nombre del fichero y la duración de los vídeos). Para ver una foto en grande, abre su miniatura de `_inventario/thumbs/` o el original.
2. Elige con esta prioridad: **sin retoque > recorte > retoque**. Si se puede esquivar la matrícula, la funda o un menor con el encuadre, se recorta; solo se retoca cuando no hay más remedio.
3. Pasa **`revision-marca`** a cada elemento elegido y apunta el resultado en su `revision_marca`: `APTA`, `APTA CON RETOQUE: <qué se tapa>` o, si es `NO APTA`, se descarta.
4. Para cada recorte o retoque, lee las coordenadas con la rejilla. Son píxeles del **original tal como se ve** (con la orientación EXIF o la rotación del vídeo aplicadas):
   ```bash
   python3 herramientas/piezas/rejilla.py "$ORIGEN/IMG_4101.HEIC" "$P/rejilla/04.jpg"
   python3 herramientas/piezas/rejilla.py "$ORIGEN/IMG_4101.HEIC" "$P/rejilla/04_zoom.jpg" --zona 700,1300,500,500 --paso 25
   python3 herramientas/piezas/rejilla.py "$ORIGEN/videos/IMG_4120.MOV" "$P/rejilla/07_t2.jpg" --t 2.4
   ```
   `--zona X,Y,AN,AL` amplía una parte (los números siguen siendo absolutos), `--paso` cambia la separación de las líneas (100 por defecto) y `--t` elige el segundo del fotograma en los vídeos.

Material por formato:
- **Deslizar**: de 5 a 9 fotos (no vídeos). El script añade solo la diapositiva de cierre («¿Cuándo os casáis?» y el WhatsApp), así que salen de 6 a 10 JPEG. Estructura: portada (la mejor foto de los novios con el coche) → el día en orden → cierre. Si se pide un tema, todas giran en torno a él. Con menos de 5 fotos buenas, avisa y propone una historia.
- **Reel**: clips (con `desde` y `hasta`) o fotos (con `duracion`), cada uno con su `tramo`: `gancho` (0–3 s, el plano con más gente y movimiento), `detalle`, `prueba` o `momento`. El cierre de marca (4 s) lo pone el script: **no lo añadas como elemento**. Con el cierre, el reel dura de 15 a 25 s, así que los elementos suman de 11 a 21 s. Si no hay clips, se monta con fotos.
- **Historia**: de 1 a 10 elementos; cada uno sale en su propia historia. En `foto-frase`, fotos. En `clip-cta`, clips (o fotos) con `desde`/`hasta` o `duracion`; `pieza.py` exige que **cada clip** dure como máximo 15 s (cada elemento es una historia aparte). Si un elemento no tiene `rotulo`, sale «¿Cuándo os casáis?».

## Paso 5. Música (solo reel)

1. Primero, `Mehari We/03_Marca/musica/`: cada pista lleva al lado su `licencia.txt`. Copia la licencia tal cual en `musica.licencia`.
2. Si no hay ninguna que encaje, busca una con HyperFrames (necesita el CLI de `heygen` instalado y con sesión):
   ```bash
   npx --yes hyperframes@0.8.174 media-use resolve --type bgm --intent "acústica alegre, boda al aire libre" --project "$P/musica"
   ```
   Apunta en `musica.ruta` la ruta absoluta del fichero que deja, y en `musica.licencia` lo que diga el catálogo. No la guardes como `proyecto/assets/musica.*`: `producir.py` borra esos ficheros antes de copiar la pista.
3. Si tampoco hay, el reel va **sin música** (`"musica": null`), en modo `aviso` en Metricool, y lo dices en el resumen. Con «sin música» en la orden, igual.

Con música, el reel va en modo `automatico`: tiene que ser libre de derechos (`docs/planes/publicacion-metricool.md` §3).

## Paso 6. Escribir `pieza.json` y producir

Escribe `$P/pieza.json` con la plantilla de abajo y lanza, en orden:

```bash
python3 herramientas/piezas/preparar.py "$P/pieza.json" "$ORIGEN" "$P/proyecto"
python3 herramientas/piezas/producir.py "$P/pieza.json" "$P/proyecto" "$P/salida"
python3 herramientas/piezas/comprobar.py "$P/pieza.json" "$P"/salida/*
```

- **`preparar.py`** valida `pieza.json`, convierte (HEIC→JPG, HLG→SDR BT.709), retoca, recorta y deja cada elemento en `proyecto/assets/material/NN.jpg|mp4`. Escribe además `proyecto/revision/NN_antes.jpg` y `NN_despues.jpg` de cada elemento con recorte o retoque, y **siempre** `proyecto/revision/avisos.json` (lista vacía si no hay avisos) y `proyecto/revision/preparado.json` (la huella del material). Empieza vaciando `assets/material/` y `revision/`. Si para con un error de recorte, de zona o de retoque, corrige `pieza.json` y repítelo.
- **`producir.py`** copia la plantilla (`marca/plantillas/estaticas/` para deslizar y foto-frase; `marca/plantillas/reel/` con HyperFrames para reel y clip-cta) y deja en `salida/` solo los ficheros finales: `01.jpg…NN.jpg`, `reel.mp4` + `portada.jpg`, o `historia.jpg|mp4` (`historia-01…NN` si hay varias).
- **`comprobar.py`** imprime un JSON con `errores`, `avisos` y `pendientes` y sale con código 1 si hay errores. Corrige cada error. Revisa cada aviso («Sevilla», «Cádiz»): nombrar el lugar de la boda vale; presentar la marca como de allí, no.

**Si `producir.py` falla**, lee el error (incluye la salida de `hyperframes check` o de `exportar.mjs`), corrige y repite **una vez**. Si vuelve a fallar, no se entrega nada: explica el error.

Para cambiar un rótulo o el texto basta con editar `pieza.json` y volver a lanzar `producir.py`. Si cambian el material, el recorte, los retoques o los cortes, hay que lanzar antes `preparar.py`: `producir.py` y `entregar.py` se niegan si `revision/preparado.json` no corresponde al `pieza.json` actual.

### Plantilla de `pieza.json`

```json
{
  "version": 1,
  "boda": "2026-10-24_la-posadilla",
  "carpeta_origen": "01_Material/Selecccion/Boda 2:11:2026",
  "formato": "deslizar",
  "variante": "con-rotulos",
  "tema": "las-cestas",
  "permiso_caras": "pendiente",
  "hay_caras": true,
  "musica": null,
  "ubicacion": null,
  "elementos": [
    {
      "orden": 1,
      "fichero": "IMG_4101.HEIC",
      "recorte": { "x": 0, "y": 120, "ancho": 3024, "alto": 4032 },
      "retoques": [{ "tipo": "funda", "poligono": [[812,1460],[990,1460],[990,1720],[812,1720]] }],
      "rotulo": "Las cestas, llenas de flores blancas",
      "revision_marca": "APTA CON RETOQUE: funda de rueda tras los asientos"
    }
  ],
  "texto": "…copy final con CTA a WhatsApp 625 06 42 93 y de 3 a 5 hashtags…",
  "a_mano_despues": ["Sticker de ubicación: Finca La Posadilla"],
  "pendientes": []
}
```

| Campo | Qué va |
|---|---|
| `version` | Siempre `1` |
| `boda` | `AAAA-MM-DD_lugar` (fecha del EXIF o de la ficha) |
| `carpeta_origen` | La `relativa` de `localizar.py` |
| `formato`, `variante` | Ver paso 1 |
| `tema` | Minúsculas, números y guiones |
| `permiso_caras` | `si` (la ficha lo confirma), `no` o `pendiente` |
| `hay_caras` | `true` si se reconoce alguna cara en la pieza. Si falta, se supone `true` |
| `musica` | `{"ruta": "<ruta absoluta de la pista>", "licencia": "…", "titulo": "…"}` (`ruta` y `licencia` obligatorias, `titulo` opcional) o `null` |
| `ubicacion` | Texto de la ubicación para Metricool, o `null`. Si no se sabe, `null` y se apunta en `pendientes` |
| `elementos[].orden` | 1, 2, 3… sin repetir. Manda el orden de salida |
| `elementos[].fichero` | Ruta relativa a la carpeta de la boda (`fotos/IMG_1.HEIC`). Los vídeos, en `.mov` o `.mp4` (`.m4v`, `.avi`… se rechazan: conviértelos antes) |
| `elementos[].recorte` | Opcional. `{x, y, ancho, alto}` en píxeles del original tal como se ve. Sin recorte, se encuadra centrado (3:4 en deslizar, 9:16 en lo demás) |
| `elementos[].retoques` | Opcional. Ver abajo |
| `elementos[].rotulo` | Opcional. Frase corta en pantalla. Sigue las reglas del texto (salvo teléfono y hashtags); un `[…]` deja la pieza `NO PUBLICAR` |
| `elementos[].revision_marca` | Resultado de `revision-marca` |
| `elementos[].tramo`, `desde`, `hasta`, `duracion` | Reel: `tramo` y (`desde` + `hasta`, en segundos del clip) o `duracion` (fotos). Historia `clip-cta`: `desde` + `hasta` o `duracion` |
| `texto` | Copy final: tuteo en plural, CTA a WhatsApp 625 06 42 93, de 3 a 5 hashtags. Sin «Citroën», sin la marca antigua, sin «—», sin «experiencia única» |
| `a_mano_despues` | Lo que se hace a mano en la app: sticker, Collab, etiquetas, ubicación si Metricool no la pone |
| `pendientes` | Cada dato que falta. Si no está vacío, la pieza sale `NO PUBLICAR` |

Retoques, siempre en píxeles (y segundos) del **original tal como se ve**, exactamente lo que enseña `rejilla.py`. Una foto solo admite `placa`, `funda` y `emblema`; un vídeo, solo `zona`. Cualquier otro tipo (o `"Placa"` con mayúscula) o una forma incompleta es un error de `pieza.py`:

| Tipo | Para | Forma |
|---|---|---|
| `placa` | Matrícula en foto (queda una placa lisa) | `{"tipo": "placa", "poligono": [[x,y], …]}`, al menos 4 vértices por dentro del borde |
| `funda` | Funda «@MEHARI_TOURSUR» en foto | `{"tipo": "funda", "poligono": [[x,y], …]}`, por dentro del borde |
| `emblema` | Chevrones o logo sobre chapa lisa en foto | `{"tipo": "emblema", "caja": [x, y, ancho, alto]}` |
| `zona` | Cualquier cosa en vídeo (se difumina siguiéndola) | `{"tipo": "zona", "t": 2.4, "caja": [x, y, ancho, alto], "desde": 2.0, "hasta": 5.0}`. `t` es el segundo del clip original en que se marca la caja (con `rejilla.py --t`) y tiene que estar **dentro** del corte `desde`–`hasta` del elemento. `desde` y `hasta` de la zona son opcionales y limitan el difuminado |

El difuminado se aplica después de escalar a 1080×1920. Si el seguimiento puede haberse perdido, o si la zona queda fuera del encuadre final (y por tanto no se difumina), `preparar.py` lo apunta en `revision/avisos.json` y la pieza no puede salir `LISTA`.

Ejemplos de elementos de reel y de historia en clip:

```json
{ "orden": 1, "fichero": "videos/IMG_4120.MOV", "tramo": "gancho", "desde": 1.0, "hasta": 3.5,
  "retoques": [{ "tipo": "zona", "t": 2.4, "caja": [610, 1480, 220, 90] }],
  "rotulo": "Salen de la iglesia", "revision_marca": "APTA CON RETOQUE: matrícula del coche de detrás" },
{ "orden": 2, "fichero": "fotos/IMG_4101.HEIC", "tramo": "detalle", "duracion": 2.5,
  "revision_marca": "APTA" }
```

## Paso 7. Mirar el resultado

Antes de entregar, mira la pieza final buscando **matrículas, la funda «@MEHARI_TOURSUR», chevrones y caras de menores** que se hayan escapado:

- **JPEG**: abre cada fichero de `$P/salida/`.
- **MP4**: saca un fotograma por plano (el segundo central de cada uno, sumando las duraciones) y míralos:
  ```bash
  mkdir -p "$P/control"
  ffmpeg -y -loglevel error -ss 1.5 -i "$P/salida/reel.mp4" -frames:v 1 "$P/control/plano-01.jpg"
  ```
- Abre también los `$P/proyecto/revision/NN_despues.jpg`.

Si aparece algo, corrige `pieza.json` (otro recorte, otro retoque u otro material) y vuelve al paso 6. Si el retoque se nota o no se puede hacer, **descarta ese material**. Nunca sale una pieza con rastro.

## Paso 8. Entregar

```bash
python3 herramientas/piezas/entregar.py "$P/pieza.json" "$P/proyecto" "$P/salida"
```

Busca `02_Produccion` en Drive (o se le pasa con `--produccion "<ruta>"`) e imprime la carpeta creada: `02_Produccion/<boda>/<id_pieza>/` o `<id_pieza>_PENDIENTE/`, con `-2`, `-3`… si ya existe. Nunca sobrescribe. Deja los ficheros finales, `texto.txt` (primera línea `Estado: LISTA` o `Estado: NO PUBLICAR · <motivos>`), `revision.html`, `revision/`, `cola-metricool.json` (una entrada, `fecha: null`, aprobación pendiente) y una copia de `pieza.json`.

**No entrega nada** (y dice por qué) si: falla el formato de un medio; el texto tiene un error (nombra «Citroën» o la marca antigua, lleva «—» o «experiencia única», pasa de 5 hashtags o le falta el 625 06 42 93); un rótulo, la ubicación o una línea de `a_mano_despues` tiene uno de esos errores; falta `proyecto/revision/avisos.json` o está mal; falta `proyecto/revision/preparado.json` o no corresponde al `pieza.json` actual; falta el antes y después de un elemento con recorte o retoques; o los ficheros de `salida/` no son exactamente los de la pieza (sobran o faltan). Corrige y vuelve a lanzarlo.

**Entrega como `NO PUBLICAR`** (carpeta `_PENDIENTE`) si: hay caras (`hay_caras` verdadero o ausente) sin `permiso_caras: "si"`, quedan marcadores `[…]` en el texto, en un rótulo, en la ubicación o en `a_mano_despues`, o datos en `pendientes`, o hay avisos de difuminado.

## Paso 9. Resumen

Tres líneas en el chat, nada más:
1. Qué se ha hecho: formato, variante, tema y carpeta de Drive.
2. Estado: `LISTA` o `NO PUBLICAR` con su motivo.
3. Qué falta: pendientes, lo que va a mano, «sin música» si es el caso, y que una persona mire `revision.html` (unos 30 s) antes de mandarlo al cliente.

Sin aprobación del cliente no se programa nada. Cuando llegue, Alejandro pone la fecha y la aprobación en `cola-metricool.json` y lanza `programar-metricool` sobre esa carpeta.

## Casos

| Caso | Qué hace |
|---|---|
| No encuentra la boda, o coinciden varias | Pregunta y enseña las candidatas. Nunca adivina |
| Drive no está sincronizado, o la ruta es distinta | `localizar.py` busca en Mac (`~/Library/CloudStorage/GoogleDrive-*/My Drive/` o `Mi unidad/`) y Windows (`G:\Mi unidad\`, `G:\My Drive\`). Si no encuentra `Mehari We`, pide la ruta. Se puede fijar con la variable de entorno `MEHARI_DRIVE` |
| No hay ficha, o no consta el permiso de caras | Produce la pieza con `permiso_caras: "pendiente"`, y sale `NO PUBLICAR · falta permiso de caras`. Con «sin caras», elige solo detalles (coche, cestas, manos, de espaldas) y pon `hay_caras: false` |
| Faltan datos (iglesia, flores, fotógrafo) | Marcador `[PENDIENTE: …]` en el texto. La pieza queda `_PENDIENTE` |
| Poco material | El carrusel baja hasta 5 fotos (6 diapositivas con el cierre); por debajo, avisa y propone una historia. El reel se monta con fotos si no hay clips |
| Funda, matrícula o menor imposible de esquivar o recortar | Se retoca. Si el retoque se nota o no se puede hacer, la foto se descarta |
| Zona de vídeo fuera del corte | `preparar.py` para con «la zona en t=… queda fuera del corte»: vuelve a marcarla con `rejilla.py --t` en un segundo entre `desde` y `hasta` |
| Seguimiento del difuminado perdido | Queda en `revision/avisos.json` y en `revision.html`, y la pieza sale `NO PUBLICAR`. Mira el vídeo: añade otra zona marcada en otro segundo, acorta el corte o cambia de plano, y vuelve al paso 6 |
| Fichero en Drive «solo en la nube» | Leerlo fuerza la descarga. Puede tardar, pero no es un error. Si el inventario lo apunta con error, se vuelve a lanzar |
| El render falla | Se lee la salida de `hyperframes check`, se corrige y se repite una vez. Si sigue fallando, no se entrega nada a medias y se explica el error |
| `entregar.py` se niega | No ha escrito nada en Drive. Corrige lo que dice y vuelve a lanzarlo |
| Ya existe una carpeta con ese nombre | Se añade `-2`, `-3`… Nunca se sobrescribe una entrega |
| Una pieza `_PENDIENTE` ya se puede publicar (llega el permiso, se completa un dato) | Cambia `pieza.json` en `.trabajo/` (`permiso_caras: "si"`, el dato en su sitio, `pendientes` vacío). Si cambia un rótulo, vuelve a lanzar `producir.py`. Después vuelve a lanzar `entregar.py`, que crea una carpeta nueva sin `_PENDIENTE`. Entonces hay que borrar a mano la carpeta `_PENDIENTE` antigua de `02_Produccion` para no dejar dos versiones: pide confirmación antes de borrarla |

## Checklist

- [ ] Boda localizada sin adivinar; `<boda>` con la fecha del EXIF o de la ficha
- [ ] Piezas anteriores de `02_Produccion/<boda>/` leídas: ni la misma portada ni el mismo gancho, y variante alternada
- [ ] Cada elemento ha pasado `revision-marca`, con su resultado en `revision_marca`; material elegido por «sin retoque > recorte > retoque»
- [ ] Coordenadas de recortes y retoques leídas con `rejilla.py` (`--t` en vídeos, dentro del corte)
- [ ] `permiso_caras` y `hay_caras` según la ficha y lo que se ve; nada de menores ni de matrículas
- [ ] Texto con CTA a WhatsApp 625 06 42 93, de 3 a 5 hashtags, sin «Citroën», sin la marca antigua, sin «—», sin «experiencia única», sin atar la marca a una ciudad y sin datos inventados; rótulos, ubicación y `a_mano_despues` con las mismas reglas
- [ ] Reel: música con licencia de `03_Marca/musica/` o de `media-use`, o «sin música» dicho en el resumen
- [ ] `preparar.py`, `producir.py` y `comprobar.py` sin errores
- [ ] Cada JPEG o un fotograma por plano mirado a ojo, más los `NN_despues.jpg`
- [ ] Entregada con `entregar.py` y resumen de tres líneas en el chat
