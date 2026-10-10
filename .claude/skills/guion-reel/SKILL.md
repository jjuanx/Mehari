---
name: guion-reel
description: Convierte una idea en un reel de Instagram terminado para la marca nueva (9:16, 15–30 s) con guion escena a escena, motion graphics con HyperFrames, sonido, subtítulos y verificación. Úsala siempre que haya que guionizar, montar o animar un reel, ya sea con fotos o con vídeo, de bodas o de turismo. Completa la ficha de `nueva-publicacion`, no la sustituye.
---

# Guion y producción de un reel

Basada en un prompt de *explainer motion studio* que circula en redes. Lo hemos adaptado: un reel nuestro no explica un concepto, sino que hace que una pareja o un turista **quiera pedir disponibilidad**.

## Objetivo

Convertir una idea en un reel terminado que deje al público con **una sola idea nueva** y **una acción clara** en 15–30 s.

El entregable es el **MP4 renderizado** (con sonido y subtítulos), la **fuente** que lo vuelve a renderizar y la **ficha** de la publicación completa. Un plan, un moodboard o un fotograma suelto no son el entregable.

## Papel

Haces de estudio completo: dirección creativa, guion, motion design, sonido y render. Si el encargo es escueto, decide tú y deja escrita la decisión (ver [Decisiones](#decisiones)).

## Principios

- **Primero la forma y después el pulido.** Antes de animar nada, fija la idea y lo que la pareja tiene que llevarse. El pulido va al final.
- **Antes de diseñar, responde a tres preguntas**: ¿para quién es?, ¿qué comunicamos?, ¿qué debe hacer después de verlo?
- **Nunca desde cero.** Ánclalo al material real: fotos de `Referencia/`, los dos Méhari, haciendas, iglesias, prensa. Sin esa base sale el aspecto genérico que hace cualquier modelo.
- **Abre y después decide.** Para la primera pieza de una serie o de un estilo nuevo, prepara 3–4 direcciones en un HTML (ver [Flujo](#flujo)).
- **Contención.** Puedes hacer cualquier cosa, así que quita lo que no sirva a la idea.

## Entradas

| Entrada | Ejemplo |
|---|---|
| Idea | "Los novios pueden conducirlo ellos" |
| Línea y pilar | Bodas · *Hazlo a tu manera* (pilares en `docs/planes/estrategia-instagram.md` §5) |
| Objetivo | Alcance · Confianza · Conversión · Comunidad |
| Público y lo que ya cree | Pareja que se casa y piensa que el coche de boda siempre lleva chófer |
| Después de verlo podrá… | Decir "podemos conducirlo nosotros" y pedir disponibilidad |
| Llamada a la acción | "Pide disponibilidad para tu fecha" · `[WHATSAPP POR DEFINIR]` |
| Duración | 15–30 s |
| Formato | Original **9:16 (1080×1920)**. Portada que funcione recortada en la rejilla del perfil |
| Material | Rutas de `Referencia/` con su resultado de `revision-marca` |
| Identidad | `marca/` cuando exista. Mientras tanto, tokens provisionales marcados como tales |

## Descubrimiento

- Escribe **la pregunta que responde el reel**, con las palabras de la pareja: "¿Y si lo llevamos nosotros?".
- Separa los datos en **imprescindibles** y **lista de recortes**. Lo que va a la lista de recortes no entra.
- Busca **el gancho**: la imagen o la idea que para el scroll en el primer segundo. A menudo es algo que el público da por hecho y que no es así ("el coche de boda siempre lleva chófer").
- **Muestra lo real.** Usa una metáfora solo si hace la idea más exacta, y casi nunca la hace.

## Estructura (15–30 s)

| Tramo | % | Qué pasa |
|---|---|---|
| **Gancho** | 0–10 % | Una imagen en movimiento que para el scroll: la salida de la iglesia, las manos al volante, los invitados rodeando el coche. **Nunca** un rótulo de título ni un logotipo |
| **Detalle** | 10–45 % | Un diferencial por plano (techo, cestas, color, clase de conducción). Un elemento cada vez |
| **Prueba** | 45–75 % | Un caso real: una boda real, la prensa o los invitados. Que se vea pasar, no que se cuente |
| **Momento** | 75–90 % | El instante emocional: arrancan, saludan, el arroz. Aquí la pareja se imagina dentro |
| **Cierre** | 90–100 % | La imagen del gancho vista de nuevo, ahora con sentido, y la **llamada a la acción** |

Para **turismo** (*Sevilla Experience*) el arco es el mismo: el gancho es Plaza de España desde el coche, el detalle es la recogida en el hotel y el tour, la prueba son las paradas y el cierre es "reserva tu ruta". El texto en pantalla va en inglés o en ES/EN según el público de la pieza.

## Sistema visual

- Saca paleta, tipografía y espaciado de `marca/` en forma de **tokens** antes de dibujar nada. Si `marca/` aún no existe, define tokens provisionales, márcalos `PROVISIONAL` en la ficha y no los presentes como identidad definitiva.
- Fondo neutro y cálido, **un acento** (los coches ya aportan el naranja y el beige), dos tipografías y una retícula.
- Mejor las fotos reales y el texto limpio que las ilustraciones.
- **Zonas seguras**: el texto y lo importante van dentro del 80 % central (*title-safe* de `hyperframes-studio`). Deja libres la franja superior y, sobre todo, la inferior, donde Instagram pone el texto, el usuario y los botones.
- **Prohibido**: brillos de neón, manchas 3D de stock, rótulos con degradado, partículas flotantes, cifras inventadas, clipart de boda (corazones, anillos, palomas) y cualquier rastro de la marca antigua.

## Lenguaje del movimiento

- **El movimiento significa algo**: agrupa, ordena, muestra causa o escala. Si no comunica nada, sobra.
- **Un foco cada vez**: lo demás se queda quieto.
- **Los objetos sobreviven entre escenas y se transforman** en lugar de sustituirse. Por ejemplo: el coche sigue siendo el hilo, la cesta vacía se llena de flores y el techo pasa de cerrado a abierto.
- **Curvas suaves que se asientan sin rebote.** En las fotos, movimiento de cámara lento (*Ken Burns*). La cámara se mueve entre ideas y se queda quieta mientras se lee el texto.
- Los cortes caen en el **pulso de la música**.

## Ficha de escena

Para cada escena escribe:

```markdown
### E<n> · <inicio>–<fin> s
- **Aporta**: lo único que añade esta escena
- **Plano**: qué se ve y en qué orden de importancia
- **Material**: `Referencia/...` · revision-marca: APTA / APTA CON RECORTE (encuadre)
- **Movimiento**: entrada, acción clave, asentamiento y salida
- **Texto en pantalla**: como mucho 8 palabras por línea y 2 líneas
- **Sonido**: lo que marca la acción clave (golpe de música, motor, campanas, risas)
- **Comprobación**: qué puede decir ahora quien lo ve que antes no podía
```

## Texto

- Como mucho **dos líneas en pantalla a la vez**, con palabras llanas.
- El texto en pantalla son **anclas**, no el *copy* completo. El *copy* va en la ficha de `nueva-publicacion`.
- **Un nombre para cada cosa** y siempre el mismo, sacado de `docs/cliente/brief.md`: "Citroën Méhari", "Sevilla Experience", "tour Monumental"…
- **Cada dato tiene su fuente en el brief**; si no la tiene, se quita o se sustituye por un marcador (`[ASÍ]`). Nada de precios, número de bodas ni testimonios inventados.
- Tono de `docs/planes/estrategia-instagram.md` §4: cálido, concreto y sin muletillas de texto generado ("no es X, es Y", "experiencia única", rayas largas).

## Sonido

- **Música con derechos claros.** Con una cuenta de empresa, solo la biblioteca libre de derechos de Meta o una licencia comercial; nada de canciones de moda sin licencia. Si la música se añade en la app al publicar, renderiza sin ella pero con los cortes pensados para el pulso, y apunta la pista en la ficha.
- **Sonido real** siempre que lo haya: el motor del Méhari, campanas, aplausos, arroz. Pesa más que cualquier efecto.
- Efectos suaves **solo en acciones con significado**. Si hay voz, baja la música por debajo de ella (*ducking*).
- Volumen de referencia: unos −14 LUFS integrados y un pico real de −1 dBTP como máximo.
- **El reel se tiene que entender sin sonido.** La mayoría lo verá así.

## Accesibilidad

- Contraste de al menos **4.5:1** entre el texto y el fondo.
- Si hay voz: subtítulos quemados en el vídeo y además un `.srt`.
- El color nunca es la única señal.
- Ningún destello de más de 3 por segundo.
- **Texto alternativo** en la ficha de la publicación.

## Producción técnica

No reinventes el render: **delega en HyperFrames**, que ya garantiza un render determinista.

1. Entra siempre por la skill `hyperframes`, que decide el flujo.
2. Lo normal será `music-to-video` (fotos con música) o `general-video` (varias escenas con vídeo). Para subtítulos sobre vídeo, `embedded-captions`.
3. El proyecto vive en `redes/instagram/reels/<AAAA-MM-DD>_<tema>/` (o `sin-fecha_<tema>/`). Los MP4 **no se suben a Git** (`.gitignore`), así que se comparten por el mismo canal que el material pesado.

## Flujo

1. **Idea en una frase** y qué hará el público después de verlo.
2. **Ficha** abierta con `nueva-publicacion` (formato Reel). Esta skill rellena su sección *Guion*.
3. **Direcciones** (solo en la primera pieza de una serie o de un estilo nuevo): `direcciones.html` con 3–4 propuestas una al lado de otra. Marca la ganadora y por qué; el fichero sirve de registro de la decisión.
4. **Storyboard**: hoja de contactos con un fotograma por escena.
5. **Animática** y pase de tiempos: ¿se entiende el gancho en 1 s? ¿Da tiempo a leer cada texto?
6. **Construcción completa** en HyperFrames.
7. **Sonido y subtítulos.**
8. **Verificación** (siguiente apartado).
9. **Exportación** y entrega para aprobación.

## Verificación

Hay que ejecutar estas comprobaciones, no basta con darlas por hechas:

- `hyperframes check` sin errores.
- **Un fotograma por escena**, leyendo cada línea a **390 px de ancho** (pantalla de móvil).
- **El primer segundo por separado**: ¿para el scroll y se entiende qué es?
- Verlo **sin sonido** y después **solo escucharlo**.
- **`revision-marca`** sobre cada fotograma y cada texto: fundas de rueda, pegatinas, la "M", el nombre antiguo.
- Una revisión de diseño hecha por otra persona del equipo o por un subagente revisor, con las tres preguntas de los principios. Después, el pase de accesibilidad.
- Cada corrección se entrega con su **par de fotogramas antes y después**.

## Entrega

En la carpeta del reel:

- `reel_9x16.mp4` (fuera de Git) y la portada (`portada.png`).
- `subtitulos.srt` si hay voz.
- `contactos.png` (hoja de contactos final).
- La fuente de HyperFrames.
- La ficha de la publicación actualizada, con una línea **Probado:** que enumere solo las comprobaciones que se han ejecutado de verdad.

## Decisiones

- Las decisiones creativas de la pieza (música, orden de escenas, dirección elegida) se apuntan en **una línea cada una** en la sección `## Decisiones` de la ficha de la publicación.
- Las que afectan a toda la marca (un estilo de reel que se va a repetir, una tipografía, una plantilla) se registran además en `docs/decisiones.md`.

## Cuándo parar y preguntar

Las decisiones creativas no se paran: se toman y se anotan. **Sí se para** cuando:

- **Hay un problema de derechos**: música sin licencia clara, o fotos de prensa de la boda Herrera mientras siga pendiente el permiso del *Diario de Sevilla* o del fotógrafo (`CLAUDE.md` §9).
- **El material lleva la marca antigua** y no se puede recortar ni retocar.
- **Falta un dato que cambia la pieza** (nombre, contacto, precio): se pone el marcador y se avisa.
- **Toca publicar.** Nunca se publica sin la aprobación del cliente y del equipo.
