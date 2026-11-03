# Reel: Lo que ven vuestros invitados

| Campo | Valor |
|---|---|
| Fecha prevista | 2026-11-18 (miércoles), 20:40 |
| Formato | Reel 9:16, ~21 s |
| Línea | Bodas |
| Objetivo | Alcance: llegar a parejas que no nos siguen |
| Público | Parejas que se casan en 2027 y sus invitados |
| Estado | Guion. Falta montarlo con `guion-reel` |
| Responsable | Nico (montaje) · Alejandro (texto y publicación) |

Semana de la boda del 31-10-2026: [`redes/instagram/bodas/2026-10-31_sevilla/`](../bodas/2026-10-31_sevilla/README.md). Miércoles, «El momento», gancho 3 de la rotación (`docs/planes/semana-boda.md` §3). La semana anterior fue el 1, «Salís de la iglesia y…».

Proyecto HyperFrames (por crear): `redes/instagram/reels/2026-11-18_lo-que-ven-vuestros-invitados/`. MP4 en Drive · `Mehari We/02_Produccion/2026-10-31_sevilla/` (no se versiona).

## Material

- Vídeos 4K de la boda en Drive (carpeta «Boda 24:10:2026»): IMG_4301, IMG_4314, IMG_4321 e IMG_4372. Están en HDR: pasarlos a SDR BT.709 antes de montar (cabecera de `difuminar.py`).
- `revision-marca`: la funda «@MEHARI_TOURSUR» de los planos de atrás de IMG_4314 se deja lisa con `funda_video.py`; la matrícula de IMG_4321 se difumina con `difuminar.py`. En IMG_4301 hay que revisar fotograma a fotograma que no salga la cara de un menor.

## Guion

Estructura de `guion-reel`: gancho, detalle, prueba, momento y cierre.

| Tramo | Plano | Texto en pantalla |
|---|---|---|
| 0–3 s | IMG_4301 0–3 s: lluvia de pétalos en la puerta de la iglesia, vista entre las cabezas de los invitados | Lo que ven vuestros invitados… |
| 3–5,5 s | IMG_4314 ≈56–59 s: las flores de la trasera, con los novios detrás | …cuando salís en un Méhari |
| 5,5–9 s | IMG_4314 ≈72–78 s: la novia se gira y sonríe, con la gente y el centro detrás | Techo abierto · flores atrás |
| 9–12 s | IMG_4321 ≈12–19 s: el coche entra por la avenida de palmeras, visto desde el coche de detrás | Hasta la hacienda… |
| 12–17 s | IMG_4372 1–7 s: los amigos mantean al novio | …y empieza la fiesta |
| 17–21 s | Cierre animado de `marca/animaciones/` | Escribidnos vuestra fecha (en el cierre) |

**Música (al publicar, en Instagram):** una canción en tendencia con un subidón que caiga en el segundo 12, cuando empieza el manteo.

## Copy

> Lo que ven vuestros invitados cuando salís de la iglesia 🤍
>
> Pétalos en la puerta, el Méhari naranja esperando con las flores atrás y un paseo por el centro hasta la hacienda.
>
> Mandádselo a quien se case en 2027 💍
>
> ¿Os casáis vosotros? Escribidnos vuestra fecha por WhatsApp al 625 06 42 93.

## Hashtags

#cochedeboda #cochesclasicos #novios2027 #bodas2027 #[hashtag_marca_por_definir]

## Decisiones

- **Gancho «Lo que ven vuestros invitados»**: IMG_4301 está grabado literalmente desde los invitados, con pétalos en el aire. Es el plano con más gente y más movimiento de la boda, y no repite el gancho de la semana anterior.
- **Un solo hilo, de la iglesia a la fiesta**: como en la v3 de La Posadilla, nada de cajas de texto largas. Frases cortas arriba, partidas en dos («…cuando salís en un Méhari», «…y empieza la fiesta») para que el texto tire del siguiente plano.
- **El manteo como momento**: es el plano con más energía después de la salida y donde cae el subidón.
- **Sin audio original**: la canción se elige en Instagram (decisión del 2026-10-19), así que va como aviso en Metricool.
- **CTA para compartir** en una línea propia del copy, pensada para que lo manden a la pareja que se casa.

## Checklist

- [x] Un objetivo y una llamada a la acción claros
- [x] Datos sacados del brief y de los vídeos, sin nada inventado
- [ ] `revision-marca` del vídeo montado: ninguna funda legible, sin matrícula, sin chevrón y sin «Citroën»
- [ ] Sin caras de menores (revisar IMG_4301 y los grupos)
- [ ] Se entiende sin sonido
- [ ] Elegir la canción en Instagram
- [ ] Permiso de los novios para publicar sus caras (bloqueante)
- [ ] Aprobación del cliente (como tarde el 15-11) y de otro miembro del equipo
