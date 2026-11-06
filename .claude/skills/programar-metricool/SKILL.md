---
name: programar-metricool
description: Programa en Metricool las publicaciones aprobadas a partir de su cola-metricool.json, para que se publiquen solas en Instagram en su día y hora. Sirve para la semana de una boda (carrusel del lunes, reel del miércoles, pieza del viernes y avisos de stories) y para las piezas sueltas de pieza-boda que están en 02_Produccion de Drive. Úsala cuando el cliente apruebe el lote de una boda o una pieza suelta, cuando alguien diga «programa la semana de…» o «programa la pieza de 02_Produccion…», o para cambiar o comprobar lo que ya está programado.
---

# Programar en Metricool

El sistema está en [`docs/planes/publicacion-metricool.md`](../../../docs/planes/publicacion-metricool.md). Léelo antes de empezar. Si algo de aquí choca con ese documento, manda el documento.

## Entradas

| Entrada | Ejemplo |
|---|---|
| Carpeta de la boda | `redes/instagram/bodas/2026-10-24_la-posadilla/` |
| Carpeta de una pieza suelta (de `pieza-boda`) | `Mehari We/02_Produccion/<boda>/<pieza>/` |
| Cola | `cola-metricool.json` de la carpeta de la boda (`redes/instagram/bodas/<boda>/`) o de la carpeta de la pieza en Drive (`Mehari We/02_Produccion/<boda>/<pieza>/`). Los `medios` son relativos a la carpeta de la cola |

## Paso 0. Conector

Busca las herramientas de Metricool (`createScheduledPost`, `getScheduledPosts`, `updateScheduledPost`, `getBrandSettings`). Si no están, **para** y dile al usuario que conecte «Metricool Social Media Management» en claude.ai › Ajustes › Conectores (`publicacion-metricool.md` §2). No publiques por otra vía.

Con `getBrandSettings`, comprueba que la marca es Méhari We y que tiene Instagram `@mehari.we` conectado. Si hay varias marcas, usa solo esa.

## Paso 1. Comprobaciones (si falla una, no se programa nada)

1. `aprobacion.estado` es `aprobado`, con fecha y quién aprueba. Si no, para: **sin aprobación del cliente no se programa**.
2. Cada publicación con `estado: "pendiente"` tiene todos sus `medios` en disco:
   - Carrusel: JPEG de 1080×1440, de 2 a 10.
   - Reel: MP4 9:16. Si el modo es `automatico`, con el audio incrustado y libre de derechos (en modo `aviso` puede ir sin audio: la música se pone a mano en la app).
3. Ningún `texto` contiene `[` (marcadores sin rellenar) ni «Citroën», ni más de 5 hashtags. El teléfono es 625 06 42 93.
4. Ninguna publicación tiene `fecha: null`. Si alguna la tiene, para y pide la fecha. Las fechas son futuras, en `Europe/Madrid`, y coinciden con las fichas enlazadas (salvo en colas de `02_Produccion`, ver 6).
5. La ficha de cada pieza tiene marcada la aprobación y `revision-marca` (salvo en colas de `02_Produccion`, ver 6). Si falta algo, avisa y pregunta antes de seguir.
6. En las colas de `02_Produccion` no hay ficha (`ficha: null`): se usa en su lugar el `revision.html` de la carpeta, y `texto.txt` tiene que empezar por `Estado: LISTA`. Si `texto.txt` no empieza por `Estado: LISTA`, para (por ejemplo, si empieza por `Estado: NO PUBLICAR`). Para también si el nombre de la carpeta contiene `_PENDIENTE` (también `…_PENDIENTE-2`).

## Paso 2. Medios

Instagram descarga los medios de una URL. En orden de preferencia:
1. La subida de medios del propio conector, si la tiene.
2. Si no, sube los ficheros a Drive · `Mehari We/02_Produccion/<boda>/`, compártelos con «cualquiera con el enlace» y usa la URL de descarga directa.

Si la cola ya está en `02_Produccion`, los medios ya están en Drive: se comparten desde ahí, sin copiarlos.

Anota en `publicacion-metricool.md` §5 cuál ha funcionado la primera vez.

## Paso 3. Programar

Para cada publicación `pendiente`, en orden de fecha:

- `createScheduledPost` con red Instagram, tipo (`carrusel`/`foto` → post; `reel`; `story`), fecha y hora en `Europe/Madrid`, texto, medios en orden, ubicación y primer comentario si el conector lo admite.
- `modo: "automatico"` → publicación automática. `modo: "aviso"` → solo notificación al móvil (publicación manual).
- Guarda el id devuelto en `metricool_id` y pon `estado: "programada"`.

Si una publicación ya tiene `metricool_id`, no la crees otra vez: usa `updateScheduledPost` solo si ha cambiado algo.

## Paso 4. Verificar

1. `getScheduledPosts` del rango de la semana: cada entrada de la cola aparece una vez, con su hora, su texto y el número de medios correcto.
2. Escribe la cola actualizada. Si está en el repositorio, haz commit en la rama de la semana (`Programa en Metricool la semana de <boda>`). Si no está en el repositorio (cola de `02_Produccion`), actualiza `metricool_id` y `estado` en el propio fichero y **no hagas commit**.
3. Resumen para el grupo: qué sale solo y cuándo, qué avisos llegarán al móvil y qué hay que hacer a mano después (Collab, etiquetas, stickers).

## Cambios después de programar

Si el cliente pide un cambio: modifica la pieza y la ficha (o `revision.html` en las piezas sueltas), vuelve a exportar, `updateScheduledPost` y actualiza la cola en el mismo paso. Si se cancela una pieza, bórrala en Metricool desde su calendario (el conector no lo permite) y pon `estado: "cancelada"`.

## Checklist

- [ ] Aprobación del cliente registrada en la cola
- [ ] Medios completos y con el formato correcto; reels automáticos con música libre de derechos
- [ ] Textos sin marcadores, sin «Citroën», máximo 5 hashtags
- [ ] Ninguna `fecha` a `null`
- [ ] Colas de `02_Produccion`: `texto.txt` empieza por `Estado: LISTA` y el nombre de la carpeta no contiene `_PENDIENTE`
- [ ] Todo programado una sola vez y verificado con `getScheduledPosts`
- [ ] `metricool_id` y `estado` apuntados en la cola, con commit si la cola está en el repositorio
