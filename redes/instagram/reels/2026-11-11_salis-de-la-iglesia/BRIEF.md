---
workflow: general-video
flow: automation
storyboard: no
message: "Salís de la iglesia y… os espera vuestro Méhari"
destination: instagram-reels
aspect: "9:16"
language: es
audience: parejas que se casan en 2027
length: 15s
---

# Brief

Reel del miércoles («El momento») de la semana de la boda del 24-10-2026 en Finca La Posadilla (`redes/instagram/bodas/2026-10-24_la-posadilla/`). Gancho 1 de la rotación de `docs/planes/semana-boda.md` §3. La ficha está en `redes/instagram/publicaciones/2026-11-11_reel_salis-de-la-iglesia.md`.

## Assets

En `assets/clips/` (no versionados). Son Live Photos de la boda (HEVC, 1440×1920 SDR BT.709, unos 3 s), porque los vídeos largos pesan más de 10 MB y el conector de Drive no los baja. Se pasaron a 30 fps y se reencuadraron a 9:16:

| Clip | Origen | Encuadre | Marca antigua y matrícula |
|---|---|---|---|
| `e1_4041_salida.mp4` | IMG_4041.MOV | `crop=788:1400:390:0`, ampliado ×1,37 | La funda queda fuera del encuadre |
| `e2_4101_cestas.mp4` | IMG_4101.MOV | `crop=810:1440:0:300`, ampliado ×1,33 | La funda queda fuera. Se ve la placa «Méhari» del coche, que es nuestra |
| `e3_4049_detras.mp4` | IMG_4049.MOV | `crop=1080:1920:240:0` | Resto de la funda en el borde izquierdo, difuminado con `difuminar.py` (zona `1.0,0,1360,80,200`) |
| `e4_4073_llegada.mp4` | IMG_4073.MOV | `crop=698:1240:370:200`, ampliado ×1,55 | Matrícula y chevrón del capó fuera del encuadre |
| `e5_4079_fiesta.mp4` | IMG_4079.MOV | `crop=1080:1920:160:0` | Funda entre los novios: lisa fotograma a fotograma con `funda_lisa()` de `retocar_foto.py`, siguiendo el movimiento con *template matching* |

Las ampliaciones llevan `scale=…:flags=lanczos,unsharp=5:5:0.5`.

`assets/vendor/gsap.min.js` es GSAP 3.14.2 en local: el render sin red no carga el CDN.

## Sonido

- **`reel_9x16.mp4` (el máster) va sin sonido original**, con una pista AAC en silencio, como manda la decisión del 2026-10-19. La música se pone de dos maneras:
  - En la app, desde la biblioteca de Instagram (en Metricool, modo «aviso»).
  - Incrustada en el MP4 si es libre de derechos (modo automático, `docs/planes/publicacion-metricool.md` §3).
- **`reel_9x16_sonido-real.mp4`** es la alternativa con el sonido de las Live Photos (vítores en la salida y ambiente), mezclado a −15 LUFS y −1,5 dBFS de pico. En el espectrograma hay una banda continua de 3 a 13 s que podría ser música de fondo de la finca. **Hay que escucharlo antes de usarlo.**

## Cierre

`compositions/cierre-corto.html` (2,1 s) ya lleva el **logo aprobado** (`assets/marca/mehari-we-blanco.svg`) en lugar del nombre en texto. Es el cierre que se reutiliza a partir de ahora.

## Render

```sh
npx --yes hyperframes@0.8.174 render -o reel_mudo.mp4 -q delivery
ffmpeg -i reel_mudo.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -c:v copy -c:a aac -shortest reel_9x16.mp4
```

Los MP4 no se versionan. Se suben a Drive · `Mehari We/02_Produccion/2026-10-24_la-posadilla/`.
