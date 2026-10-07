# SKILLS.md — Catálogo de skills del equipo

Las skills viven en `.claude/skills/<nombre>/SKILL.md`. Al hacer *pull* del repo, Claude Code las carga automáticamente en la sesión de cada uno (Alejandro, Juan y Nico). Así todos trabajamos con las mismas instrucciones.

Se invocan pidiéndolo con naturalidad ("prepara una publicación sobre…") o por su nombre (`/nueva-publicacion`).

## Catálogo

| Skill | Para qué sirve | Cuándo usarla |
|---|---|---|
| [`gitflow`](.claude/skills/gitflow/SKILL.md) | Flujo de ramas, commits y PR del equipo, más la checklist para mantener vivo el contexto | Al empezar cualquier tarea y antes de abrir un PR |
| [`nueva-publicacion`](.claude/skills/nueva-publicacion/SKILL.md) | Ficha completa de una publicación de Instagram: objetivo, material, guion, copy con CTA y hashtags | Siempre que se prepare contenido para Instagram |
| [`revision-marca`](.claude/skills/revision-marca/SKILL.md) | Comprueba que no hay rastro de la marca antigua, ni datos inventados, y que todo es coherente con el brief | Antes de cerrar cualquier pieza y al elegir fotos |

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
