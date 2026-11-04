---
workflow: general-video
flow: automation
storyboard: no
message: "Lo que ven vuestros invitados, y lo que veis vosotros"
destination: instagram-reels
aspect: "9:16"
language: es
audience: parejas que se casan en 2027 y sus invitados
length: 18.1s
---

# Brief

Reel del miércoles («El momento») de la boda del 31-10-2026. Ficha: `redes/instagram/publicaciones/2026-11-18_reel_lo-que-ven-vuestros-invitados.md`. Plan de la semana: `redes/instagram/bodas/2026-10-31_sevilla/README.md`.

**Una sola idea en dos mitades**: lo que ven los invitados desde fuera (pétalos, la gente alrededor del coche) y, tras la transición de marca, lo que ven los novios desde dentro (POV del capó naranja por el centro). Referencias del cliente: los reels de @landroverevents88 (una frase de contraste en el primer segundo y una sola idea, `docs/planes/analisis-competencia-reels.md` §1) y los patrones que más reparten (POV desde el coche, 10–18 s, poco texto y grande, §2).

## Montaje (18,1 s)

| Tramo | Clip | Qué hace |
|---|---|---|
| 0–2,9 s | `01_petalos-iglesia_IMG4301_difuminado` | Pétalos en la puerta de la iglesia, entre las cabezas de los invitados; el beso al principio. Frase «Lo que ven vuestros invitados» desde el fotograma 0 |
| 2,9–4,5 s | `02_invitados-alrededor_IMG4314` | Los invitados se agolpan alrededor del Méhari; la novia se inclina hacia el chófer |
| 4,09–4,96 s | `transicion.webm` | Costillas de marca: tapan a los 4,5 s, donde se pasa de fuera a dentro |
| 4,5–8,7 s | `03_pov-centro_IMG4408` | POV desde el asiento, con el capó naranja, por una calle empedrada del centro. Frase «Y lo que veis *vosotros*» |
| 8,7–10,9 s | `04_avenida-palmeras_IMG4321_difuminado` | El Méhari entra por la avenida de palmeras de la hacienda |
| 10,9–14,1 s | `05_manteo_IMG4372` | Los amigos mantean al novio |
| 14,1–18,1 s | `06_cierre-marca` | Cierre animado de `marca/animaciones/`: logo aprobado, «Escribidnos vuestra fecha» y WhatsApp |

## Assets

En `assets/clips/` (los MP4 no se versionan; van a Drive · `02_Produccion/2026-10-31_sevilla/clips-limpios/`). Todos en 1080×1920, SDR BT.709, 30 fps y sin audio, sacados de los 4K de la carpeta de Drive «Boda 24:10:2026» con el tonemap de la cabecera de `difuminar.py`:

| Clip | Origen | Tramo | revision-marca |
|---|---|---|---|
| `01_petalos-iglesia_IMG4301_difuminado.mp4` | IMG_4301.MOV | 0–2,9 s | APTA CON RETOQUE: una niña de blanco junto a las flores de la derecha y un chico muy joven al fondo, con la cara difuminada (`difuminar.py --zona 1.0,965,1115,80,90 --zona 2.0,985,825,85,95`, parecido mínimo 0,71). Sin coche |
| `02_invitados-alrededor_IMG4314.mp4` | IMG_4314.MOV | 64,8–66,4 s | APTA. La funda «@MEHARI_TOURSUR» entra en plano antes del 64,5 y después del 69: el tramo queda fuera. Sin matrícula ni chevrón. Solo adultos |
| `03_pov-centro_IMG4408.mp4` | IMG_4408.MOV | 4,0–8,2 s | APTA. El capó no enseña el chevrón; los coches del fondo, lejos y sin matrícula legible. Desde el 22 s sale un coche blanco de cerca: no se usa |
| `04_avenida-palmeras_IMG4321_difuminado.mp4` | IMG_4321.MOV | 15,0–17,2 s, recortado del 4K (`crop=1380:2453:390:0`) para quitar el salpicadero del coche que graba | APTA CON RETOQUE: matrícula y rótulo «CITROËN» traseros difuminados (`difuminar.py --zona 0.1,630,1438,112,42,0,1.2 --zona 2.0,660,1355,128,56,1.0,2.3`, parecido mínimo 0,92) |
| `05_manteo_IMG4372.mp4` | IMG_4372.MOV | 0,6–3,8 s | APTA. Solo adultos. Destello del sol arriba |
| `06_cierre-marca.mp4`, `transicion.webm` | Copias de `marca/animaciones/renders/` | — | — |

`assets/vendor/gsap.min.js` es GSAP 3.14.2 en local.

## Sonido

`reel_9x16.mp4` va **sin sonido original**, con una pista AAC en silencio (decisión del 2026-10-19). La canción se pone en Instagram (Metricool en modo «aviso»). Que el golpe fuerte caiga en el 4,5 s (el giro a «vosotros») y otro en el 10,9 s (el manteo).

## Render

```sh
npx --yes hyperframes@0.8.174 render -o reel_mudo.mp4 -q delivery
ffmpeg -i reel_mudo.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -c:v copy -c:a aac -shortest reel_9x16.mp4
```

Los MP4 no se versionan. Se suben a Drive · `Mehari We/02_Produccion/2026-10-31_sevilla/`.
