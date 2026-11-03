---
workflow: general-video
flow: automation
storyboard: no
message: "Salís de la iglesia y… os espera vuestro Méhari"
destination: instagram-reels
aspect: "9:16"
language: es
audience: parejas que se casan en 2027
length: 19.8s
---

# Brief

Reel del miércoles («El momento») de la semana de la boda del 24-10-2026 en Finca La Posadilla (`redes/instagram/bodas/2026-10-24_la-posadilla/`). Gancho 1 de la rotación de `docs/planes/semana-boda.md` §3. La ficha está en `redes/instagram/publicaciones/2026-11-11_reel_salis-de-la-iglesia.md`.

## Assets

En `assets/clips/` (no versionados). Versión 2: con los **vídeos 4K de la boda**, que se bajaron directamente de Drive (la carpeta está compartida por enlace y el dominio permitido en la red del entorno). Son iPhone 4K en HDR (HLG): se pasaron a SDR BT.709 con el tonemap de `difuminar.py`, a 30 fps, y **se recortaron desde el 4K**, así que los reencuadres no pierden nitidez.

| Clip | Origen | Tramo | Encuadre (sobre 2160×3840) | Marca antigua y matrícula |
|---|---|---|---|---|
| `e1_salida.mp4` | IMG_4036.MOV | 12,3–15,6 s | Completo | Funda lisa fotograma a fotograma con `herramientas/material/funda_video.py` (`0.2 440,900,215,105`, polígono `466,975,482,954,507,934,540,926,580,929,612,944,628,963,634,990,540,981`) |
| `e2_cestas.mp4` | IMG_4106.MOV | 28,5–30,6 s | `crop=1900:3378:130:0` | La matrícula y el rótulo trasero quedan fuera por abajo |
| `e3_detras.mp4` | Live Photo IMG_4049 | 0–2,8 s | `crop=1080:1920:240:0` sobre 1440×1920 | Resto de la funda en el borde, difuminado con `difuminar.py` |
| `e4_cartel.mp4` | IMG_4053.MOV | 9,5–11,9 s | Completo | — |
| `e5_llegada.mp4` | IMG_4075.MOV | 5,5–8,5 s | `crop=1350:2400:250:0` | Funda, matrícula y chevrón fuera del encuadre |
| `e6_brazos.mp4` | IMG_4075.MOV | 9,8–13,9 s | `crop=1350:2400:400:0` | Ídem |

Descartados: IMG_4036 hasta el segundo 10 (sale un niño de cara), los planos frontales de IMG_4075 (matrícula y chevrones) y el vídeo de WhatsApp de la salida (`09d98426….mp4`, 848×478), que es el único con el coche arrancando entre los invitados pero no aguanta la ampliación a 9:16. Si el cliente tiene el original, sería el mejor gancho.

`assets/vendor/gsap.min.js` es GSAP 3.14.2 en local: el render sin red no carga el CDN.

## Sonido

- **`reel_9x16.mp4` (el máster) va sin sonido original**, con una pista AAC en silencio, como manda la decisión del 2026-10-19. La música se pone de dos maneras:
  - En la app, desde la biblioteca de Instagram (en Metricool, modo «aviso»).
  - Incrustada en el MP4 si es libre de derechos (modo automático, `docs/planes/publicacion-metricool.md` §3).

## Cierre

`compositions/cierre-corto.html` (2,1 s) ya lleva el **logo aprobado** (`assets/marca/mehari-we-blanco.svg`) en lugar del nombre en texto. Es el cierre que se reutiliza a partir de ahora.

## Render

```sh
npx --yes hyperframes@0.8.174 render -o reel_mudo.mp4 -q delivery
ffmpeg -i reel_mudo.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -c:v copy -c:a aac -shortest reel_9x16.mp4
```

Los MP4 no se versionan. Se suben a Drive · `Mehari We/02_Produccion/2026-10-24_la-posadilla/`.
