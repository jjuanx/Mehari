# Grid semilla: piezas estáticas

Fotos y carruseles del grid semilla de [docs/planes/perfil-redes.md](../../../../docs/planes/perfil-redes.md) §8, listos para subir a 1080×1440 (3:4).

| Pieza | Diapositivas | Ficha | Sitio en el grid |
|---|---|---|---|
| `foto-f0345` | 1 | [sin-fecha_foto_beso-ramo-naranja.md](../sin-fecha_foto_beso-ramo-naranja.md) | Inferior izquierda |
| `ideas-fotos` | 10 | [sin-fecha_carrusel_8-fotos-fotografo.md](../sin-fecha_carrusel_8-fotos-fotografo.md) | Inferior derecha |
| `naranja-beige` | 4 | [sin-fecha_carrusel_naranja-o-beige.md](../sin-fecha_carrusel_naranja-o-beige.md) | Media izquierda |
| `foto-f1839` | 1 | [sin-fecha_foto_playa-naranja.md](../sin-fecha_foto_playa-naranja.md) | Media derecha |
| `foto-f0524` | 1 | [sin-fecha_foto_atardecer-beige.md](../sin-fecha_foto_atardecer-beige.md) | Superior derecha |

Los JPEG están en `jpg/<pieza>/NN.jpg`, en el orden en que se suben.

## Cambios respecto al plan de §8

- **Foto superior derecha:** F0524 en lugar de F0538. Es la misma pareja y la misma luz, pero en F0538 no sale el coche.
- **Foto media derecha:** F1839 (el naranja en la playa con barcas) en lugar de F2131. El plano de dron solo mide 1170×671 y se vería pixelado a pantalla completa.
- **«¿Naranja o beige?»:** F1018 y F0774, porque F1839 pasa a ser foto suelta y F0524 también.
- **«8 fotos»:** F0022, F0329, F1508 y F0047 en lugar de F0023, F0499, F2181 y F1725. Las tres primeras no estaban retocadas en local; F1725 pasa a la portada.
- **Reel inferior central (V066/V067):** no se puede usar. Al montar el primer reel se descartaron por la cara de un niño y una matrícula visible. Sustituto propuesto: V063–V065 ([análisis](../../../../docs/planes/analisis-competencia-reels.md) §4).

## Revisión de marca

Todas las fotos salen de `redes/instagram/destacadas/historias/limpias/`. En F0345, F0524, F0750 y F1839 se sustituyó el difuminado, que se notaba mucho, por una placa lisa y los emblemas borrados con `herramientas/material/retocar_foto.py`. La placa roja del frontal de F0345 no queda bien rellenada: sigue difuminada en el fichero y la foto suelta va con un zoom ×1,1 que la deja fuera. Al montar se revisaron otra vez a tamaño real los volantes de F1018, F0022, F0329 y F0619: el centro queda tapado por las manos o fuera de plano. Se ve la placa «Méhari» del salpicadero, que sí es nuestra. No hay caras de menores reconocibles (en F0774 y F1018 la gente del fondo es adulta o se ve a lo lejos).

## Volver a exportar

`piezas.html` sin parámetros muestra todas las diapositivas en pequeño. Para regenerar los JPEG (Chrome y FFmpeg), desde Git Bash en esta carpeta:

```bash
bash exportar.sh
```

Las tipografías (Fraunces y Jost) son provisionales, las mismas que en el reel. Cuando esté el logo y la identidad de la grafista, se cambian en `piezas.html` y se vuelve a exportar.
