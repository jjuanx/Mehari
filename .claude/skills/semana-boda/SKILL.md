---
name: semana-boda
description: Prepara la semana de publicaciones de una boda de Méhari We a partir de su carpeta de Drive (fotos, vídeos y ficha). Selecciona el material, decide las tres publicaciones fijas (lunes carrusel «La boda», miércoles reel «El momento», viernes «Vuestra elección»), las stories, las fechas de producción y aprobación y quién hace cada pieza. Úsala cada vez que llegue el material de una boda o alguien diga «ya está la carpeta de la boda de…».
---

# Semana de una boda

El sistema está en [`docs/planes/semana-boda.md`](../../../docs/planes/semana-boda.md). **Léelo antes de empezar**: esta skill solo lo aplica. Si algo de aquí choca con ese documento, manda el documento.

## Entradas

| Entrada | Obligatoria | Ejemplo |
|---|---|---|
| Carpeta de la boda | Sí | Enlace de Drive o ruta local de `Mehari We/01_Material/Bodas/2026-11-07_sanlucar/` |
| Fecha de la boda (D) | Sí | Sale del nombre de la carpeta o de la ficha |
| Ficha de la boda | Recomendada | Fichero `ficha` dentro de la carpeta |
| Otras bodas pendientes | No | Si hay dos bodas en el mismo fin de semana (ver casos especiales) |

Si falta la ficha, sigue con lo que haya y apunta cada dato que falte como `[PENDIENTE: …]`. **Nunca inventes nombres, lugares ni flores**: si no se reconoce el lugar en la foto ni lo dice la ficha, se pregunta.

## Paso 1. Llegar al material

1. **Conector de Google Drive.** Lista el contenido con `search_files` (`parentId = '<id de la carpeta>'`, `excludeContentSnippets: true`, `pageSize: 100`) y sigue el `nextPageToken` hasta el final. El listado no cabe en el contexto: se guarda solo en `tool-results/` y se resume con Python. Lee la ficha con `read_file_content`.
2. **Descargar con el conector.** `download_file_content` devuelve el fichero en base64. Como no cabe en el contexto, la herramienta lo guarda en `tool-results/` como JSON (`{content, title, …}`): decodifícalo con Python en el scratchpad, nunca en el repositorio. Lanza las descargas en tandas de unas 12 en paralelo y decodifica después de cada tanda.
   - **Límite de 10 MB por fichero.** Por encima, el conector devuelve «File too large for download». Las fotos HEIC (2–8 MB) y los Live Photos (2–9 MB) bajan sin problema; **los vídeos largos no**. Apúntalos en el plan como «sin revisar» y que los revise quien monte el reel (Nico), o pide la ruta local.
   - Las fotos del iPhone vienen en **HEIC**: hace falta `pip install pillow-heif` para abrirlas con Pillow. La fecha y la hora están en el EXIF (etiqueta 36867): con ellas se fija D y se ordena el día.
   - Los **Live Photos** (`IMG_xxxx.MOV` con el mismo número que una foto, 2–3 s, 1440×1920 y ya en SDR) bastan para montar un reel si no hay vídeos. Un `.MOV` pequeño sin foto al lado también es un Live Photo.
3. **Si el conector no ve el contenido** (ya ha pasado: solo veía la carpeta raíz de `Mehari We`), pide la ruta local. Con Google Drive para escritorio, la carpeta compartida aparece en el ordenador si se añade un acceso directo en «Mi unidad», por ejemplo `G:\Mi unidad\Mehari We\01_Material\Bodas\…`.
4. **No copies el material al repositorio.** Las fotos y vídeos no entran en Git (`CLAUDE.md` §5).

## Paso 2. Ver y elegir

- **Hasta unas 40 fotos**: míralas una a una y refiérete a cada una por su nombre de fichero.
- **Más de 40, o con vídeos**: genera hojas de contacto con las herramientas de material sobre la carpeta local:
  ```bash
  python herramientas/material/1_analizar.py "<carpeta>"
  python herramientas/material/4_hojas_contacto.py "<carpeta>"
  ```
  Los códigos (F0001, V001…) son **de esa boda**, no los del catálogo general. Escríbelos siempre con el prefijo de la boda: `2026-11-07_sanlucar/F0012`.
- Clasifica cada pieza útil por el paso del día que muestra (iglesia, salida, cestas, volante, llegada, momento, detalle) y ponle calidad 1–5 con los criterios de `herramientas/material/README.md`.
- **Busca la funda de rueda con «@MEHARI_TOURSUR».** En la boda del 24-10-2026 el beige aún la llevaba y salía en casi todas las fotos laterales y traseras. Si aparece, márcala en cada foto y en cada clip, y ponla la primera en «Pendiente» para que el cliente la quite antes de la siguiente boda.
- **Pasa `revision-marca` a lo elegido** y marca cada pieza como APTA, APTA CON RETOQUE (qué hay que tapar: matrícula, chevrones, cara de un menor) o NO APTA. Las fotos se retocan con `retocar_foto.py` (placa lisa) y los vídeos con `difuminar.py`.

## Paso 3. Decidir la semana

Con el material elegido, rellena las tres piezas tal como las define `docs/planes/semana-boda.md` §3:

1. **Lunes · La boda.** Asigna una foto a cada paso de la estructura fija. Si falta un paso, sáltalo; si quedan menos de 6 fotos, aplica el caso «Poco material».
2. **Miércoles · El momento.** Elige el gancho: el plano con más gente y más movimiento. Coge uno de los cuatro ganchos que **no se usara la semana anterior** (mira la última semana en `redes/instagram/bodas/`). Ordena los planos con la estructura de `guion-reel`.
3. **Viernes · Vuestra elección.** Elige el tema que mejor muestre esta boda y que **no se usara la semana anterior**. Decide el formato (reel corto, carrusel o foto) y la palabra clave.

Luego calcula las fechas a partir de D: lote al cliente en D+6, aprobación en D+8 y publicación en D+9, D+11 y D+13. Si D no es sábado, mantén los días de la semana (lunes, miércoles y viernes de la semana que empieza en D+9).

## Paso 4. Escribir

1. **El plan de la semana** en `redes/instagram/bodas/AAAA-MM-DD_<lugar>/README.md`, con la plantilla de abajo.
2. **Una ficha por publicación** con la skill `nueva-publicacion`, en `redes/instagram/publicaciones/` (`AAAA-MM-DD_carrusel_<tema>.md`, etc.), con el responsable que marca el reparto.
3. Los textos siguen el tono de la estrategia (§4): tuteo en plural, concretos, sin rayas largas, sin «experiencia única». Datos solo del brief y de la ficha. Contacto: WhatsApp **625 06 42 93**. Entre 3 y 5 hashtags.
4. Los reels se producen después, con la skill `guion-reel`. Esta skill solo deja el guion de escenas.

### Plantilla del plan

```markdown
# Semana de la boda: <lugar>, <fecha D>

| Campo | Valor |
|---|---|
| Boda | <fecha> · <iglesia> → <hacienda> · coche <naranja/beige> · <con chófer / conducido por los novios> |
| Carpeta | <enlace o ruta> |
| Permiso de caras y nombres | Sí / No / [PENDIENTE] |
| Créditos | Fotógrafo <@>, hacienda <@>, florista <@> |
| Lote al cliente | <D+6> · Aprobación como tarde <D+8> |
| Publicación | Lun <D+9> · Mié <D+11> · Vie <D+13> |

## Material elegido
| Código o fichero | Qué es | Paso del día | Calidad | revision-marca |

## Lunes <fecha> · La boda (carrusel) · Juan
Diapositiva por diapositiva, con el fichero y el rótulo. Borrador del texto. Hashtags. Etiquetas y Collab.

## Miércoles <fecha> · El momento (reel) · Nico
Gancho elegido y por qué. Escenas: plano, tramo (s), texto en pantalla. Borrador del texto. Hashtags.

## Viernes <fecha> · Vuestra elección (<formato>) · <Nico o Juan>
Tema y por qué. Material. Palabra clave. Borrador del texto. Hashtags.

## Stories
Tabla de `semana-boda.md` §4 con el material concreto de cada día.

## Retoques
Lista de cada fichero con lo que hay que tapar y la herramienta.

## Pendiente
Datos que faltan de la ficha y preguntas al cliente.
```

## Paso 5. Avisar

Termina con un resumen corto para el grupo del equipo: las tres piezas en una línea cada una, quién hace cada cosa, la fecha del envío al cliente y lo que falta. Nada más.

## Casos especiales

Aplica la tabla de `docs/planes/semana-boda.md` §7: dos bodas el mismo fin de semana, fin de semana sin boda, sin permiso de caras, poco material, material tardío y bodas fuera de la zona habitual.

## Checklist

- [ ] Todo el material elegido ha pasado `revision-marca`, con los retoques apuntados (funda de rueda incluida)
- [ ] Los vídeos que el conector no pudo bajar (más de 10 MB) figuran en el plan como «sin revisar»
- [ ] Las tres piezas siguen la estructura fija y no repiten gancho ni tema de la semana anterior
- [ ] Fechas calculadas desde D: lote D+6, aprobación D+8, publicación D+9, D+11 y D+13
- [ ] Caras y nombres solo con permiso en la ficha; nada de menores ni de matrículas
- [ ] Sin «Citroën», sin «de Sevilla» como identidad y sin datos inventados
- [ ] Plan en `redes/instagram/bodas/` y una ficha por pieza en `redes/instagram/publicaciones/`
