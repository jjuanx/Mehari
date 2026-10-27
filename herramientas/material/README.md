# Herramientas de material

Scripts para procesar lotes grandes de fotos y vídeos del cliente sin revisarlos uno a uno. Funcionan en Mac, Windows y Linux. Resultados y criterios del primer lote: [`docs/material/README.md`](../../docs/material/README.md).

## Instalación

```bash
pip install -r herramientas/material/requirements.txt
```

También hacen falta **FFmpeg** y **ffprobe** en el PATH. En Mac: `brew install ffmpeg`. En Windows: `winget install ffmpeg`.

## Pasos

Todos los scripts reciben la carpeta del material como primer argumento: `python <script> "<carpeta>"`. **Ninguno borra nada**: lo que se aparta se mueve a una subcarpeta de la misma carpeta.

| Paso | Script | Qué hace |
|---|---|---|
| 1 | `1_analizar.py` | Calcula resolución, fecha, nitidez, pHash/dHash y duración. Genera las miniaturas en `_analisis/`. Si se corta, sigue donde lo dejó |
| 2 | `2_descartar.py` | Propone duplicados exactos, casi duplicados, vídeos por debajo de 1080p y candidatas a movidas. **Simula** por defecto; con `--aplicar` mueve a `_DESCARTADOS/` y deja `restaurar.py` |
| 3 | `3_livephotos.py` | Mueve los clips de Live Photo a `_livephotos/` |
| 4 | `4_hojas_contacto.py` | Asigna los códigos F0001 / V001 y genera las hojas de contacto en `_analisis/hojas/` |
| 5 | `5_clasificacion.py` | Une las notas `clasificacion_fotos.txt` y `clasificacion_videos.txt` en `clasificacion.csv` (el formato está en el propio script) |
| 6 | `6_seleccion.py` | Copia lo de calidad ≥4 a `_SELECCION/` y convierte las fotos a JPG |
| 7 | `7_galeria.py` | Genera `galeria.html`, o la versión para Drive con `--drive "<carpeta de la selección>"` |

Fuera de la secuencia, para preparar piezas:

| Script | Qué hace |
|---|---|
| `difuminar.py` | Difumina matrículas, chevrones o caras en un vídeo y sigue la zona fotograma a fotograma. Uso y ejemplos en la cabecera del script. Avisa con `<< REVISAR` si pierde el seguimiento; aun así, revisa el resultado a ojo |
| `retocar_foto.py` | **Para fotos, en lugar de difuminar.** Deja la matrícula como una placa lisa (borra los caracteres y conserva la placa, su sombra y la banda azul) y borra los emblemas sobre chapa rellenándolos con la chapa de alrededor. Se marca a mano el polígono de cada placa. Uso en la cabecera del script |

**Vídeos del iPhone:** vienen en HDR (HLG). Antes de montarlos, conviértelos a SDR BT.709 con el comando de la cabecera de `difuminar.py`. Si no, el naranja del coche sale amarillo y el render final queda marcado como HDR.

## Paso 2: revisar las movidas a ojo

El detector usa la nitidez de la mejor zona de la foto, pero confunde los desenfoques buscados (flores en primer plano, contraluces, blanco y negro con grano) con fotos movidas. Por eso:

1. Ejecuta `2_descartar.py` sin opciones y abre `_analisis/candidatas_desenfoque.txt`.
2. Mira esas fotos (o pide a Claude que las revise ampliadas) y copia en un `.txt` solo las movidas de verdad, una por línea.
3. Ejecuta `2_descartar.py "<carpeta>" --desenfocadas elegidas.txt --aplicar`.

Umbrales usados, calibrados a ojo con el primer lote: casi duplicado si pHash ≤10 y dHash ≤16, o si ambos ≤12; vídeo descartado si su lado corto mide menos de 1080 px.

## Paso 5: clasificar con Claude

Pide a Claude que lea las hojas de `_analisis/hojas/` de cuatro en cuatro y escriba una línea por código en `clasificacion_fotos.txt` y `clasificacion_videos.txt`. Cada miniatura gasta unos 200 tokens, frente a los miles de la foto entera, así que entra un lote de miles de ficheros sin problemas de contexto. Criterios:

- **Calidad 5:** portada o anuncio. **4:** publicable. **3:** de relleno. **1–2:** no usar.
- **Marca antigua `S`:** se lee la funda «MEHARI TOUR SUR» o @mehari_toursur. **`R`:** se ve la rueda de repuesto pero no se distingue.
- **Notas:** el lugar si se reconoce, `FOTO PROFESIONAL?` si lo parece, y `NO USAR` en capturas con datos personales o de la marca antigua.
