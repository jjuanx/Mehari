# Sistema de piezas por boda — Méhari We

| Campo | Valor |
|---|---|
| Versión | 1 (diseño **pendiente de revisión** por el equipo) |
| Fecha | 2026-11-06 |
| Qué fija | Cómo se pasa de «la carpeta de la boda está en Drive» a una pieza de Instagram lista para programar, con una sola orden: «reel», «deslizar» o «historia» |
| Base | [semana-boda.md](semana-boda.md) (formatos y tono) · [publicacion-metricool.md](publicacion-metricool.md) (cola y música) · [automatizacion-contenido.md](automatizacion-contenido.md) §2 (plantillas y render por lotes) |
| Skill | `pieza-boda` (nueva) |

---

## 1. Qué problema resuelve

Hoy, `semana-boda` deja escrito **qué** foto va en cada sitio, pero cada pieza se monta a mano y cada vez de una forma distinta: un `piezas.html` y un `exportar.mjs` por boda, y un proyecto de HyperFrames por reel. Eso funciona, pero no escala. Este sistema cierra el hueco que hay entre «plan escrito» y «fichero final con su texto».

**Lo que se quiere**: alguien del equipo sube la carpeta de una boda a Drive, abre Claude Code y escribe «reel de la boda de La Posadilla». Al rato tiene en Drive el MP4, el texto y la cola de Metricool, listos para enviar al cliente y programar.

**Decisiones de partida** (Juan, 2026-11-06):

| Pregunta | Decisión |
|---|---|
| ¿Cómo arranca? | **A demanda.** Una persona lo pide en Claude Code. No hay vigilante programado |
| ¿Qué pieza sale? | **Piezas sueltas.** Cada orden es independiente del calendario de `semana-boda` |
| ¿Cómo se resuelven matrículas, funda antigua, chevrones y menores? | **Esquivar y recortar.** Se prefiere el material que no necesita retoque. Si hace falta, se recorta; solo cuando no hay más remedio se retoca, y queda un antes y después para revisar |
| ¿Dónde viven las piezas? | **En Drive**, en `02_Produccion/`. Las piezas sueltas no generan ficha ni PR. El repositorio solo cambia cuando cambia el sistema |

## 2. La orden

En Claude Code, en lenguaje natural:

```
reel de la boda de La Posadilla
deslizar de la boda del 24 de octubre, que salgan las cestas
historia de la última boda
3 historias de la boda de Sanlúcar, sin caras
reel sin música de la boda del 31
deslizar con rótulos de …
```

| Parte | Obligatoria | Valores |
|---|---|---|
| Formato | Sí | `reel` · `deslizar` (carrusel) · `historia` (o «N historias») |
| Boda | Sí | Fecha, lugar o «la última». Claude la busca en Drive |
| Indicaciones | No | Tema («las cestas», «el volante»), coche, «sin caras», «sin música», variante («con rótulos», «titular») |

Sin indicaciones, Claude elige el tema, el material y la variante.

## 3. Arquitectura

### 3.1 Piezas del sistema

| Pieza | Dónde | Responsabilidad |
|---|---|---|
| Skill `pieza-boda` | `.claude/skills/pieza-boda/SKILL.md` | Orquesta y **decide**: qué material, qué variante, qué rótulos, qué texto. Escribe `pieza.json` |
| Localizar Drive y boda | `herramientas/piezas/localizar.py` | Encuentra `Mehari We` en Mac o Windows y las carpetas de boda que encajan con la consulta |
| Inventario | `herramientas/piezas/inventario.py` | Recorre la carpeta de la boda (con subcarpetas) y saca miniaturas, datos técnicos, fecha EXIF y hojas de contacto en `.trabajo/<boda>/_inventario/`. **Escribe solo en la carpeta de trabajo.** Reutiliza las funciones de `herramientas/material/` sin cambiar su uso actual |
| Rejilla | `herramientas/piezas/rejilla.py` | Dibuja una rejilla de coordenadas sobre una foto o un fotograma (`--t`) para que Claude lea los recortes y los vértices de cada retoque en píxeles del original tal como se ve |
| Preparar | `herramientas/piezas/preparar.py` | Lee `pieza.json`: convierte HEIC→JPG y HLG→SDR BT.709, recorta, aplica los retoques (`retocar_foto.py`, `difuminar.py`) y copia todo a los `assets/` del proyecto de trabajo. Deja el antes y después de cada recorte o retoque y `revision/avisos.json` |
| Producir | `herramientas/piezas/producir.py` | Copia la plantilla del formato a la carpeta de trabajo, le pasa las variables y renderiza: HyperFrames para el reel y la historia en clip, y HTML + Playwright para el carrusel y la historia en foto |
| Comprobar | `herramientas/piezas/comprobar.py` | Controles automáticos (§6.1): formato de los ficheros y revisor de texto |
| Entregar | `herramientas/piezas/entregar.py` | Copia el resultado a `02_Produccion/<boda>/<pieza>/` con su `texto.txt`, `revision.html`, `cola-metricool.json` y `pieza.json` |
| Plantillas | `marca/plantillas/estaticas/` y `marca/plantillas/reel/` | `estaticas/` (HTML + Playwright) sirve para el carrusel y la historia en foto; `reel/` (HyperFrames) para el reel y la historia en clip. Cada formato tiene 2 variantes (§4) |
| Tokens | `marca/tokens.css` (ya existe) | Colores y tipografías. Las plantillas usan sus valores, sin inventar colores |
| Lo que ya existe | `herramientas/material/` | Análisis, hojas de contacto, `retocar_foto.py` (placa, emblema, funda) y `difuminar.py` |

Los scripts son Python 3 y Node, sin dependencias de un sistema operativo concreto: Juan trabaja en Mac, y el resto del equipo puede hacerlo en Windows.

### 3.2 `pieza.json`: el contrato

Es la frontera entre **decidir** (Claude) y **producir** (scripts). Claude escribe sus decisiones aquí; los scripts solo leen este fichero. Para cambiar un rótulo se edita una línea y se vuelve a ejecutar `producir.py`, sin repetir la selección.

```json
{
  "version": 1,
  "boda": "2026-10-24_la-posadilla",
  "carpeta_origen": "01_Material/Selecccion/Boda 2:11:2026",
  "formato": "deslizar",
  "variante": "con-rotulos",
  "tema": "las-cestas",
  "permiso_caras": "si",
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
  "texto": "…copy final con CTA y hashtags…",
  "a_mano_despues": ["Sticker de ubicación: Finca La Posadilla"],
  "pendientes": []
}
```

- `boda`: `AAAA-MM-DD_lugar`, con la fecha del EXIF o de la ficha (§3.3). `carpeta_origen`: la carpeta de la boda, relativa a `Mehari We`.
- `elementos[].fichero`: relativo a la carpeta de la boda. `recorte` (`x`, `y`, `ancho`, `alto`) y `retoques` van en píxeles del original **tal como se ve** (con la orientación EXIF o la rotación del vídeo aplicadas), lo mismo que enseña `rejilla.py`. Sin recorte, se encuadra centrado.
- Retoques de foto: `{"tipo": "placa" | "funda", "poligono": [[x,y], …]}` o `{"tipo": "emblema", "caja": [x, y, ancho, alto]}`. De vídeo: `{"tipo": "zona", "t", "caja": [x, y, ancho, alto], "desde"?, "hasta"?}`, con `t` en segundos del clip original y **dentro** del corte del elemento. El difuminado se aplica después de escalar a 1080×1920. Una foto solo admite `placa`, `funda` y `emblema`, y un vídeo (`.mov` o `.mp4`), solo `zona`: cualquier otro tipo o forma es un error de validación, y nunca se salta un retoque. Una zona que queda fuera del encuadre final no se difumina y deja un aviso en `revision/avisos.json`.
- Para el reel, cada elemento lleva además `tramo` (`gancho`, `detalle`, `prueba` o `momento`) y `desde` y `hasta` (segundos del clip) o `duracion` (fotos). El cierre de marca (4 s) lo añade la plantilla: no es un elemento. Con el cierre, el reel dura de 15 a 25 s.
- Cuántos elementos: deslizar, de 5 a 9 fotos (más la diapositiva de cierre, que se añade sola); historia, de 1 a 10. En la historia en clip, cada clip dura como máximo 15 s (cada elemento es una historia aparte).
- `permiso_caras`: `si` por defecto (el permiso para enseñar caras de adultos viene con el material del cliente, `CLAUDE.md` §4), `no` si la pareja ha pedido no salir, o `pendiente` si hay alguna duda. Los menores nunca salen con cara, haya permiso o no. `hay_caras`: si en la pieza se reconoce alguna cara; si falta, se supone que sí. Una pieza con caras solo puede salir `LISTA` con `permiso_caras: "si"`.
- `musica`: `{"ruta", "licencia", "titulo"?}` de la pista libre de derechos (`ruta` y `licencia` obligatorias y no vacías), o `null` si es «sin música».
- `ubicacion`: texto para la cola de Metricool, o `null`.
- `pendientes`: cada marcador `[PENDIENTE: …]` que haya quedado. Si no está vacío, la pieza no está lista.
- Lo valida `herramientas/piezas/pieza.py` (versión 1, formato y variante, `boda`, `tema`, número de elementos, duraciones, retoques, música y tipos de los textos).

### 3.3 Carpetas

| Qué | Dónde | ¿En Git? |
|---|---|---|
| Sistema (skill, scripts, plantillas) | Repositorio | Sí |
| Trabajo (miniaturas, hojas, assets, proyecto de render) | `.trabajo/<boda>/_inventario/` (uno por boda) y `.trabajo/<boda>/<pieza>/` (con `pieza.json`, `proyecto/` y `salida/`) en la raíz del repositorio | **No** (está en `.gitignore`). Se puede borrar y regenerar desde `pieza.json` |
| Material del cliente | Drive · `01_Material/…` | No. **Nunca se escribe en él** |
| Pieza terminada | Drive · `02_Produccion/<boda>/<AAAA-MM-DD>_<formato>_<tema>/` | No |

`<boda>` es `AAAA-MM-DD_<lugar>`, con la **fecha de la boda sacada del EXIF** (o de la ficha) y no del nombre de la carpeta. Los nombres de Drive no son fiables: «Boda 24:10:2026» contiene la boda del 31-10. `<AAAA-MM-DD>` en la carpeta de la pieza es la fecha en que se produce.

## 4. Formatos

Reglas comunes a todos:

- **Texto**: tuteo en plural, concreto, sin rayas largas ni «experiencia única», sin «Citroën» y sin presentar la marca como «de Sevilla». CTA a WhatsApp **625 06 42 93** y 3–5 hashtags. Los nombres, el lugar, las flores y el fotógrafo solo se ponen si salen de la ficha o se leen en la foto; si no, va un marcador `[PENDIENTE: …]`.
- **Sin repetir**: antes de elegir, Claude mira las piezas que ya hay en `02_Produccion/<boda>/` (su `pieza.json`). No repite la foto de portada ni el plano del gancho, y alterna las variantes.
- **Zonas seguras**: el texto y lo importante van en el 80 % central. Se dejan libres la franja superior y la inferior, donde Instagram pone su interfaz.

### 4.1 Reel

| | |
|---|---|
| Salida | `reel.mp4` (1080×1920, H.264, 30 fps, 15–25 s, AAC) y `portada.jpg` (fotograma que funciona recortado a 4:5) |
| Estructura | La de `guion-reel`: gancho (0–3 s, el plano con más gente y más movimiento), detalle, prueba, momento y cierre |
| Sonido | **Música libre de derechos incrustada** (la busca `media-use`), con modo `automatico` en Metricool (`publicacion-metricool.md` §3). Con «sin música», sale sin audio y en modo `aviso` |
| Material | Clips de vídeo o Live Photos. Si solo hay fotos, se montan con movimiento lento de cámara |
| Variante `limpio` | Cortes secos al pulso, rótulos pequeños abajo y en el centro |
| Variante `titular` | Rótulo grande en el gancho y transición suave entre planos |
| Cierre | `marca/animaciones/renders/cierre.mp4` (4 s), que parte del cierre animado de `marca/animaciones/` y del `cierre-corto.html` del reel del 11-11, con el logo y el nombre actuales. Termina con «Escribidnos vuestra fecha» y el WhatsApp 625 06 42 93. Lo añade la plantilla al final de los planos |

### 4.2 Deslizar (carrusel)

| | |
|---|---|
| Salida | `01.jpg` … `NN.jpg`, 1080×1440, solo JPEG (calidad 90) |
| Estructura | 6–10 diapositivas (5–9 fotos más el cierre): portada (la mejor foto de los novios con el coche y un rótulo corto) → el día en orden (iglesia, salida, cestas, volante, llegada, momento, detalle) → cierre con CTA. Si se pide un tema, todas las diapositivas giran en torno a él |
| Cierre | Lo añade la plantilla: «¿Cuándo os casáis?», «Escribidnos vuestra fecha y os decimos si hay un Méhari libre.» y «WhatsApp · 625 06 42 93». Sin año, para que valga todo el año |
| Variante `foto-entera` | Sin rótulos, salvo en la portada y el cierre |
| Variante `con-rotulos` | Una frase corta en 2–4 diapositivas |
| Técnica | Plantilla HTML con `?s=<n>` y exportación con Playwright, como `bodas/2026-10-24_la-posadilla/exportar.mjs`, generalizada en `producir.py` |

### 4.3 Historia

| | |
|---|---|
| Salida | `historia.jpg` o `historia.mp4`, 1080×1920. Con «N historias», `historia-01…NN`. En clip, cada clip dura como máximo 15 s |
| Variante `foto-frase` | Una foto con una frase («Sábado en [lugar]») |
| Variante `clip-cta` | Un clip corto con «¿Cuándo os casáis?» (el rótulo por defecto si el elemento no lleva otro) |
| Sticker | Se deja hueco. `texto.txt` dice qué sticker poner (ubicación, encuesta, pregunta o enlace a WhatsApp), porque la API no los pone. En la cola va en modo `aviso` |

## 5. Flujo de una orden

```
orden ─► localizar.py ──► 0 candidatas: pide la ruta · 2 o más: pregunta (enseña las candidatas)
      ─► inventario.py ─► .trabajo/<boda>/_inventario/ (miniaturas, hojas, fecha EXIF)
      ─► lee la ficha si existe y las piezas previas de 02_Produccion/<boda>/
      ─► Claude mira las hojas, elige el material (prioridad: sin retoque > recorte > retoque)
      ─► revision-marca de cada fichero elegido (APTA / APTA CON RETOQUE / NO APTA)
      ─► escribe pieza.json (material, recortes, retoques, rótulos, texto, música)
      ─► preparar.py ─► producir.py ─► comprobar.py   (preparar.py deja siempre revision/avisos.json y revision/preparado.json)
      ─► Claude mira el resultado final (cada diapositiva; un fotograma por escena del reel)
      ─► entregar.py ─► 02_Produccion/<boda>/<AAAA-MM-DD>_<formato>_<tema>[_PENDIENTE]/
                          ├─ reel.mp4 + portada.jpg  |  01…NN.jpg  |  historia.*
                          ├─ texto.txt
                          ├─ revision.html
                          ├─ cola-metricool.json
                          └─ pieza.json
      ─► resumen de 3 líneas en el chat: qué se ha hecho, estado y qué falta
```

`preparar.py` empieza vaciando `assets/material/` y `revision/` del proyecto, para que nunca quede material de una pasada anterior. Escribe siempre `revision/avisos.json`: una lista vacía, o un aviso por cada zona de vídeo cuyo seguimiento puede haberse perdido o que ha quedado fuera del encuadre. `entregar.py` lo exige; si falta o no es una lista de textos, no entrega nada. Al terminar escribe `revision/preparado.json` con la huella (sha256) de lo que decide el material: el formato y, por elemento, `orden`, `fichero`, `recorte`, `retoques`, `desde`, `hasta` y `duracion`. `producir.py` y `entregar.py` se niegan si falta o no coincide con el `pieza.json` que reciben: cambiar un rótulo o el texto no obliga a preparar de nuevo; cambiar el material, sí.

### 5.1 Los ficheros de la entrega

- **`texto.txt`**. Primera línea: `Estado: LISTA` o `Estado: NO PUBLICAR · <motivo>`. Después: el copy listo para pegar, lo que se hace a mano en la app (sticker, Collab, etiquetas, ubicación si Metricool no la pone) y la música usada con su licencia.
- **`revision.html`**. Página autónoma, que se abre con doble clic: la pieza, el antes y después de cada retoque o recorte, la checklist de `revision-marca` y los pendientes.
- **`cola-metricool.json`**. El mismo formato que `publicacion-metricool.md` §4, con **una sola publicación**. Va con `fecha: null`, `aprobacion.estado: "pendiente"`, `modo` según §4 y `medios` relativos a la carpeta de la pieza. Cuando el cliente aprueba, Alejandro pone la fecha y la aprobación y lanza `programar-metricool` sobre esa carpeta.
- **`pieza.json`**. Para volver a renderizar con cambios (§3.2).

### 5.2 Cambio en `programar-metricool`

Esa skill hoy da por hecho que la cola está en `redes/instagram/bodas/<boda>/` y hace commit al terminar. Se ajusta para que:

1. Acepte una cola en cualquier carpeta, también en Drive, con los `medios` relativos a esa carpeta.
2. Si la cola no está en el repositorio, actualice `metricool_id` y `estado` en el propio fichero y **se salte el commit**.
3. Se pare si `fecha` es `null`.

## 6. Controles y estados

### 6.1 Controles antes de entregar

1. **Automáticos** (`comprobar.py`, y `entregar.py` los repite). Si falla uno, no se entrega nada:
   - Formato: dimensiones, códec, fps, duración y audio AAC con ffprobe; carruseles en JPEG de 1080×1440, entre 2 y 10.
   - Texto: no contiene «Citroën», la marca antigua («Tour Sur», «toursur», «Mehari Experiences», sin distinguir mayúsculas ni tildes), rayas largas (—), «experiencia única» ni más de 5 hashtags, y sí contiene 625 06 42 93.
   - Texto incrustado: cada `rotulo`, la `ubicacion` y cada línea de `a_mano_despues` siguen las mismas reglas, salvo el teléfono y el número de hashtags.
   - Material (solo `entregar.py`; `producir.py` exige lo primero): `revision/preparado.json` corresponde al `pieza.json` actual, y cada elemento con recorte o retoques tiene su `NN_antes.jpg` y `NN_despues.jpg`.
   - Conjunto (solo `entregar.py`): los ficheros de salida son exactamente los de la pieza (ni sobran ni faltan), y `revision/avisos.json` existe y es una lista de textos.
   - Avisos que no bloquean: «Sevilla», «sevillano/a/os/as» o «Cádiz» (con o sin tilde) en cualquiera de esos textos. Nombrar el lugar de una boda está permitido; presentar la marca como de allí, no (`CLAUDE.md` §2). Claude revisa cada aviso y lo justifica en `revision.html`.
2. **Claude mira el resultado final**: cada diapositiva y un fotograma por escena del reel, buscando matrículas, la funda «@MEHARI_TOURSUR», chevrones y caras de menores que se hayan escapado.
3. **Una persona** echa un vistazo de unos 30 segundos a `revision.html` antes de enviarlo al cliente. Sigue siendo obligatorio: la pre-revisión no sustituye a la revisión (`automatizacion-contenido.md` §6).

Se entrega, pero como `NO PUBLICAR` (carpeta `_PENDIENTE`), si hay caras sin `permiso_caras: "si"`, si quedan marcadores `[…]` en el texto, en los rótulos, en la ubicación o en `a_mano_despues`, o datos en `pendientes`, o si hay avisos de difuminado.

**Sin aprobación del cliente no se programa nada.** Este sistema no cambia esa regla.

### 6.2 Casos

| Caso | Qué hace |
|---|---|
| No encuentra la boda, o coinciden varias | Pregunta y enseña las candidatas. Nunca adivina |
| Drive no está sincronizado, o la ruta es distinta | Busca en las rutas habituales de Mac (`~/Library/CloudStorage/GoogleDrive-*/My Drive/` o `Mi unidad/`) y Windows (`G:\Mi unidad\`, `G:\My Drive\`). Si no encuentra `Mehari We`, pide la ruta. Se puede fijar con la variable de entorno `MEHARI_DRIVE` (otra letra de unidad, una unidad compartida…). Drive para Windows escribe los «:» de los nombres como «_» («Boda 24_10_2026»): también se reconocen |
| Caras | El permiso de caras de adultos viene con el material: `permiso_caras: "si"`. Si la pareja ha pedido no salir, `"no"` y la pieza sale `NO PUBLICAR · falta permiso de caras`. Menores con cara, nunca: se descarta, se recorta o se difumina. Con «sin caras», elige solo detalles: coche, cestas, manos, de espaldas |
| Faltan datos (iglesia, flores, fotógrafo) | Marcador `[PENDIENTE: …]` en el texto. La pieza queda `_PENDIENTE` |
| Poco material | El carrusel baja hasta 6 diapositivas; por debajo, avisa y propone una historia. El reel se monta con fotos si no hay clips |
| Funda, matrícula o menor imposible de esquivar o recortar | Se retoca. Si el retoque se nota o no se puede hacer, **la foto se descarta**. Nunca sale una pieza con rastro |
| Zona de vídeo fuera del corte | Si el `t` de una zona queda fuera del `desde`–`hasta` del elemento, `preparar.py` para antes de procesar nada. Se vuelve a marcar con `rejilla.py --t` dentro del corte |
| Zona de vídeo fuera del encuadre final | No se difumina: `preparar.py` lo apunta en `revision/avisos.json` y la pieza queda `NO PUBLICAR`. Se comprueba la caja con `rejilla.py --t` y se corrige, o se cambia el recorte |
| Seguimiento del difuminado perdido | `preparar.py` lo apunta en `revision/avisos.json`; sale en `revision.html` y la pieza queda `NO PUBLICAR`. Se añade otra zona, se acorta el corte o se cambia de plano, y se vuelve a preparar |
| Fichero en Drive «solo en la nube» | Leerlo fuerza la descarga. Puede tardar, pero no es un error |
| El render falla | `hyperframes check`, se corrige y se repite una vez. Si sigue fallando, no se entrega nada a medias y se explica el error |
| Ya existe una carpeta con ese nombre | Se añade `-2`, `-3`… Nunca se sobrescribe una entrega |

## 7. Pruebas

- **Scripts** (pytest, en `herramientas/piezas/tests/`):
  - `localizar.py` con rutas de Mac y Windows simuladas, y nombres como «Boda 24:10:2026» o `2026-11-07_sanlucar`.
  - Validación de `pieza.json`: campos obligatorios, formato y variante válidos.
  - `comprobar.py`: cada regla del revisor de texto con un caso que pasa y otro que falla, y el formato de un JPEG y un MP4 de muestra.
  - `entregar.py`: estado `LISTA` frente a `_PENDIENTE`, nombre sin sobrescribir y `cola-metricool.json` válido según `publicacion-metricool.md` §4.
- **Prueba real con La Posadilla** (24-10-2026, ya sincronizada en el Mac de Juan): se lanzan «deslizar», «reel» e «historia» y se comparan con su plan, que ya tiene las fotos aptas identificadas. Se da por buena si las tres piezas llegan a `02_Produccion/2026-10-24_la-posadilla/`, pasan los controles y cada una tarda menos de unos 15 minutos.

## 8. Orden de construcción

1. Scripts comunes (`localizar`, `inventario`, `comprobar`, `entregar`) con sus pruebas.
2. Plantilla de **deslizar** y de **historia en foto**, con `preparar` y `producir` para estáticos. Es lo que antes da valor y no necesita HyperFrames.
3. Plantilla del **reel**, con música incrustada.
4. **Historia en clip**.
5. Ajuste de `programar-metricool` (§5.2).
6. Skill `pieza-boda` y documentación en el mismo PR: `SKILLS.md`, `CLAUDE.md` §5 y §7, `docs/decisiones.md`, `.gitignore` (`.trabajo/`) y `herramientas/piezas/README.md`.

## 9. Fuera de alcance

- Detectar carpetas nuevas en Drive sin que nadie lo pida (se descartó el vigilante programado).
- Publicar o programar: lo hace `programar-metricool` tras la aprobación del cliente.
- Las piezas fijas de la semana de cada boda: siguen con `semana-boda`. Más adelante, `semana-boda` podrá usar estas plantillas para producir sus piezas, pero no entra en esta versión.
- Turismo (Sevilla Experience): las plantillas sirven, pero la orden y el texto están pensados para bodas.

## 10. Recomendación para Drive

Para las bodas nuevas, usar el nombre `01_Material/Bodas/AAAA-MM-DD_<lugar>/` que ya fija `semana-boda.md` §6. La skill seguirá encontrando las carpetas con nombres antiguos («Boda 24:10:2026», `Selecccion/`), pero un nombre fiable ahorra la pregunta de «¿cuál de estas?».
