# SKILLS.md — Catálogo de skills del equipo

Las skills viven en `.claude/skills/<nombre>/SKILL.md`. Al hacer *pull* del repo, Claude Code las carga automáticamente en la sesión de cada uno (Alejandro, Juan y Nico). Así todos trabajamos con las mismas instrucciones.

Se invocan pidiéndolo con naturalidad ("prepara una publicación sobre…") o por su nombre (`/nueva-publicacion`).

## Catálogo

| Skill | Para qué sirve | Cuándo usarla |
|---|---|---|
| [`gitflow`](.claude/skills/gitflow/SKILL.md) | Flujo de ramas, commits y PR del equipo, más la checklist para mantener vivo el contexto | Al empezar cualquier tarea y antes de abrir un PR |
| [`nueva-publicacion`](.claude/skills/nueva-publicacion/SKILL.md) | Ficha completa de una publicación de Instagram: objetivo, material, guion, copy con CTA y hashtags | Siempre que se prepare contenido para Instagram |
| [`revision-marca`](.claude/skills/revision-marca/SKILL.md) | Comprueba que no hay rastro de la marca antigua, ni datos inventados, y que todo es coherente con el brief | Antes de cerrar cualquier pieza y al elegir fotos |
| [`guion-reel`](.claude/skills/guion-reel/SKILL.md) | De la idea al reel terminado (9:16, 15–30 s): estructura gancho, detalle, prueba, momento y cierre; ficha por escena; reglas de texto, sonido y accesibilidad; producción con HyperFrames y verificación ejecutada | Siempre que se guionice, monte o anime un reel. Completa la ficha de `nueva-publicacion` |

## Skills de terceros: estrategia y contenido de redes

| Skill | Origen | Commit | Licencia | Para qué |
|---|---|---|---|---|
| [`social`](.claude/skills/social/SKILL.md) | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | `5e721d7` | MIT | Estrategia de redes, pilares, ganchos, guiones de reel, marcos de carrusel (`references/carousel-frameworks.md`), rutina de interacción y métricas. Es la skill de redes más instalada del ecosistema (skills.sh) |

Está en inglés y es genérica: nuestras reglas (brief, marca antigua, marcadores, máximo de 5 hashtags) mandan sobre ella. Se usa junto a `nueva-publicacion`, no en su lugar. No se edita a mano; para actualizarla: `npx skills add coreyhaines31/marketingskills@social -y`, sustituir el *symlink* que crea por una copia real en `.claude/skills/social`, borrar `.agents/` y cambiar el commit de esta tabla.

## Skills de terceros: motion graphics y vídeo

Están copiadas tal cual del repositorio oficial de cada una, para que los tres tengamos la misma versión. **No se editan a mano**: si hace falta cambiar algo, se escribe una skill nuestra que las use.

| Paquete | Origen | Commit | Licencia |
|---|---|---|---|
| Remotion (`remotion-best-practices`) | [remotion-dev/skills](https://github.com/remotion-dev/skills) | `32b241b` | ver su repositorio |
| HyperFrames (21 skills) | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | `5c7f631` | Apache 2.0 |

**¿Cuál usar?**
- **HyperFrames** es la opción por defecto para las piezas de Instagram. Compone en HTML, CSS y JS y renderiza a MP4. Es más rápido de iterar con Claude.
- **Remotion** es para vídeos en React. También servirá para reutilizar componentes en la web.

| Skill | Para qué |
|---|---|
| [`hyperframes`](.claude/skills/hyperframes/SKILL.md) | **Punto de entrada.** Decide qué flujo de HyperFrames usar. Si dudas, empieza aquí |
| [`motion-graphics`](.claude/skills/motion-graphics/SKILL.md) | Piezas cortas (<10–30 s) donde el movimiento es el mensaje: tipografía cinética, logotipo animado, rótulos, mapas animados (rutas de Sevilla) |
| [`general-video`](.claude/skills/general-video/SKILL.md) | Piezas largas o de varias escenas: reels de bodas, montajes con fotos, *sizzle* de marca |
| [`music-to-video`](.claude/skills/music-to-video/SKILL.md) | Vídeo sincronizado con una canción. Ideal para reels con fotos de bodas |
| [`embedded-captions`](.claude/skills/embedded-captions/SKILL.md) | Subtítulos diseñados sobre un vídeo |
| [`talking-head-recut`](.claude/skills/talking-head-recut/SKILL.md) | Rótulos y gráficos sobre un vídeo de alguien hablando (testimonios) |
| [`media-use`](.claude/skills/media-use/SKILL.md) | Gestión de imágenes, vídeo, audio y efectos de sonido dentro de una composición |
| `hyperframes-core`, `-animation`, `-keyframes`, `-creative`, `-audio`, `-cli`, `-studio`, `-registry` | Referencia interna que usan las anteriores (API, animación, render, CLI) |
| `faceless-explainer`, `product-launch-video`, `slideshow`, `figma`, `pr-to-video`, `remotion-to-hyperframes` | Otros flujos del paquete. Probablemente no los usemos, pero se dejan para que funcione el enrutado |
| [`remotion-best-practices`](.claude/skills/remotion-best-practices/SKILL.md) | Enrutador de Remotion: crear proyecto, markup, subtítulos, mapas, multimedia y render |

**Requisitos en cada ordenador**: Node.js 18 o superior y **FFmpeg** en el PATH para renderizar MP4. En Windows: `winget install Gyan.FFmpeg`.

**Actualizar**: se vuelve a copiar la carpeta `skills/` del repositorio de origen en una rama `feature/actualizar-skills-video`, y se cambia el commit de la tabla.

## Normas

1. **Si una tarea se repite dos veces, se convierte en skill.**
2. Las skills se crean o modifican **en su propia rama** (`feature/skill-<nombre>`) y se fusionan mediante PR, como todo lo demás.
3. Toda skill nueva o modificada se **registra en esta tabla en el mismo PR**.
4. Nada de copias locales distintas: si tu versión es mejor, súbela.
5. Formato de una skill: carpeta con `SKILL.md`, cabecera con `name` y `description` (la `description` dice *qué hace* y *cuándo usarla*, porque Claude la usa para decidir si la activa), y el cuerpo en español.

## Ideas de próximas skills

- `calendario-editorial`: planificar un mes de publicaciones con los pilares de contenido.
- `informe-mensual`: métricas de Instagram y Meta Ads frente a los objetivos.
- `respuesta-dm`: plantillas para responder solicitudes de presupuesto por mensaje directo o WhatsApp.
