# Reel: Salís de la iglesia y…

| Campo | Valor |
|---|---|
| Fecha prevista | 2026-11-11 (miércoles), 20:40 |
| Formato | Reel 9:16, 19,8 s |
| Línea | Bodas |
| Objetivo | Alcance: llegar a parejas que no nos siguen |
| Público | Parejas que se casan en 2027 |
| Estado | Montado (v2, con los vídeos 4K). En revisión |
| Responsable | Nico (montaje) · Alejandro (texto y publicación) |

Semana de la boda del 24-10-2026: [`redes/instagram/bodas/2026-10-24_la-posadilla/`](../bodas/2026-10-24_la-posadilla/README.md). Miércoles, «El momento», gancho 1 de la rotación (`docs/planes/semana-boda.md` §3).

Proyecto HyperFrames: [`redes/instagram/reels/2026-11-11_salis-de-la-iglesia/`](../reels/2026-11-11_salis-de-la-iglesia/BRIEF.md). MP4 en Drive · `Mehari We/02_Produccion/2026-10-24_la-posadilla/` (no se versiona).

## Material

- Vídeos 4K de la boda (IMG_4036, 4106, 4053 y 4075) y la Live Photo IMG_4049. Tramos, encuadres y retoques en el `BRIEF.md` del proyecto.
- `revision-marca`: la funda «@MEHARI_TOURSUR» de la salida se deja lisa fotograma a fotograma (`funda_video.py`). La matrícula, los chevrones y el rótulo trasero quedan fuera del encuadre. Se descarta el principio de IMG_4036, donde sale un niño de cara.

## Guion

Montado así (hoja de contactos en `reels/2026-11-11_salis-de-la-iglesia/contactos.png`):

| Escena | Plano | Tramo | Texto en pantalla |
|---|---|---|---|
| Gancho | La novia llega al coche ante la ermita, con el velo y los invitados alrededor (IMG_4036) | 0–3,3 s | Salís de la iglesia y… |
| Detalle | Las cestas llenas de flores blancas, de cerca (IMG_4106) | 3,3–5,4 s | …os espera vuestro Méhari |
| Prueba | Los dos riendo en el asiento de atrás, con el campo (Live 4049) | 5,4–8,2 s | Con chófer · y el techo abierto |
| Llegada | El cartel de Finca La Posadilla, con la cámara acercándose (IMG_4053) | 8,2–10,6 s | Llegáis a la finca… |
| Momento | Los novios de pie en el coche, riendo (IMG_4075) | 10,6–13,6 s | — |
| Momento | Ramo y brazos arriba ante los invitados (IMG_4075) | 13,6–17,7 s | …y empieza la fiesta |
| Cierre | Cierre corto con el logo aprobado | 17,7–19,8 s | Escribidnos vuestra fecha · WhatsApp 625 06 42 93 |

## Copy

> Salís de la iglesia y os espera vuestro Méhari.
>
> Así fue el sábado en Finca La Posadilla: el beige con el techo abierto, las cestas llenas de flores y un chófer hasta la finca.
>
> ¿Os casáis en 2027? Escribidnos vuestra fecha por WhatsApp al 625 06 42 93.

## Hashtags

#cochedeboda #cochesclasicos #novios2027 #bodas2027 #[hashtag_marca_por_definir]

## Decisiones

- **Gancho 1, «Salís de la iglesia y…»**: es la primera semana y la salida con el ramo arriba es el plano con más gente y más movimiento.
- **v2 con los vídeos 4K** en lugar de solo Live Photos: la v1 (Live Photos de 3 s) no tenía planos con movimiento de verdad. Se queda una Live, la del asiento de atrás, porque no hay vídeo de ese momento.
- **Reencuadre desde el 4K antes que difuminado**: la matrícula, los chevrones y el rótulo trasero quedan fuera. La funda de la salida, que está detrás de la novia, se deja lisa fotograma a fotograma.
- **Dos frases partidas entre planos** («Salís de la iglesia y… / …os espera vuestro Méhari» y «Llegáis a la finca… / …y empieza la fiesta»). La llegada de pie va sin texto para que respire.
- **Sin audio original.** El máster lleva una pista en silencio (decisión del 2026-10-19). Si se publica por Metricool, la música va **incrustada en el MP4** y es libre de derechos, porque la API no puede usar la biblioteca de Instagram. Si se quiere una canción en tendencia, el reel se deja en Metricool como «aviso al móvil» y se publica a mano (`docs/planes/publicacion-metricool.md` §3).
- **Portada**: fotograma del gancho con el rótulo, también 3:4 para que se vea bien en el grid.

## Checklist

- [x] Un objetivo y una llamada a la acción claros
- [x] Datos sacados del brief y de las fotos, sin nada inventado
- [x] `revision-marca` del vídeo montado: ninguna funda legible, sin matrícula, sin chevrón y sin «Citroën» (fotogramas revisados)
- [x] Sin caras de menores (se descarta el tramo de IMG_4036 donde sale un niño; los invitados del fondo son adultos)
- [x] El reel se entiende sin sonido: no lleva voz y los rótulos cuentan la historia
- [ ] Elegir música: de la biblioteca de Instagram (aviso) o libre de derechos e incrustada (automático)
- [ ] Revisión de diseño de otro miembro del equipo
- [ ] Permiso de los novios para publicar sus caras (bloqueante)
- [ ] Aprobación del cliente (como tarde el 7-11) y de otro miembro del equipo

**Probado (v2):** `hyperframes check` sin errores (1 aviso de densidad de pista, como en los reels anteriores; contraste 6/6 WCAG AA); render de 19,8 s a 1080×1920; un fotograma por escena revisado a 390 px; `revision-marca` sobre la salida fotograma a fotograma (0,2, 1,0, 1,6, 2,4 y 3,1 s) y sobre el resto de planos. No probado: la revisión de diseño por otra persona y la vista previa en un móvil.
