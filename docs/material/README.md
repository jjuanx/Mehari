# Material fotográfico y de vídeo del cliente

El cliente entregó **22 GB** de fotos y vídeos (casi todo del iPhone, en HEIC y MOV en 4K). Se procesaron el 2026-10-16 con las herramientas de [`herramientas/material/`](../../herramientas/material/). En este repo solo está lo ligero: la clasificación y los descartes. Las fotos y los vídeos están en Google Drive.

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Selección para trabajar (calidad ≥4), fotos en JPG | Drive · `Mehari We/01_Material/Selecccion/` |
| Galería filtrable (`galeria.html`, `thumbs/`, `vframes/`) | Drive · `Mehari We/01_Material/Galeria/` |
| Producción (carruseles, renders, anuncios) | Drive · `Mehari We/02_Produccion/` |
| Logos e identidad final | Drive · `Mehari We/03_Marca/` |
| Dossiers, PDF y prensa del cliente | Drive · `Mehari We/04_Cliente/` |
| Originales completos (17 GB), clips de Live Photo (5,6 GB) y descartes (1,2 GB) | Solo en el Mac de Juan (`FOTOS MEHARI/`). El cliente también los tiene |
| Clasificación de cada fichero | Este repo · [`clasificacion.csv`](clasificacion.csv) |
| Lista de lo apartado y por qué | Este repo · [`descartes.csv`](descartes.csv) |

> **Galería en Drive:** para que se vean las miniaturas, la carpeta `Galeria` tiene que estar disponible sin conexión con Drive para escritorio. Desde el navegador, Drive no abre un HTML con imágenes locales. Al hacer clic se abre la copia de `Selecccion/`, por lo que solo tienen enlace las fichas con calidad ≥4.
>
> **Windows:** los vídeos están en HEVC (H.265). Si no se reproducen, instala la extensión de vídeo HEVC de Microsoft Store. Las fotos de la selección ya están en JPG.

## Qué se hizo

1. **Filtro automático, sin IA.** Se apartaron 409 ficheros a `_DESCARTADOS/`:
   - 287 casi duplicados (ráfagas y copias en baja calidad de una foto que ya estaba en HEIC);
   - 10 fotos movidas, revisadas a ojo (el detector proponía 48, pero la mayoría eran desenfoques buscados);
   - 18 vídeos por debajo de 1080p;
   - los 94 vídeos de Live Photo de esas fotos.

   No había duplicados exactos.
2. **Live Photos.** Los 770 clips de 2–3 s que graba el iPhone con cada foto se movieron a `_livephotos/`.
3. **Clasificación.** Claude revisó las hojas de contacto (25 fotos o 6 vídeos por imagen) y clasificó cada uno de los 2.367 ficheros: 2.199 fotos y 168 vídeos.
4. **Selección.** Se copió lo de calidad ≥4, ordenado por línea. Lo que tiene la marca antigua visible se separó en `para_retoque_marca_antigua/`.

## `clasificacion.csv`

Separador `;` y UTF-8 con BOM, para que Excel en español lo abra bien.

| Columna | Valores |
|---|---|
| `id` | `F0001`… para fotos (por fecha) y `V001`… para vídeos. Es el código que aparece en las hojas, la galería y los nombres de la selección (`F1259_q5_beige.jpg`) |
| `archivo` | Nombre del original en `FOTOS MEHARI/` |
| `tipo` | `foto` · `video` |
| `linea` | `boda` · `turismo` · `coche` (el coche solo) · `detalle` (flores, interior, cestas) · `otro` |
| `coche` | `naranja` · `beige` · `ambos` · `sin coche` |
| `marca_antigua` | `no` · `si` (funda «MEHARI TOUR SUR», capturas de @mehari_toursur) · `revisar` |
| `calidad` | 1–5. 5 = portada o anuncio; 4 = publicable; 3 = de relleno; 1–2 = no usar |
| `nota` | Descripción breve y avisos (`FOTO PROFESIONAL?`, `NO USAR`, lugar…) |
| `fecha`, `ancho`, `alto`, `duracion_s`, `mb` | Metadatos del original |

La calidad se puso mirando miniaturas: es un primer filtro, no un veredicto. Antes de publicar, la pieza pasa por `revision-marca`.

## Cifras

- **Fotos:** 1.224 de boda, 423 del coche, 326 de detalles, 55 de turismo y 171 de otros. 914 tienen calidad ≥4 y 163 calidad 5.
- **Vídeos:** 90 de boda, 31 del coche, 6 de turismo, 4 de detalle y 37 de otros. 50 tienen calidad ≥4.
- **Usables ya** (calidad ≥4 y sin marca antigua): 878 fotos y 50 vídeos.
- **Con la marca antigua visible:** 113 fotos y 17 vídeos. Otras 26 fotos y 4 vídeos están por revisar.

## Avisos antes de publicar

- **La selección NO está filtrada por matrículas ni por menores.** Muchas fotos traseras muestran la matrícula legible de los dos coches, y en varias bodas salen pajes y niños. Hay que aplicar las reglas 5 y 6 de `CLAUDE.md` §4 en cada pieza.
- **Fotos de fotógrafo profesional:** unas 75 (busca `PROFESIONAL` en la galería; ficheros `AL__`, `PER__`, `WIT_` y otros). Son de lo mejor del material. Hay que confirmar el autor y el permiso con el cliente.
- **No usar nunca:**
  - F0572 (captura de Bizum con datos bancarios: hay que borrarla del original);
  - F1934 (cita de la ITV con matrícula);
  - F1933 (app de deporte);
  - F2117 (captura con teléfono);
  - F0874 y F0982 (stories de @mehari_toursur);
  - F2081 (ilustración generada con IA).
- **Preguntar al cliente:**
  - F1926–F1929: un hombre con delantal de restaurante posa con el naranja. ¿Quién es y hay consentimiento?
  - La colaboración con la marca Bollo (el naranja con sandías; F2177 y otras).
  - Las bodas en Cáceres y Plasencia, fuera de la zona actual.

## Lo más potente para Instagram

- Atardeceres en viñedo con el beige (F0499–F0539).
- El naranja en la playa con barcas (F1839–F1861).
- Tomas de dron en una hacienda (F2130–F2134).
- Novios de pie en el coche (F0345, F1446–F1455; vídeos V066, V067, V132 y V139).
- Conducción entre girasoles (V033).
- Novia con velo larguísimo por una calle de Sevilla (V144).

## Repetir el proceso con material nuevo

Consulta [`herramientas/material/README.md`](../../herramientas/material/README.md).
