# Reel: Salís de la iglesia y…

| Campo | Valor |
|---|---|
| Fecha prevista | 2026-11-11 (miércoles), 20:40 |
| Formato | Reel 9:16, 15 s |
| Línea | Bodas |
| Objetivo | Alcance: llegar a parejas que no nos siguen |
| Público | Parejas que se casan en 2027 |
| Estado | Montado (v1). En revisión |
| Responsable | Nico (montaje) · Alejandro (texto y publicación) |

Semana de la boda del 24-10-2026: [`redes/instagram/bodas/2026-10-24_la-posadilla/`](../bodas/2026-10-24_la-posadilla/README.md). Miércoles, «El momento», gancho 1 de la rotación (`docs/planes/semana-boda.md` §3).

Proyecto HyperFrames: [`redes/instagram/reels/2026-11-11_salis-de-la-iglesia/`](../reels/2026-11-11_salis-de-la-iglesia/BRIEF.md). MP4 en Drive · `Mehari We/02_Produccion/2026-10-24_la-posadilla/` (no se versiona).

## Material

- Live Photos de la boda (clips de unos 3 s y menos de 10 MB, que el conector de Drive sí baja): IMG_4041, 4101, 4049, 4073 y 4079. Encuadre y retoque de cada una en el `BRIEF.md` del proyecto.
- Vídeos largos (IMG_4036, 4052, 4053, 4075, 4081, 4087, 4090, 4102–4106 y 4108): pesan más de 10 MB y no se han usado. Para una v2 se bajan a mano de Drive; si hay un plano de la salida o del coche en marcha, sustituye a la Live correspondiente.
- `revision-marca`: la funda «@MEHARI_TOURSUR» salía en cuatro clips, y la matrícula y el chevrón en la llegada. Resuelto con encuadre, difuminado (4049) o funda lisa (4079).

## Guion

Montado así (hoja de contactos en `reels/2026-11-11_salis-de-la-iglesia/contactos.png`):

| Escena | Plano | Tramo | Texto en pantalla |
|---|---|---|---|
| Gancho | Live 4041: la novia levanta el ramo y el novio la abraza, con los invitados detrás | 0–2,9 s | Salís de la iglesia y… |
| Detalle | Live 4101: la trasera con las cestas llenas de flores blancas | 2,9–4,8 s | …os espera vuestro Méhari |
| Prueba | Live 4049: los dos riendo en el asiento de atrás, con el campo | 4,8–7,6 s | Con chófer · y el techo abierto |
| Momento | Live 4073: llegada a la finca, de pie en el coche | 7,6–10,1 s | Llegáis a la finca |
| Momento | Live 4079: la novia luce el vestido junto al coche | 10,1–12,9 s | y empieza la fiesta |
| Cierre | Cierre corto con el logo aprobado | 12,9–15 s | Escribidnos vuestra fecha · WhatsApp 625 06 42 93 |

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
- **Live Photos en lugar de los vídeos largos**: el conector de Drive no baja ficheros de más de 10 MB. Con clips de unos 3 s el ritmo queda en un corte cada 2–3 s, que es lo que pide el gancho.
- **Reencuadre antes que difuminado**: en tres planos la funda, la matrícula o el chevrón quedan fuera del encuadre. En 4079 la funda está entre los novios y se deja lisa fotograma a fotograma, porque el difuminado se notaba mucho.
- **Rótulos arriba en cuatro de los cinco planos**, para no tapar caras ni las cestas.
- **Sin audio original.** El máster lleva una pista en silencio (decisión del 2026-10-19). Hay una alternativa con el sonido real de las Live Photos, pero hay que escucharla: el espectrograma sugiere música de fondo en la finca. Si se publica por Metricool, la música va **incrustada en el MP4** y es libre de derechos, porque la API no puede usar la biblioteca de Instagram. Si se quiere una canción en tendencia, el reel se deja en Metricool como «aviso al móvil» y se publica a mano (`docs/planes/publicacion-metricool.md` §3).
- **Portada**: fotograma del gancho con el rótulo, también 3:4 para que se vea bien en el grid.

## Checklist

- [x] Un objetivo y una llamada a la acción claros
- [x] Datos sacados del brief y de las fotos, sin nada inventado
- [x] `revision-marca` del vídeo montado: ninguna funda legible, sin matrícula, sin chevrón y sin «Citroën» (fotogramas revisados)
- [x] Sin caras de menores (los invitados del fondo son adultos)
- [x] El reel se entiende sin sonido: no lleva voz y los rótulos cuentan la historia
- [ ] Elegir música: de la biblioteca de Instagram (aviso) o libre de derechos e incrustada (automático)
- [ ] Revisión de diseño de otro miembro del equipo
- [ ] Permiso de los novios para publicar sus caras (bloqueante)
- [ ] Aprobación del cliente (como tarde el 7-11) y de otro miembro del equipo

**Probado:** `hyperframes check` sin errores (1 aviso de densidad de pista, igual que en los reels anteriores; contraste 7/7 WCAG AA); render de 15 s a 1080×1920; un fotograma por escena revisado a 390 px; el primer segundo por separado (el ramo arriba se entiende sin texto); `revision-marca` sobre cada fotograma; sonoridad de la versión con sonido real (−15,2 LUFS, −1,5 dBFS). No probado: la escucha del sonido real, la revisión de diseño por otra persona y la vista previa en un móvil.
