# Dossier para novios

Dossier de bodas de Méhari We para enviar a las parejas que piden información. Sustituye a los dos
dossiers de la marca antigua (`Referencia/Dossier Mehari.pdf` y `Dossier Mehari (1).pdf`): mismo
contenido, ampliado para que se entienda solo, con la identidad nueva y sin rastro de la antigua.

**Estado: borrador, pendiente de revisión del equipo y del cliente.**

## Páginas (16:9, 1440×810)

1. Portada · 2. Bienvenida · 3. Los coches · 4. Foto a sangre · 5. Tres formas de llevar el techo ·
6. Cestas de mimbre · 7. ¿Quién conduce? · 8. Las llaves son vuestras (clase de conducción) ·
9. Cómo es el día · 10. El clásico que enamora + cita de prensa · 11. Galería · 12. Cómo reservar ·
13. Preguntas frecuentes · 14. Contacto

## Generar el PDF

```sh
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --no-pdf-header-footer \
  --virtual-time-budget=8000 --print-to-pdf="mehari-we-dossier-novios.pdf" \
  "file:///C:/PROYECTOS/Mehari/Mehari/comercial/dossier-novios/index.html"
```

En Mac, la misma orden con `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.
El PDF (unos 16 MB) no se versiona: se sube a Drive · `Mehari We/02_Produccion/`.

## Antes de enviarlo

- **Logo**: el aprobado, versión 03 en blanco (`marca/logo/mehari-we-blanco.svg`), en la portada y en
  el contacto. Se cambia en `<template id="logo">` de `index.html`.
- **Fotos**: todas salen de `redes/instagram/destacadas/historias/limpias/`, sin marca antigua ni
  menores. Las matrículas visibles van con placa lisa (`herramientas/material/retocar_foto.py`, PR #21):
  F0345, F0524, F0750 y F1839 vienen de `feature/grid-semilla`, y F2194 se retocó para el dossier con
  `--placa 967,643,1044,624,1043,654,966,676`. Pasa igualmente `revision-marca` sobre el PDF.
- **A validar con el cliente**: el paso a paso de la reserva (página 12), la respuesta «solo hay dos
  coches y las fechas de temporada vuelan» (página 13) y el uso de la cita del *Diario de Sevilla*.
