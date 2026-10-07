# Workflow de contenido y captación — [MARCA POR DEFINIR]

| Campo | Valor |
|---|---|
| Versión | 1 (propuesta del equipo, **pendiente de validar con el cliente** en la reunión del 14-10-2026) |
| Fecha | 2026-10-07 |
| Relacionado | [estrategia-instagram.md](estrategia-instagram.md) (embudo, indicadores, publicidad) · skills `guion-reel`, `nueva-publicacion`, `revision-marca` |
| Presentación | [presentacion-reunion-2026-10-14.pdf](presentacion-reunion-2026-10-14.pdf) (versión para el cliente, 14 diapositivas) |

Qué pasa desde que termina una boda hasta que sabemos cuántas parejas nos han pedido disponibilidad gracias a ella. El principio de diseño es que **el cliente solo tenga que hacer dos cosas: pasarnos el material y aprobar**. Lo demás lo llevamos nosotros.

---

## 1. Vista general

```
 CLIENTE                         EQUIPO                                   INSTAGRAM / WHATSAPP
 ───────                         ──────                                   ────────────────────
 1. Boda ──► 2. Sube material ─► 3. Ingesta y curación
             (Drive + ficha)        (revision-marca: APTA / RECORTE / NO)
                                 4. Producción
                                    (guion-reel + HyperFrames,
                                     nueva-publicacion)
 6. Aprueba ◄──────────────────  5. Envío a aprobación (lote semanal)
             ──────────────────► 7. Programación ─────────────────────► 8. Publicación
                                    (Meta Business Suite)                   (reel, carrusel, stories)
                                                                         9. La pareja escribe
 10. Responde y presupuesta ◄────────────────────────────────────────────── (WhatsApp / DM, con código de pieza)
             ──────────────────► 11. Panel de solicitudes en la web (automático)
                                 12. Informe semanal y mensual ──────────► ajustes de contenido y de Ads
```

## 2. Las fases

### 1–2 · Entrada de material (cliente)

- **Dónde**: una carpeta compartida de Google Drive, una subcarpeta por boda: `Bodas/AAAA-MM-DD_lugar/` con `fotos/`, `videos/` y `ficha`. Es el canal más fácil para el cliente desde el móvil y cubre el pendiente de "dónde compartir los ficheros pesados" (`CLAUDE.md` §9).
- **Cuándo**: en los 2 días siguientes a la boda.
- **Ficha de la boda** (formulario corto o nota en la carpeta): fecha, iglesia y hacienda, coche (naranja o beige), con chófer o conducido por los novios, fotógrafo y su usuario de Instagram, wedding planner y florista si los hay, y **consentimiento de la pareja** para publicar su imagen.
- **Lista de planos para el día de la boda** (la llevan el chófer o el cliente; móvil en **vertical**):
  1. El coche esperando en la puerta de la iglesia (5 s, quieto).
  2. La salida de los novios y los invitados alrededor (10–15 s).
  3. Desde dentro: manos al volante y la carretera (5–10 s).
  4. Las cestas con las flores (detalle, 5 s).
  5. Llegada a la hacienda (plano general, 10 s).
  6. Sonido real: motor, campanas, aplausos (sin música de fondo).
- **Además**: pedir a las parejas y a los fotógrafos sus vídeos y fotos, y crédito al fotógrafo siempre.

### 3 · Ingesta y curación (equipo)

- Se descarga a local; **nada pesado entra en Git** (`.gitignore`).
- Selección de las mejores piezas y revisión con la skill **`revision-marca`**: fundas de rueda, pegatinas, la "M" antigua y marcas de agua. Resultado por foto o clip: APTA, APTA CON RECORTE o NO APTA.
- Se comprueba la ficha: sin consentimiento de la pareja no se publican caras.

### 4 · Producción (equipo)

Cada boda rinde, como mínimo, un lote de 3 piezas:

| Pieza | Herramienta | Para qué |
|---|---|---|
| **Reel** de 15–30 s | Skill `guion-reel` → HyperFrames (`general-video` / `music-to-video`) | Alcance: es lo que más reparte Instagram |
| **Carrusel** de 5–10 fotos | Skill `nueva-publicacion` (+ `social` para el marco) | Guardados y explicar el servicio |
| **Stories** del día | Directo desde el móvil | Cercanía y llevar a WhatsApp |

- Fuente del reel en `redes/instagram/reels/<fecha>_<tema>/` (versionada); el MP4 exportado, fuera de Git.
- Ficha de cada publicación en `redes/instagram/publicaciones/` con objetivo, copy, hashtags (máximo 5) y **código de pieza** (ver fase 9).
- Todo pasa por `revision-marca` antes de enviarse a aprobación.

### 5–6 · Aprobación (cliente)

- **Un envío por semana** con el lote de la semana: los MP4 y las imágenes por WhatsApp o en la carpeta `Aprobación/` del Drive, con el texto de cada publicación.
- El cliente responde **"OK"** o con cambios concretos. Plazo propuesto: 48 h; si no hay respuesta, se mueve la publicación, no se publica sin visto bueno.

### 7–8 · Programación y publicación (equipo)

- **Meta Business Suite** (gratis): programa reels, carruseles e historias en Instagram (y Facebook si se quiere).
- En cada publicación: ubicación, etiquetas al fotógrafo, la hacienda y la iglesia; **Collab** con el fotógrafo o la hacienda cuando acepten (la pieza sale en los dos perfiles).
- Ritmo según la estrategia: 4 publicaciones a la semana en el lanzamiento, 3–4 después.

### 9 · Captación: la pareja escribe

- **Enlaces de WhatsApp que pasan por la web**: en la bio, las historias y cada publicación, el enlace es de nuestra web (`[dominio]/w/<código>`). La web registra el clic con su origen y redirige a `wa.me/[WHATSAPP POR DEFINIR]` con el mensaje ya escrito ("Hola, quiero disponibilidad para mi boda").
- **Código de pieza**: cada publicación con llamada a la acción tiene su código (`NARANJA`, `FLORES`…), que va en el enlace y en la palabra clave ("escríbenos *NARANJA*"). Así sabemos qué pieza ha traído cada conversación sin preguntar nada.
- **Respuestas rápidas** de WhatsApp Business preparadas (disponibilidad, zonas, qué incluye, siguiente paso). Futura skill `respuesta-dm`.
- La **web** (landing que prepara el equipo) recibe el tráfico del enlace de la bio y lleva también a WhatsApp o a un formulario.
- **Pendiente decidir**: quién responde y en qué plazo (`CLAUDE.md` §9). Propuesta: responde el cliente en menos de 24 h; el equipo deja las respuestas preparadas.

### 10–11 · Panel de solicitudes (automático)

Nada de hojas rellenadas a mano: una sección **Solicitudes** dentro de la web, con acceso solo para administradores (el equipo y el cliente). Cada solicitud entra sola:

| Origen | Cómo entra | Fase |
|---|---|---|
| Formulario de la web | Se guarda directamente en el panel | 1 |
| Clic en un enlace de WhatsApp (`/w/<código>`) | La web registra el clic con la publicación de origen antes de redirigir | 1 |
| Mensaje de WhatsApp | Webhook de la API de WhatsApp Business (Cloud API): crea la solicitud y detecta la palabra clave | 2 |
| Mensaje directo de Instagram | Webhook de la API de mensajería de Instagram | 2 |

Campos: fecha, canal, publicación de origen (código), nombre y teléfono si los hay, fecha y lugar de la boda si los da, y **estado**: Nueva → Presupuesto enviado → Reservada / Perdida (con motivo: fecha ocupada, precio, otro). Lo único manual es cambiar el estado, con un botón.

**Limitación de la fase 1**: un clic en el enlace de WhatsApp no garantiza que la pareja llegue a escribir. Cuenta como intención; la fase 2 lo sustituye por el mensaje real.

**Requisitos de la fase 2**: cuenta profesional de Instagram, negocio verificado en Meta, una app de Meta con revisión de permisos (lleva semanas) y el número de WhatsApp conectado a la Cloud API (compatible con seguir usando la app de WhatsApp Business). Se arranca la tramitación en el lanzamiento para tenerla lista cuanto antes.

**Pendiente con quien construye la web**: la tecnología del panel (base de datos y acceso de administradores) se decide con él; este documento solo fija qué tiene que hacer.

### 12 · Medición e informes

| Nivel del embudo | Indicador | De dónde sale |
|---|---|---|
| Descubrimiento | Alcance, visualizaciones, alcance a no seguidores | Instagram (Insights). En la fase 2, cargado solo en el panel con la API de Instagram |
| Interés | Guardados, compartidos, visitas al perfil, clics en el enlace | Instagram |
| Conversación | Solicitudes de disponibilidad por canal y por pieza | Panel de solicitudes |
| Negocio | Presupuestos enviados, **bodas reservadas** | Panel de solicitudes |

- **Semanal (15 min, equipo)**: 3 mejores y 3 peores publicaciones, y las solicitudes de la semana.
- **Mensual (cliente)**: informe con el embudo completo y qué cambiamos. En la fase 1 lo montamos con la skill `informe-mensual` a partir del panel; en la fase 2 el panel lo genera solo.
- **Objetivos numéricos**: no se fijan sin datos; las 4 primeras semanas son la línea base y en la semana 5 se cierran con el cliente.
- **Publicidad en Meta**: cuando haya presupuesto, se promocionan los reels que mejor funcionen en orgánico, con objetivo "mensajes".

## 3. Calendario de una boda

| Día | Qué pasa | Quién |
|---|---|---|
| D | Boda; se graban los planos de la lista | Cliente / chófer |
| D+2 | Material y ficha en el Drive | Cliente |
| D+4 | Curación y `revision-marca` | Equipo |
| D+6 | Lote (reel, carrusel, stories) enviado a aprobación | Equipo |
| D+8 | Aprobado | Cliente |
| D+9 a D+14 | Publicado según calendario | Equipo |
| Mes siguiente | Resultados en el informe mensual | Equipo |

## 4. Herramientas y coste

| Necesidad | Herramienta | Coste |
|---|---|---|
| Entrada de material | Google Drive (carpeta compartida) | Gratis (15 GB); ampliar si hace falta |
| Producción de reels | HyperFrames (local, en nuestros ordenadores) | Gratis |
| Fuentes, guiones y fichas | Repositorio `jjuanx/Mehari` + skills del equipo | Gratis |
| Programación y métricas | Meta Business Suite e Instagram Insights | Gratis |
| Conversaciones | WhatsApp Business | Gratis |
| Registro de solicitudes y métricas | Panel de administración dentro de la web | Incluido en la web; las API de Meta son gratuitas (los mensajes de WhatsApp que inicia la empresa pueden tener coste) |
| Música para publicar | Biblioteca libre de derechos de Meta | Gratis |
| Publicidad | Meta Ads | `[PRESUPUESTO POR DEFINIR]` |

## 5. Lo que necesitamos del cliente

1. Nombre, logo, usuario de Instagram, email y WhatsApp de la marca nueva.
2. Quién responde las solicitudes y en qué plazo.
3. Acceso de edición a la cuenta de Instagram (o crearla con nosotros) y a Meta Business Suite, y **verificar el negocio en Meta** (necesario para la fase 2 del panel de solicitudes).
4. El compromiso de subir el material de cada boda en 2 días y de aprobar el lote semanal en 48 h.
5. El material que ya tenga: vídeos de bodas anteriores y originales de las fotos (las de Instagram están comprimidas).
6. Presupuesto para Meta Ads, si lo hay.
7. Permiso del *Diario de Sevilla* o del fotógrafo para usar las fotos de la boda Herrera.
