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
| Inventario | `herramientas/piezas/inventario.py` | Recorre la carpeta de la boda (con subcarpetas) y saca miniaturas, datos técnicos, fecha EXIF y hojas de contacto. **Escribe solo en la carpeta de trabajo.** Reutiliza las funciones de `herramientas/material/` sin cambiar su uso actual |
| Preparar | `herramientas/piezas/preparar.py` | Lee `pieza.json`: convierte HEIC→JPG y HLG→SDR BT.709, recorta, aplica los retoques (`retocar_foto.py`, `difuminar.py`) y copia todo a los `assets/` del proyecto de trabajo |
| Producir | `herramientas/piezas/producir.py` | Copia la plantilla del formato a la carpeta de trabajo, le pasa las variables y renderiza: HyperFrames para el reel y la historia en clip, y HTML + Playwright para el carrusel y la historia en foto |
| Comprobar | `herramientas/piezas/comprobar.py` | Controles automáticos (§6.1): formato de los ficheros y revisor de texto |
| Entregar | `herramientas/piezas/entregar.py` | Copia el resultado a `02_Produccion/<boda>/<pieza>/` con su `texto.txt`, `revision.html`, `cola-metricool.json` y `pieza.json` |
| Plantillas | `marca/plantillas/{reel,deslizar,historia}/` | Una plantilla por formato, con 2 variantes cada una (§4) |
| Tokens | `marca/tokens.css` (ya existe) | Colores y tipografías. Las plantillas los leen de ahí; no se copian |
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
  "permiso_caras": "pendiente",
  "musica": null,
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

- Para el reel, cada elemento lleva además `desde` y `hasta` (segundos del clip) y `tramo` (gancho, detalle, prueba, momento o cierre).
- `permiso_caras`: `si` (la ficha lo confirma), `no` o `pendiente`. Solo con `si` puede salir `LISTA` una pieza con caras de los novios.
- `musica`: ruta y licencia de la pista libre de derechos, o `null` si es «sin música».
- `pendientes`: cada marcador `[PENDIENTE: …]` que haya quedado. Si no está vacío, la pieza no está lista.

### 3.3 Carpetas

| Qué | Dónde | ¿En Git? |
|---|---|---|
| Sistema (skill, scripts, plantillas) | Repositorio | Sí |
| Trabajo (miniaturas, hojas, assets, proyecto de render) | `.trabajo/<boda>/<pieza>/` en la raíz del repositorio | **No** (se añade a `.gitignore`). Se puede borrar y regenerar desde `pieza.json` |
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
| Cierre | Parte del cierre animado de `marca/animaciones/` y del `cierre-corto.html` del reel del 11-11, que ya llevan el logo y el nombre actuales. Termina con «Escribidnos · 625 06 42 93» |

### 4.2 Deslizar (carrusel)

| | |
|---|---|
| Salida | `01.jpg` … `NN.jpg`, 1080×1440, solo JPEG (calidad 90) |
| Estructura | 6–10 diapositivas: portada (la mejor foto de los novios con el coche y un rótulo corto) → el día en orden (iglesia, salida, cestas, volante, llegada, momento, detalle) → cierre con CTA. Si se pide un tema, todas las diapositivas giran en torno a él |
| Variante `foto-entera` | Sin rótulos, salvo en la portada y el cierre |
| Variante `con-rotulos` | Una frase corta en 2–4 diapositivas |
| Técnica | Plantilla HTML con `?s=<n>` y exportación con Playwright, como `bodas/2026-10-24_la-posadilla/exportar.mjs`, generalizada en `producir.py` |

### 4.3 Historia

| | |
|---|---|
| Salida | `historia.jpg` o `historia.mp4` (≤15 s), 1080×1920. Con «N historias», `historia-01…NN` |
| Variante `foto-frase` | Una foto con una frase («Sábado en [lugar]») |
| Variante `clip-cta` | Un clip corto con «¿Cuándo os casáis?» |
| Sticker | Se deja hueco. `texto.txt` dice qué sticker poner (ubicación, encuesta, pregunta o enlace a WhatsApp), porque la API no los pone. En la cola va en modo `aviso` |

## 5. Flujo de una orden

```
orden ─► localizar.py ──► 0 candidatas: pide la ruta · 2 o más: pregunta (enseña las candidatas)
      ─► inventario.py ─► .trabajo/<boda>/_inventario/ (miniaturas, hojas, fecha EXIF)
      ─► lee la ficha si existe y las piezas previas de 02_Produccion/<boda>/
      ─► Claude mira las hojas, elige el material (prioridad: sin retoque > recorte > retoque)
      ─► revision-marca de cada fichero elegido (APTA / APTA CON RETOQUE / NO APTA)
      ─► escribe pieza.json (material, recortes, retoques, rótulos, texto, música)
      ─► preparar.py ─► producir.py ─► comprobar.py
      ─► Claude mira el resultado final (cada diapositiva; un fotograma por escena del reel)
      ─► entregar.py ─► 02_Produccion/<boda>/<AAAA-MM-DD>_<formato>_<tema>[_PENDIENTE]/
                          ├─ reel.mp4 + portada.jpg  |  01…NN.jpg  |  historia.*
                          ├─ texto.txt
                          ├─ revision.html
                          ├─ cola-metricool.json
                          └─ pieza.json
      ─► resumen de 3 líneas en el chat: qué se ha hecho, estado y qué falta
```

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

1. **Automáticos** (`comprobar.py`). Si falla uno, no se entrega:
   - Formato: dimensiones, códec, fps, duración y peso con ffprobe; carruseles en JPEG de 1080×1440, entre 2 y 10.
   - Texto: no contiene «Citroën», rayas largas (—), «experiencia única» ni más de 5 hashtags, y sí contiene 625 06 42 93. Los marcadores `[…]` no impiden la entrega, pero ponen el estado en `NO PUBLICAR`.
   - Avisos que no bloquean: «Sevilla», «sevillano» o «Cádiz» en el texto. Nombrar el lugar de una boda está permitido; presentar la marca como de allí, no (`CLAUDE.md` §2). Claude revisa cada aviso y lo justifica en `revision.html`.
2. **Claude mira el resultado final**: cada diapositiva y un fotograma por escena del reel, buscando matrículas, la funda «@MEHARI_TOURSUR», chevrones y caras de menores que se hayan escapado.
3. **Una persona** echa un vistazo de unos 30 segundos a `revision.html` antes de enviarlo al cliente. Sigue siendo obligatorio: la pre-revisión no sustituye a la revisión (`automatizacion-contenido.md` §6).

**Sin aprobación del cliente no se programa nada.** Este sistema no cambia esa regla.

### 6.2 Casos

| Caso | Qué hace |
|---|---|
| No encuentra la boda, o coinciden varias | Pregunta y enseña las candidatas. Nunca adivina |
| Drive no está sincronizado, o la ruta es distinta | Busca en las rutas habituales de Mac (`~/Library/CloudStorage/GoogleDrive-*/My Drive/` o `Mi unidad/`) y Windows (`G:\Mi unidad\`, `G:\My Drive\`). Si no encuentra `Mehari We`, pide la ruta. Se puede fijar con la variable de entorno `MEHARI_DRIVE` |
| No hay ficha, o no consta el permiso de caras | Produce la pieza y la marca `NO PUBLICAR · falta permiso de caras`. Con «sin caras», elige solo detalles: coche, cestas, manos, de espaldas |
| Faltan datos (iglesia, flores, fotógrafo) | Marcador `[PENDIENTE: …]` en el texto. La pieza queda `_PENDIENTE` |
| Poco material | El carrusel baja hasta 6 diapositivas; por debajo, avisa y propone una historia. El reel se monta con fotos si no hay clips |
| Funda, matrícula o menor imposible de esquivar o recortar | Se retoca. Si el retoque se nota o no se puede hacer, **la foto se descarta**. Nunca sale una pieza con rastro |
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
