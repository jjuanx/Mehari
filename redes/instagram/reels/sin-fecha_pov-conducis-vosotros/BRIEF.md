---
workflow: general-video
flow: automation
storyboard: no
message: "POV: os acabáis de casar y conducís vosotros"
destination: instagram-reels
aspect: "9:16"
language: es
audience: parejas que se casan en 2027
length: 11.5s
---

# Brief

Reel con el plano subjetivo desde el asiento del conductor, el formato que más reparte en las cuentas de referencia (`docs/planes/analisis-competencia-reels.md` §2 y §4). La ficha completa está en `redes/instagram/publicaciones/sin-fecha_reel_pov-conducis-vosotros.md`.

## Assets

En `assets/clips/` (no versionados), preparados con FFmpeg a 1080×1920 SDR BT.709 y 30 fps:

| Clip | Origen | Tramo | Preparación |
|---|---|---|---|
| `p1_v033_girasoles.mp4` | `V033_q5_naranja.mov` (4K HLG) | 0–2,5 s | Recorte 9:16 fijo (x = 1006 en 3840) y de HLG a SDR con el comando de `difuminar.py` |
| `p2_v033_camino.mp4` | `V033_q5_naranja.mov` | 4,5–7 s | Recorte 9:16 que sigue el camino (x = 1504 − 445·t) y de HLG a SDR |
| `p3_v023_saludan.mp4` | Clip `e5_v023.mp4` de «Las llaves son vuestras» | — | Ya preparado |
| `p4_v080_hacienda.mp4` | `V080_q4_naranja.mov` (1080p SDR) | 34–36,5 s | Recorte 9:16 (x = 1270 en 1920), ampliado ×1,78 con Lanczos y `unsharp` |

Los originales se bajaron de Drive (`Mehari We/01_Material/Selecccion/videos/turismo/`) a `assets/originales/`, que tampoco se versiona.

## Notes

- Sin sonido: la música se añade en Instagram (biblioteca comercial de Meta). El MP4 lleva una pista AAC en silencio.
- El cierre es `compositions/cierre-corto.html`, el mismo de la v2 de «Las llaves son vuestras».
