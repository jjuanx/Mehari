---
workflow: general-video
flow: automation
storyboard: no
message: "Así se sale de una boda"
destination: instagram-reels
aspect: "9:16"
language: es
audience: parejas que se casan en 2027
length: 16s
---

# Brief

**v3**, reel de un solo momento (la v2 se descartó: era un resumen de 5 mensajes en 20 s con cajas de texto). Reel del miércoles («El momento») de la boda del 24-10-2026 en Finca La Posadilla. Ficha: `redes/instagram/publicaciones/2026-11-11_reel_salis-de-la-iglesia.md`.

## Montaje (16 s)

| Tramo | Plano | Qué hace |
|---|---|---|
| 0–2 s | Cuatro destellos de 0,5 s: cartel de la finca, cestas, salida ante la ermita, asiento de atrás | Cortes a pulso de 120 BPM, cada uno entra ampliado ×1,12 y se asienta. Frase «Así se sale de una boda» en los tres primeros, grande, arriba y sin caja (con un degradado suave para el contraste) |
| 2–5,2 s | Toma continua IMG_4075: los novios de pie en el coche, ríen y la novia levanta el ramo (≈2,9 s) | Acercamiento lento |
| 5,2–8,2 s | La misma toma a 0,5× (interpolada con `minterpolate`): el novio levanta el brazo | Cámara lenta en el momento fuerte. Aquí tiene que caer el subidón de la canción |
| 7,79–8,66 s | Transición de costillas (`marca/animaciones/renders/transicion.webm`) | Tapa la pantalla a los 8,2 s: ahí se corta a la fiesta |
| 8,2–12 s | Travelling junto al Méhari beige en el patio de la finca, con los invitados (IMG_4081) | Acercamiento lento |
| 12–16 s | Cierre animado de marca (`marca/animaciones/renders/cierre.mp4`) | Costillas → logo aprobado → «Escribidnos vuestra fecha» y WhatsApp |

## Assets

En `assets/clips/` (no versionados): el paquete de clips limpios, en 1080×1920, SDR BT.709 y sin audio. Se subieron a Drive · `02_Produccion/2026-10-24_la-posadilla/clips-limpios/`. Se sacan de los 4K de la carpeta de la boda:

| Clip | Origen | Tramo | Encuadre (sobre 2160×3840) | Marca antigua y matrícula |
|---|---|---|---|---|
| `01_momento_brazos-arriba_IMG4075.mp4` | IMG_4075.MOV | desde 4,6 s (9,8 s) | `crop=1350:2400:300:0` | Funda, matrícula y chevrón fuera |
| `01b_brazos_camara-lenta.mp4` | El 01, de 7,8 a 9,3 s | — | `minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:vsbmc=1,setpts=2*PTS,fps=30` | — |
| `02_salida-ermita_IMG4036_funda-lisa.mp4` | IMG_4036.MOV | 12,3–15,6 s | Completo | Funda lisa con `herramientas/material/funda_video.py` (`0.2 440,900,215,105`, polígono `466,975,482,954,507,934,540,926,580,929,612,944,628,963,634,990,540,981`) |
| `03_cestas-flores_IMG4106.mp4` | IMG_4106.MOV | 28,5–30,6 s | `crop=1900:3378:130:0` | Matrícula y rótulo trasero fuera |
| `04_cartel-finca_IMG4053.mp4` | IMG_4053.MOV | 6–12,8 s | Completo | — |
| `06_fiesta-patio_IMG4081_funda-lisa.mp4` | IMG_4081.MOV | 3–6,8 s | Completo | Funda lisa con `funda_video.py` (`1.5 270,1040,270,105`, polígono `290,1133,300,1102,330,1078,375,1060,415,1058,460,1065,498,1087,518,1113,520,1133`). El seguimiento baja a 0,54 de parecido: revisado a 8 fotogramas por segundo, sin letras |
| `07_cierre-marca.mp4`, `transicion.webm` | Copias de `marca/animaciones/renders/` | — | — | — |
| `05_asiento-atras_Live4049.mp4` | Live Photo IMG_4049 | 0–2,9 s | `crop=1080:1920:240:0` sobre 1440×1920 | Resto de funda en el borde, difuminado con `difuminar.py` |

HDR a SDR con el tonemap de la cabecera de `difuminar.py`. En IMG_4036 antes del segundo 12 sale un niño de cara; en IMG_4075 antes del 4,5, la matrícula.

`assets/vendor/gsap.min.js` es GSAP 3.14.2 en local: el render sin red no carga el CDN.

## Sonido

- **`reel_9x16.mp4` (el máster) va sin sonido original**, con una pista AAC en silencio, como manda la decisión del 2026-10-19. La música se pone de dos maneras:
  - En la app, desde la biblioteca de Instagram (en Metricool, modo «aviso»).
  - Incrustada en el MP4 si es libre de derechos (modo automático, `docs/planes/publicacion-metricool.md` §3).

## Cierre

El reel termina con el cierre animado de `marca/animaciones/` (4 s), ya con el logo aprobado. `compositions/cierre-corto.html` (2,1 s) se queda como alternativa corta.

## Render

```sh
npx --yes hyperframes@0.8.174 render -o reel_mudo.mp4 -q delivery
ffmpeg -i reel_mudo.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -c:v copy -c:a aac -shortest reel_9x16.mp4
```

Los MP4 no se versionan. Se suben a Drive · `Mehari We/02_Produccion/2026-10-24_la-posadilla/`.
