---
workflow: general-video
flow: automation
storyboard: no
message: "El trayecto más corto del día… y el que más se recuerda"
destination: instagram-reels / tiktok
aspect: "9:16"
language: es
audience: parejas que se casan en 2027
length: 17.7s
---

# Brief

Vídeo emotivo de marca, sin atarlo a una boda: varios momentos reales en el coche (llega la novia, suben, celebran, conducen y, ya de noche, la llegada). Pedido por Juan el 2026-11-12 después de descartar las piezas montadas con fotos. **Permiso de caras confirmado por Juan** (2026-11-12). Sin música: se elige al publicar (TikTok o Instagram).

**Una sola idea**: el trayecto en el Méhari dura minutos, pero es lo que más se recuerda. Dos frases de contraste, una al principio y otra tras la transición de marca, del día a la noche.

## Montaje (17,7 s)

| Tramo | Clip | Qué hace |
|---|---|---|
| 0–2,3 s | `01_velo_V144` | La novia, con un velo larguísimo, camina hacia la iglesia del brazo del padrino. Frase «El trayecto más corto del día» |
| 2,0–4,3 s | `02_subida_V151` | La novia sube al Méhari beige riendo, con el ramo en alto y los invitados detrás |
| 4,0–8,2 s | `03_ramo-rojo_V139` | Los novios, de pie en el Méhari naranja ante una iglesia gótica, levantan el ramo rojo |
| 7,9–10,5 s | `04_volante_V023` | El novio conduce el naranja y la novia saluda con el ramo |
| 10,09–10,96 s | `transicion.webm` | Costillas de marca: del día a la noche |
| 10,5–14,0 s | `06_noche_V063` | De noche, en la hacienda: el novio levanta el puño, la novia ríe. Frase «…y el que *más se recuerda*» |
| 13,7–17,7 s | `08_cierre-marca` | Cierre animado de `marca/animaciones/`: logo aprobado, «Escribidnos vuestra fecha» y WhatsApp 625 06 42 93 |

Fundidos de 0,3 s entre planos; corte seco bajo la transición. Los cortes caen en 2,0 · 4,0 · 7,9 · 10,5 · 13,7 s: la música, cuando se ponga, debería tener su golpe fuerte en el 10,5 (día → noche).

## Assets

En `assets/clips/` (los MP4 no se versionan; copias en Drive · `02_Produccion/_marca/2026-11-12_reel_el-trayecto-mas-corto/`). Todos en 1080×1920, SDR BT.709, 30 fps y sin audio, sacados de los 4K HLG de Drive · `01_Material/Selecccion/videos/bodas/` con el tonemap de la cabecera de `difuminar.py` (con `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`: el `ffmpeg` normal de Homebrew no trae `zscale`).

| Clip | Origen | Tramo del original | revision-marca |
|---|---|---|---|
| `01_velo_V144.mp4` | V144_q5_beige.mov | 16,6–18,9 s | APTA. Empieza cuando el beige ya no está en plano (antes se ve de frente con matrícula) y acaba antes de que en la puerta aparezca un bebé en brazos (2,4 s del clip) |
| `02_subida_V151.mp4` | V151_q4_beige.mov | 0,9–3,2 s | APTA. La funda «@MEHARI_TOURSUR» de la rueda entra por la izquierda a los 3,5 s del original: el corte acaba antes. Frontal del beige sin matrícula visible. Botella de cerveza con marca en la mano de la novia (momento real, se deja) |
| `03_ramo-rojo_V139.mp4` | V139_q5_naranja.mov | 0,3–4,5 s | APTA. De lado, sin matrícula ni funda; volante sin emblema legible |
| `04_volante_V023.mp4` | V023_q5_naranja.mov (horizontal) | 1,8–4,4 s, `crop=1215:2160:1950:0` | APTA. Insignia «Leader» y pegatina TARA/PMA de la puerta, sin marca |
| `06_noche_V063.mp4` | V063_q4_beige.mov | 1,5–5,0 s, `crop=1800:3200:180:0` (sobre el vertical 2160×3840) | APTA CON RECORTE: la funda «@MEHARI_TOURSUR» de la rueda queda en la franja inferior del original, fuera del recorte |
| `08_cierre-marca.mp4`, `transicion.webm` | Copias de `marca/animaciones/renders/` | — | — |

**Descartados** tras mirarlos a resolución completa: V052 (se lee «…RI TO…» de la funda en el respaldo), V044 (funda en el centro, bajo los novios, en todo el tramo útil), V066 (funda en el centro y matrícula trasera legible), V140 y V132 (matrícula legible), V097 (horizontal: en vertical no cabe la pareja).

`assets/vendor/gsap.min.js` es GSAP 3.14.2 en local.

## Sonido

`reel_9x16.mp4` va **sin sonido original**, con una pista AAC en silencio (decisión del 2026-10-19). La música la pone Juan al publicar en TikTok.

## Render

```sh
npx --yes hyperframes@0.8.174 render -o reel_mudo.mp4 -q delivery
ffmpeg -i reel_mudo.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -c:v copy -c:a aac -shortest reel_9x16.mp4
```

## Texto propuesto

> El trayecto más corto del día: de la puerta de la iglesia al coche, y del coche a la celebración. Unos minutos con todo el mundo alrededor que luego son los que más se cuentan.
>
> ¿Cuándo os casáis? Escribidnos vuestra fecha por WhatsApp al 625 06 42 93.
>
> #cochedeboda #cochesclasicos #bodasconencanto #novios2027

Texto alternativo: «Varias novias y novios en dos Méhari clásicos, uno beige y otro naranja: una novia con velo largo camina hacia la iglesia, otra sube al coche riendo, una pareja levanta un ramo rojo de pie en el coche, un novio conduce y, de noche, una pareja celebra en una hacienda. Termina con el logo de Méhari We y el WhatsApp 625 06 42 93.»

**Probado:** `hyperframes check` sin errores (contraste WCAG AA incluido); fotograma por plano y por fundido revisado a 390 px; revisión de marca de cada clip a 540 px y zonas dudosas a resolución completa (fundas, matrículas, menores).
