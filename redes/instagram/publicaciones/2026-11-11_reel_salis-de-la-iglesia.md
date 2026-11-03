# Reel: Así se sale de una boda

| Campo | Valor |
|---|---|
| Fecha prevista | 2026-11-11 (miércoles), 20:40 |
| Formato | Reel 9:16, 8,7 s |
| Línea | Bodas |
| Objetivo | Alcance: llegar a parejas que no nos siguen |
| Público | Parejas que se casan en 2027 |
| Estado | v3 montada (un solo momento). En revisión. Falta la canción |
| Responsable | Nico (montaje) · Alejandro (texto y publicación) |

Semana de la boda del 24-10-2026: [`redes/instagram/bodas/2026-10-24_la-posadilla/`](../bodas/2026-10-24_la-posadilla/README.md). Miércoles, «El momento», gancho 1 de la rotación (`docs/planes/semana-boda.md` §3).

Proyecto HyperFrames: [`redes/instagram/reels/2026-11-11_salis-de-la-iglesia/`](../reels/2026-11-11_salis-de-la-iglesia/BRIEF.md). MP4 en Drive · `Mehari We/02_Produccion/2026-10-24_la-posadilla/` (no se versiona).

## Material

- Vídeos 4K de la boda (IMG_4036, 4106, 4053 y 4075) y la Live Photo IMG_4049. Tramos, encuadres y retoques en el `BRIEF.md` del proyecto.
- `revision-marca`: la funda «@MEHARI_TOURSUR» de la salida se deja lisa fotograma a fotograma (`funda_video.py`). La matrícula, los chevrones y el rótulo trasero quedan fuera del encuadre. Se descarta el principio de IMG_4036, donde sale un niño de cara.

## Guion

v3 (hoja de contactos en `reels/2026-11-11_salis-de-la-iglesia/contactos.png`; detalle en su `BRIEF.md`):

| Tramo | Plano | Texto en pantalla |
|---|---|---|
| 0–2 s | Cuatro destellos de 0,5 s: cartel, cestas, salida, asiento de atrás | «Así se sale de una boda» (hasta 1,5 s) |
| 2–5,2 s | IMG_4075 en una sola toma: ríen y la novia levanta el ramo | — |
| 5,2–8,2 s | Cámara lenta: el novio levanta el brazo | — |
| 7,1–8,7 s | El mismo plano con el logo sobre el cielo | — |

**Música (al publicar, en Instagram):** una canción en tendencia con pulso de unos 120 BPM. Que el arranque coincida con el segundo 0 y el subidón caiga en el 5,2, cuando empieza la cámara lenta.

## Copy

> Así se sale de una boda 🤍
>
> Sábado en Finca La Posadilla, con el Méhari beige, el techo abierto y las cestas llenas de flores.
>
> Mandádselo a quien se case en 2027 💍
>
> ¿Os casáis vosotros? Escribidnos vuestra fecha por WhatsApp al 625 06 42 93.

## Hashtags

#cochedeboda #cochesclasicos #novios2027 #bodas2027 #[hashtag_marca_por_definir]

## Decisiones

- **Un solo momento en lugar de un resumen**: las v1 y v2 contaban el día en 5 mensajes, con cajas de texto y sin ritmo. Eso es lógica de carrusel. Los reels que funcionan enseñan un momento (`analisis-competencia-reels.md` §2).
- **Destellos a pulso de 0,5 s antes de la toma larga**: dan contexto (finca, cestas, ermita, pareja) sin texto y crean ritmo para la canción.
- **Cámara lenta en el brazo del novio**: es el instante emocional y donde tiene que caer el subidón de la música.
- **Una frase arriba y sin caja**, solo en el primer segundo y medio, para no tapar caras. Lleva un degradado suave para el contraste.
- **Sin cartón final**: el logo aparece sobre el cielo del último plano, para que el bucle no se corte.
- **Sin audio original** (decisión del 2026-10-19): la canción se elige en Instagram, así que en Metricool va como «aviso».
- **CTA para compartir** en una línea propia del copy: «Mandádselo a quien se case en 2027».

## Checklist

- [x] Un objetivo y una llamada a la acción claros
- [x] Datos sacados del brief y de las fotos, sin nada inventado
- [x] `revision-marca` del vídeo montado: ninguna funda legible, sin matrícula, sin chevrón y sin «Citroën» (fotogramas revisados)
- [x] Sin caras de menores (se descarta el tramo de IMG_4036 donde sale un niño; los invitados del fondo son adultos)
- [x] El reel se entiende sin sonido: no lleva voz y la imagen cuenta el momento
- [ ] Elegir la canción en Instagram (≈120 BPM, subidón en el 5,2 s)
- [ ] Revisión de diseño de otro miembro del equipo
- [ ] Permiso de los novios para publicar sus caras (bloqueante)
- [ ] Aprobación del cliente (como tarde el 7-11) y de otro miembro del equipo

**Probado (v3):** `hyperframes check` sin errores ni avisos de contraste (1/1 WCAG AA); render de 8,7 s a 1080×1920; un fotograma por tramo revisado a 270 px de ancho; la cámara lenta revisada a 5 fotogramas por segundo, sin artefactos; `revision-marca` del paquete de clips (salida fotograma a fotograma). No probado: con la canción puesta, en un móvil y la revisión de otra persona.
