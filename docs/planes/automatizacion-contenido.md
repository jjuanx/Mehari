# Automatización de la producción y la publicación — [MARCA POR DEFINIR]

| Campo | Valor |
|---|---|
| Versión | 1 (investigación del equipo, **pendiente de decidir** qué opción de publicación pilotamos) |
| Fecha | 2026-10-07 |
| Relacionado | [workflow-contenido.md](workflow-contenido.md) (el flujo completo, que este documento no sustituye) · [estrategia-instagram.md](estrategia-instagram.md) · skills `guion-reel`, `nueva-publicacion`, `revision-marca`, `hyperframes` |

El [workflow de contenido](workflow-contenido.md) fija **qué** pasa desde una boda hasta que se publica. Este documento investiga **cuánto de eso puede hacer Claude solo**: recibir las fotos y vídeos del cliente, montarlos (reels, carruseles, stories) y dejarlos programados en Instagram y otras redes.

---

## 0. Resumen

1. **Se puede automatizar casi toda la cadena**: ordenar y revisar el material, montar las piezas con plantillas de HyperFrames y programarlas por API. La API oficial de Instagram publica fotos, carruseles, reels y stories.
2. **Dos pasos siguen siendo humanos, a propósito**: confirmar que una foto no tiene rastros de la marca antigua y el visto bueno del cliente. **Nada se publica sin aprobación.**
3. **La API no lo hace todo.** La música en tendencia, los stickers y los enlaces de las stories, y los filtros siguen siendo manuales en la app.
4. **La mayor ganancia está en producir, no en publicar.** Programar una pieza a mano lleva unos minutos. Montar un reel lleva horas, y es ahí donde las plantillas con variables y el render por lotes ahorran tiempo.
5. **Recomendación**: en el lanzamiento (semanas 1–4) publicamos a mano con Meta Business Suite, como dice el workflow, y en paralelo **automatizamos la producción** y probamos la publicación por API **en una cuenta de pruebas**. En la semana 5 elegimos la opción de publicación (§4).

## 1. Qué automatizamos y qué no

| Fase del workflow | Hoy (workflow v1) | Con automatización | Quién decide |
|---|---|---|---|
| 1–2 · Entrada de material | El cliente sube a Drive | Igual. Claude detecta las carpetas nuevas | Cliente |
| 3 · Ingesta y curación | Revisión a mano foto a foto | Claude hace el **inventario** y una **pre-revisión** de marca; el equipo confirma solo las dudosas | **Equipo** (confirma) |
| 4 · Producción | Cada reel se monta desde cero | **Plantillas** con variables y **render por lotes** | Claude, con revisión del equipo |
| 5–6 · Aprobación | Envío semanal por WhatsApp o Drive | Página de aprobación del lote generada sola | **Cliente** |
| 7–8 · Programación | Meta Business Suite a mano | **Cola de publicación** que se programa por API | Equipo (pulsa "programar") |
| 12 · Medición | Insights a mano | Métricas por API para el informe mensual | — |

> **Regla**: la automatización prepara y propone, pero las dos decisiones en negrita son de una persona. Una foto con una funda "@MEHARI_TOURSUR" publicada por error rompe la regla 1 de `CLAUDE.md` §4, y no se arregla borrando el post.

## 2. La cadena propuesta

```
 Drive (Bodas/AAAA-MM-DD_lugar/)
        │  sincronizado en local con Google Drive para escritorio
        ▼
 [1] INGESTA ── inventario.json + pre-revisión de marca (APTA / RECORTE / NO / DUDOSA)
        │                    └─► el equipo confirma las DUDOSAS
        ▼
 [2] PRODUCCIÓN ── plantillas HyperFrames + variables ── render por lotes
        │          (reel, carrusel, story, portada)       MP4 y JPEG fuera de Git
        ▼
 [3] REVISIÓN ── PR con fichas y previsualizaciones (otro miembro del equipo)
        ▼
 [4] APROBACIÓN ── lote semanal al cliente ── "OK" o cambios
        ▼
 [5] COLA ── redes/instagram/cola.json (pieza, fecha, copy, ficheros)
        ▼
 [6] PUBLICACIÓN ── API (opción B o C de §4) o Meta Business Suite (opción A)
        ▼
 [7] MÉTRICAS ── Insights por API ─► informe-mensual
```

### 2.1 Ingesta: inventario y pre-revisión

- **Cómo llega el material a Claude**: Google Drive para escritorio sincroniza la carpeta compartida en el ordenador. Claude trabaja con ficheros locales, que es lo más práctico para vídeos de cientos de MB. El conector de Google Drive de Claude sirve para buscar y leer, pero no para mover vídeos grandes.
- **Datos técnicos** (script con `ffprobe`): orientación, resolución, duración, fecha de captura, si tiene audio. Marca como **"comprimida"** cualquier foto de 1600 px o menos de lado largo: casi seguro que ha pasado por WhatsApp. *Todas las fotos de `Referencia/` vienen de WhatsApp*, así que hay que pedir los originales (ya está en el workflow §5, punto 5).
- **Lectura visual** (Claude ve las imágenes y fotogramas de los vídeos): qué coche sale (naranja o beige), qué escena es (iglesia, hacienda, cestas con flores, novios al volante, ruta por Sevilla), si hay caras y **cualquier rastro de la marca antigua** (fundas de rueda, pegatinas, la "M", marcas de agua).
- **Salida**: `inventario.json` en la carpeta de la boda (no en Git) y un resumen en Markdown con una tabla por fichero y su resultado provisional de `revision-marca`. El equipo solo mira las marcadas como **DUDOSA** o **RECORTE**.

### 2.2 Producción por plantillas

Hoy cada reel se guioniza y monta a medida con `guion-reel`. Eso tiene sentido para las piezas de marca, pero el contenido que más se repite (una boda nueva, una ruta de turismo) puede salir de **plantillas**: una composición de HyperFrames cuyas fotos, textos y colores son **variables**. Después se renderizan muchas versiones de una vez:

```bash
npx hyperframes render --batch filas.json --output "renders/{name}.mp4"
```

Plantillas que proponemos (una por cada formato que se repite):

| Plantilla | Formato | Variables | Skill de base |
|---|---|---|---|
| `reel-boda` | 9:16, 15–25 s, sincronizado con la música | 6–10 fotos o clips, coche, lugar, CTA | `music-to-video` |
| `reel-turismo` | 9:16, 15–25 s, **ES y EN** | fotos de la ruta, tour (Monumental o Romántico), idioma | `general-video` |
| `carrusel` | 4:5 (1080×1350), 5–10 diapositivas JPEG | foto y texto por diapositiva | `hyperframes-core` (fotograma fijo) |
| `story-cta` | 9:16 imagen o vídeo de 5–10 s | foto, frase, CTA a WhatsApp | `motion-graphics` |
| `portada-reel` | 9:16 con zona segura 4:5 para la rejilla | fotograma, título | `motion-graphics` |

- **Identidad**: mientras no haya marca (`CLAUDE.md` §9), las plantillas usan una paleta neutra y `[MARCA POR DEFINIR]`. Cuando exista `marca/`, los colores y tipografías se leen de ahí y **todas las piezas se actualizan con un solo render**.
- **Alternativa para piezas estáticas**: Canva (hay conector con Claude). Útil si el cliente quiere retocar un carrusel él mismo. Para vídeo nos quedamos con HyperFrames.
- **Especificaciones de salida** (que la API acepte el fichero a la primera):
  - Vídeo: MP4 H.264 con audio AAC, 1080×1920, 30 fps. Reels de hasta 300 MB y stories de hasta 60 s y 100 MB.
  - Imagen: **solo JPEG** (la API rechaza PNG). En un carrusel, todas las diapositivas se recortan a la proporción de la primera.
  - Copy: máximo 2.200 caracteres y **5 hashtags** (decisión del equipo del 2026-10-07).
- **Música**: el MP4 sale con la música ya mezclada, sacada de una biblioteca libre de derechos. Si un reel necesita una canción en tendencia de Instagram, se publica a mano desde la app (ver §3).
- **Antipatrón**: una sola plantilla repetida cada semana cansa. Hay que rotar 2–3 variantes por formato y seguir haciendo piezas a medida con `guion-reel` para lo importante (lanzamiento, prensa, Herrera).

### 2.3 Revisión y aprobación

- **Equipo**: igual que ahora, un PR por lote con las fichas de `nueva-publicacion` y enlaces a las previsualizaciones. Lo revisa otro miembro.
- **Cliente**: se puede generar una **página de aprobación del lote**: los vídeos y carruseles de la semana con su copy y, debajo de cada uno, los botones "OK" y "Cambios" con un campo de texto. Claude lee las respuestas y solo pasan a la cola las piezas aprobadas. Es opcional: si el cliente prefiere WhatsApp, seguimos con WhatsApp.

## 3. Lo que la API de Instagram puede y no puede hacer

La API oficial (*Instagram Platform, Content Publishing*) funciona con **cuentas profesionales** (de empresa o de creador).

| Puede | No puede (se hace a mano en la app) |
|---|---|
| Publicar foto, carrusel de hasta 10 elementos, reel y story | Música en tendencia de la biblioteca de Instagram (solo un subconjunto autorizado para terceros, y depende de la herramienta) |
| Programar (con una herramienta o con nuestra cola) | Stickers interactivos y **enlaces en stories** |
| Copy, ubicación y texto alternativo (no en reels ni stories) | Filtros de Instagram y etiquetas de compra |
| Reels de prueba (*trial reels*), que solo ven los no seguidores | — |
| Leer métricas (Insights) | — |

- **Límite**: 100 publicaciones por API cada 24 h. Un carrusel cuenta como una. Nosotros publicamos 4 a la semana, así que no nos afecta.
- **Requisito técnico importante**: la API no recibe el fichero, sino **una URL pública** desde la que lo descarga. Hace falta alojar los MP4 y JPEG en algún sitio accesible (un *bucket* o la propia web cuando exista). Los vídeos grandes admiten subida reanudable. Las herramientas de la opción B se encargan de esto por nosotros.
- **Colaboraciones (Collab)** con el fotógrafo o la hacienda: **comprobar en el piloto** si la herramienta elegida las admite. Si no, esas piezas se publican a mano.

## 4. Opciones para publicar

| | **A · Meta Business Suite** (plan actual) | **B · Herramienta con API y conector para Claude** | **C · App propia de Meta** |
|---|---|---|---|
| Qué es | Programar a mano desde el navegador | Un servicio intermediario (Upload-Post, Late, PostEverywhere, Post Bridge…) que publica por nosotros. Claude lo usa por MCP o por API | Nuestra propia app de Meta con la API de Instagram y un script `publicar` que lee la cola |
| Coste | Gratis | Upload-Post: plan gratis de 10 subidas al mes y desde unos 16–24 $/mes. Late: desde 13 $/mes. Ayrshare: desde 149 $/mes | Gratis (más el alojamiento de ficheros, unos céntimos) |
| Puesta en marcha | Ninguna | Minutos: conectar la cuenta y añadir el MCP a Claude Code | Días: app de Meta, permisos, alojamiento, script y tarea programada |
| Revisión de Meta | No | No (la tiene el intermediario) | **No**, si solo publica en una cuenta que gestionamos nosotros (acceso estándar) |
| Otras redes | Facebook | **TikTok, Facebook, YouTube Shorts…** con la misma llamada | Solo Meta. TikTok requeriría su propia app y una auditoría de 2–6 semanas |
| Música en tendencia, stickers, Collab | **Sí** | Parcial | Parcial |
| Riesgo | Tiempo del equipo | Un tercero guarda el acceso a la cuenta del cliente y dependemos de su servicio | Mantenimiento nuestro. El token caduca cada 60 días y hay que renovarlo |

Metricool, muy usada en España, está a medio camino entre A y B: tiene calendario visual y métricas, publica posts, reels y stories solos (hasta 50 al día) y avisa al móvil para lo que hay que publicar a mano. Su integración con Claude depende del plan; si interesa, **hay que comprobarlo**.

**Recomendación**

- **Semanas 1–4: A.** La cuenta es nueva y aún no sabemos qué formatos funcionan, así que no merece la pena añadir piezas móviles. Además, publicar a mano permite usar música en tendencia y Collab desde el primer día. Como precaución, tampoco conviene que una cuenta recién creada empiece publicando solo por API.
- **En paralelo**: montar la producción automática (§2.1 y §2.2) y probar **B con el plan gratis en una cuenta de Instagram de pruebas**, nunca en la del cliente.
- **Semana 5, decidir**:
  - **B** si TikTok entra en el alcance (`CLAUDE.md` §9) o si queremos lo más rápido. Es la opción natural para trabajar desde Claude Code.
  - **C** si ya se está tramitando la app de Meta para la fase 2 del panel de solicitudes ([workflow](workflow-contenido.md) §10–11). Sería **la misma app**, y así el acceso a la cuenta del cliente no pasa por un tercero.

## 5. Claude trabajando solo: skills y tareas programadas

Siguiendo la norma de que lo que se repite dos veces se convierte en skill, la automatización se traduce en tres skills nuevas (ver `SKILLS.md`, ideas):

| Skill | Qué hace | Entrada → salida |
|---|---|---|
| `ingesta-material` | Inventario técnico y visual y pre-revisión de marca de una carpeta de boda | Carpeta de Drive → `inventario.json` + resumen |
| `lote-semanal` | Elige material del inventario según el calendario, rellena las plantillas, renderiza por lotes y crea las fichas | Inventario + calendario → MP4/JPEG + fichas + PR |
| `publicar` | Pasa las piezas aprobadas a la cola y las programa con la opción elegida en §4 | Cola → publicaciones programadas |

**¿Se puede ejecutar solo, sin pedírselo?** Claude Code permite tareas programadas (`/schedule` en la nube y `/loop` en local). Por ejemplo: "cada lunes, mira si hay bodas nuevas en el Drive y deja preparado el lote". Pero el render necesita Node.js y FFmpeg y el material está en local, así que **de momento proponemos ejecutarlo a demanda** ("lunes de producción", una persona del equipo lanza `lote-semanal`). La programación automática se valora cuando el proceso sea estable.

## 6. Riesgos y reglas

1. **Nunca se publica nada sin la aprobación del cliente**, aunque la cadena lo permita técnicamente. La cola solo acepta piezas con estado "Aprobada".
2. **Credenciales fuera de Git**: tokens y claves en un `.env` local (incluido en `.gitignore`). No se pegan en fichas, PR ni chats.
3. **Material comprimido**: una plantilla bonita con fotos de WhatsApp se ve mal en pantalla completa. Hay que pedir originales.
4. **Pre-revisión ≠ revisión**: Claude puede pasar por alto una pegatina pequeña. La confirmación humana de `revision-marca` sigue siendo obligatoria.
5. **Dependencia de terceros (opción B)**: si el servicio cae o cambia de precio, volvemos a A sin perder nada. Por eso la fuente de verdad son nuestra cola y nuestras fichas, no la herramienta.

## 7. Requisitos para empezar

- [ ] **FFmpeg** en cada ordenador (en Mac: `brew install ffmpeg`). En el de Juan **no está instalado** (Node.js 24 sí).
- [ ] Una **cuenta de Instagram profesional de pruebas** para el piloto de publicación.
- [ ] Google Drive para escritorio con la carpeta compartida sincronizada.
- [ ] Originales de las fotos y los vídeos de bodas anteriores (workflow §5, punto 5).
- [ ] Para la opción C: cuenta de desarrollador de Meta y un sitio donde alojar los ficheros.

## 8. Piloto propuesto

1. Instalar FFmpeg y montar la plantilla `reel-boda` con 6–8 fotos **APTAS** de `Referencia/` y la marca provisional.
2. Renderizar por lotes 3 variantes (coche naranja, coche beige y una versión en inglés para turismo) y medir el tiempo frente a montar una a mano.
3. Pasar una carpeta de `Referencia/` por la ingesta y comprobar si la pre-revisión detecta las fundas antiguas.
4. Publicar 2–3 piezas en la cuenta de pruebas con la opción B (plan gratis). Si da tiempo, también con C.
5. Anotar lo que la API no permitió hacer y llevar la decisión de §4 a la reunión de la semana 5.

## 9. Decisiones pendientes

- [ ] Opción de publicación: A, B o C (semana 5). → `CLAUDE.md` §9.
- [ ] Si TikTok entra en el alcance (condiciona B frente a C).
- [ ] Si se ofrece al cliente la página de aprobación o seguimos con WhatsApp.
- [ ] Quién del equipo hace el "lunes de producción".

## Fuentes

- Meta: [Content Publishing (Instagram Platform)](https://developers.facebook.com/docs/instagram-platform/content-publishing) · [IG User Media](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media) · [App Review for Instagram API](https://developers.facebook.com/docs/instagram-platform/app-review)
- Guías de la API: [Postproxy, reels por API](https://postproxy.dev/blog/instagram-reels-api-publishing-guide/) · [Upload-Post, guía 2026](https://www.upload-post.com/instagram-api/) · [Outstand, reels y stories](https://www.outstand.so/blog/instagram-reels-stories-api)
- Música en terceros: [Later, audio en reels](https://help.later.com/hc/en-us/articles/42098148094871-Add-Audio-to-Instagram-Reels)
- Herramientas con MCP: [PostEverywhere](https://github.com/posteverywhere/mcp) · [PostOnce instagram-mcp](https://github.com/postoncehq/instagram-mcp) · [Post Bridge](https://www.post-bridge.com/claude-code) · [PostFast](https://postfa.st/api-integrations/claude-code)
- Precios: [Upload-Post, comparativa](https://www.upload-post.com/pricing-comparison) · [Late frente a Ayrshare](https://getlate.dev/ayrshare-vs-late)
- Metricool: [Programar y publicar en Instagram](https://help.metricool.com/es/programar-y-publicar-en-instagram-6b6q5)
- Meta Business Suite: [guía de SocialKit](https://socialk.it/es/blog/meta-business-suite-guide)
- TikTok: [Postproxy, publicar por API](https://postproxy.dev/blog/how-to-post-to-tiktok-via-api/) · [bundle.social, aprobación de la API](https://bundle.social/blog/tiktok-api-approval)
- HyperFrames: `.claude/skills/hyperframes-cli/SKILL.md` (render por lotes con variables)
