# Animaciones de costillas

Recursos animados de marca para los reels y la cuenta de Instagram, hechos con HyperFrames a partir del símbolo **C · El detalle** (ver `marca/propuestas/costillas.html`) y de la paleta de `marca/tokens.css`.

> **Estado:** el **cierre** ya lleva el logo aprobado (2026-10-28) y el nombre actual, «Méhari We · Wedding & Events» (actualizado el 2026-11-03). La **entrada** sigue con el coche de costillas de la propuesta C y está pendiente de pasar a la identidad nueva. La **transición** son solo franjas de color y vale tal cual.

## Las piezas

| Pieza | Fichero fuente | Render | Duración | Uso |
|---|---|---|---|---|
| **Cierre** | `index.html` | `renders/cierre.mp4` | 4 s | Último plano de cada reel: las costillas entran desde los lados, se estrechan en un friso y aparece debajo el logo aprobado (con «Méhari We · Wedding & Events»); después, «Escribidnos vuestra fecha» y el WhatsApp |
| **Entrada** | `compositions/entrada.html` | `renders/entrada.webm` (transparente) | 2,6 s | Encima del **primer plano** del reel: el coche se monta con las costillas y sale por la derecha. No sustituye al gancho (regla de `guion-reel`), va por encima |
| **Transición** | `compositions/transicion.html` | `renders/transicion.webm` (transparente) | 0,85 s | Entre dos escenas. A los **0,41 s** las franjas tapan toda la pantalla: ahí se corta al plano siguiente |

`renders/demo-entrada-sobre-foto.mp4` es una prueba de la entrada encima de una foto de boda.

## Cómo usarlas

- **Transparencia**: `entrada.webm` y `transicion.webm` llevan canal alfa (VP9). Para editores que no lean WebM con alfa, se renderiza en MOV (ProRes 4444): `npx hyperframes render . -c compositions/entrada.html --format mov -o renders/entrada.mov`. El MOV no se sube a Git (pesa unos 16 MB).
- **Altura del coche en la entrada**: si el plano de debajo tiene algo importante en esa zona (por ejemplo, el coche naranja real), se cambia la variable `altura` (píxeles desde arriba; por defecto 1150): `npx hyperframes render . -c compositions/entrada.html --variables '{"altura":420}' --format webm -o renders/entrada-arriba.webm`.
- **Llamada a la acción y WhatsApp del cierre**: variables `cta` y `whatsapp` (por defecto, «Escribidnos vuestra fecha» y «625 06 42 93»). El nombre va dentro del logo (`assets/marca/mehari-we-blanco.svg`, copia de `marca/logo/`), que se usa tal cual. Para volver a renderizar: `npx hyperframes render . -o renders/cierre.mp4`.
- **GSAP en local** (`assets/vendor/gsap.min.js`): el render no depende del CDN.
- **Previsualizar y editar**: `npx hyperframes preview` desde esta carpeta abre Studio.

## Detalles técnicos

- Formato 9:16 (1080 × 1920), 30 fps. El texto del cierre queda por encima de la franja de botones de Instagram.
- Tipografías Fraunces y Jost incrustadas desde `assets/fonts/` (licencia OFL), para que el render no dependa de la red.
- Paleta copiada de `marca/tokens.css`. Si cambia la paleta, hay que cambiarla también en las tres composiciones.
- `hyperframes check` pasa sin errores en las tres; los textos del cierre cumplen el contraste AA.
- Los renders ligeros de esta carpeta sí se versionan (excepción en `.gitignore`); el resto de vídeos del repo no.
