---
name: revision-marca
description: Revisa que un texto, una foto o una pieza de la marca nueva no contenga rastros de la marca antigua (Mehari Tour Sur), no tenga datos inventados y sea coherente con docs/cliente/brief.md. Úsala antes de dar por buena cualquier publicación, documento o pieza gráfica, y al elegir fotos de Referencia/.
---

# Revisión de marca

La marca nueva **no debe ligarse a la antigua** (ver `CLAUDE.md` §2). Esta revisión es obligatoria antes de cerrar cualquier pieza.

## Textos

Busca y elimina:
- "Mehari Tour Sur", "Tour Sur", "Méhari Tour", "@mehari_toursur", "@mehari_experiences", "meharitoursur@gmail.com", "680 75 88 79".
- "Méhari" o "Mehari" **como nombre de marca**. Sí es válido como modelo: "Citroën Méhari", "nuestros Méhari".
- Frases como "antes conocidos como", "nueva etapa de…" o cualquier referencia a la separación de los socios.

Comprueba además:
- La marca, el usuario y los datos de contacto coinciden con `docs/cliente/brief.md`. Si siguen pendientes, debe aparecer el marcador (`[MARCA POR DEFINIR]`, etc.).
- No hay precios, cifras ni testimonios inventados.
- Hay una llamada a la acción clara.

Para buscar en el repo:
```bash
grep -rniE "tour ?sur|mehari_|meharitoursur|680 ?75 ?88 ?79" --include="*.md" . | grep -v "^./Referencia" | grep -v "^./docs/cliente/brief.md" | grep -v "^./CLAUDE.md" | grep -v "skills/revision-marca"
```

## Fotos y vídeos

Abre la imagen y revisa:
- **Fundas de la rueda de repuesto** ("@MEHARI_TOURSUR" o el logo de la furgoneta).
- Pegatinas, camisetas o merchandising con el sello circular (Giralda, Torre del Oro y palmeras) o con la "M" tricolor.
- Marcas de agua o logos en las esquinas (las páginas de los dossiers llevan la "M" arriba a la derecha).
- Portadas y páginas de texto de los dossiers: no se usan tal cual.

Resultado por cada imagen: **APTA**, **APTA CON RECORTE** (indica el encuadre) o **NO APTA** (indica el motivo).

## Salida

Devuelve una lista corta: qué has revisado, qué has encontrado y qué has corregido o queda pendiente.
