# Publicación automática con Metricool — Méhari We

| Campo | Valor |
|---|---|
| Versión | 1 |
| Fecha | 2026-11-03 |
| Qué fija | Cómo pasan las piezas aprobadas de cada boda a Metricool para que se publiquen solas en su día y hora |
| Base | [semana-boda.md](semana-boda.md) (qué se publica y cuándo) · [automatizacion-contenido.md](automatizacion-contenido.md) §3–4 (qué permite la API de Instagram) |
| Skill | [`programar-metricool`](../../.claude/skills/programar-metricool/SKILL.md) |

La cuenta `@mehari.we` está conectada a Metricool desde el 2026-10-27. Con esto se cierra la opción de publicación de `automatizacion-contenido.md` §4. Metricool queda a medio camino entre A y B: calendario y métricas, y Claude programa por su conector.

---

## 1. El flujo

```
 Boda (D) ─► semana-boda ─► piezas + fichas + cola-metricool.json ─► lote al cliente (D+6)
                                                                         │
                                         aprobación del cliente (D+8) ◄──┘
                                                   │
                                   programar-metricool (Claude + conector)
                                                   │
                     Metricool publica solo: lun D+9 · mié D+11 · vie D+13
                     y avisa al móvil de lo que hay que subir a mano (stories con stickers)
```

1. **`semana-boda`** deja en `redes/instagram/bodas/<boda>/` las piezas exportadas (`jpg/`, `reel/`) y `cola-metricool.json`: una entrada por publicación, con fecha y hora, tipo, medios, texto con hashtags, ubicación y modo.
2. **Lote al cliente** (Alejandro). Cuando el cliente contesta «OK», Alejandro rellena `aprobacion` en la cola: `estado: "aprobado"`, fecha y quién aprueba.
3. **`programar-metricool`** (cualquiera de los tres, desde Claude). Comprueba la aprobación y que no queden marcadores `[…]` en los textos, sube los medios y crea cada publicación en Metricool. Después lista lo programado para verificarlo y apunta el `metricool_id` en la cola.
4. **Metricool publica solo** en su día y hora. Las piezas en modo `aviso` llegan como notificación al móvil de Alejandro, que las sube a mano.
5. **Revisión** del lunes D+16 con las métricas de Metricool (`semana-boda.md` §8). El conector también las lee.

Hay un segundo origen de colas: las **piezas sueltas** de `pieza-boda`, que dejan su `cola-metricool.json` (una publicación, o una por historia) en `Mehari We/02_Produccion/<boda>/<pieza>/`, con `fecha: null` y los `medios` relativos a esa carpeta. Siguen los mismos pasos 2 y 3. La skill las programa desde Drive y no hace commit. Ver [sistema-piezas-boda.md](sistema-piezas-boda.md) §5.

**Sin aprobación no se programa nada.** La skill se para si `aprobacion.estado` no es `aprobado`. Si el cliente pide un cambio después de programar, se edita la publicación (`updateScheduledPost`) y la cola en el mismo paso.

## 2. Puesta en marcha (una vez)

1. **Conector de Metricool en Claude.** En claude.ai › Ajustes › Conectores › «Metricool Social Media Management», iniciar sesión con la cuenta de Metricool de la marca. Lo conecta cada uno de los tres. Herramientas: `createScheduledPost`, `getScheduledPosts`, `updateScheduledPost`, `getBestTimeToPostByNetwork`, `getBrandSettings` y las de métricas.
2. **Plan de Metricool.** Hay que comprobar que el plan contratado permite el acceso por el conector (API). Si no, el gratuito sigue sirviendo para programar a mano desde el calendario con la misma cola.
3. **Autopublicación de Instagram** activada en Metricool (cuenta profesional conectada por Facebook o Instagram Login). Hay que comprobarlo con una primera publicación de prueba.
4. **Medios con URL pública.** Instagram no recibe el fichero: lo descarga de una URL. La skill usa la subida de medios del conector si la tiene. Si no, sube los JPEG y el MP4 a Drive · `Mehari We/02_Produccion/<boda>/`, los comparte con «cualquiera con el enlace» y usa esa URL. **Comprobar en la primera boda** cuál de las dos funciona y anotarlo aquí.

## 3. Qué se publica solo y qué no

| Pieza | Modo | Por qué |
|---|---|---|
| Carrusel del lunes | `automatico` | Foto y carrusel se publican por API sin limitaciones (hasta 10 diapositivas, JPEG) |
| Reel del miércoles | `automatico` **con música incrustada** en el MP4, o `aviso` | La API no usa la biblioteca de música de Instagram: el reel sale con el audio que lleve el fichero. Si queremos una canción en tendencia, va como `aviso` y se publica a mano |
| Pieza del viernes | `automatico` | Igual que el lunes. El comentario fijado con la palabra clave se pone como primer comentario si Metricool lo permite; si no, a mano |
| Stories para compartir | `aviso` | Los stickers (enlace, encuesta, pregunta) no se pueden poner por API |
| Collab y etiquetas | A mano, justo después | **Comprobar** en la primera boda si Metricool etiqueta y propone Collab. Si no, se hace desde la app nada más publicar |
| Ubicación | `automatico` si Metricool la admite | Si no, se añade a mano |

**Música de los reels.** Como la publicación automática es lo que queremos, la regla por defecto pasa a ser: el reel se renderiza **con música libre de derechos incrustada** (la skill `media-use` la busca). Solo cuando el equipo quiera una canción concreta de Instagram, la pieza va en `aviso`. Esto cambia la decisión del 2026-10-19 («la música se añade en Instagram»), solo para los reels que se publican solos.

## 4. Formato de `cola-metricool.json`

Un fichero por boda, en su carpeta (o por pieza suelta, en su carpeta de `02_Produccion`). Ejemplo: [`redes/instagram/bodas/2026-10-24_la-posadilla/cola-metricool.json`](../../redes/instagram/bodas/2026-10-24_la-posadilla/cola-metricool.json).

| Campo | Qué es |
|---|---|
| `zona_horaria` | Siempre `Europe/Madrid`. Las fechas van en hora local, sin desfase |
| `aprobacion.estado` | `pendiente` · `aprobado` · `cambios`. Solo con `aprobado` se programa |
| `publicaciones[].fecha` | `AAAA-MM-DDTHH:MM:SS`, hora local. Minutos fuera de :00 y :30 (12:40, 20:40). Puede llegar como `null` (colas de piezas sueltas): se rellena al aprobar y, mientras sea `null`, la skill no programa |
| `tipo` | `carrusel` · `foto` · `reel` · `story` |
| `modo` | `automatico` (Metricool publica solo) · `aviso` (Metricool avisa al móvil y se publica a mano) |
| `medios` | Rutas relativas a la carpeta de la cola, en orden. Carruseles: JPEG de 1080×1440. Reels: MP4 9:16 |
| `texto` | Copy final, con los hashtags al final (máximo 5) y **sin marcadores `[…]`** |
| `metricool_id`, `estado` | Los rellena la skill: `pendiente` → `programada` → `publicada` |

## 5. Pendiente de comprobar en la primera boda

- [ ] El plan de Metricool permite usar el conector.
- [ ] Cómo se suben los medios: por el conector o con URL pública de Drive.
- [ ] Si Metricool pone ubicación, primer comentario, etiquetas y Collab en Instagram.
- [ ] Que la publicación automática del carrusel sale bien (probarlo antes con una publicación de prueba en borrador o con la hora a un minuto vista).
