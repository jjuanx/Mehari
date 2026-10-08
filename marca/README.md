# Identidad de marca

Referencia única de la identidad visual: nombre, logo, colores, tipografía y recursos gráficos.
Cualquier pieza (vídeo, post, web) sale de aquí. Los valores que se usan en código viven en
[`tokens.css`](tokens.css).

> **Estado: PROPUESTA.** Nada de esta carpeta está aprobado por el cliente. Mientras tanto, el
> contenido publicado sigue usando `[MARCA POR DEFINIR]`.

## Contenido

| Fichero | Qué es |
|---|---|
| [`tokens.css`](tokens.css) | Variables CSS de colores y tipografías. Se importan en las composiciones de HyperFrames, en Remotion y en la web |
| [`propuestas/logos.html`](propuestas/logos.html) | Las dos propuestas de logo, con variantes de fondo, avatar de Instagram y muestras tipográficas. Se abre en el navegador |

Cuando el cliente elija, se añadirá `logo/` con los SVG finales (texto convertido a trazos) y los
PNG exportados.

## Nombre: dos propuestas

| | A · Mehari Azahar | B · Mehari Getaway |
|---|---|---|
| Idea | Flor del naranjo: Sevilla y flor nupcial por tradición | *Getaway car*: el coche en el que se van los novios |
| Símbolo | Flor de azahar de cinco pétalos | El Méhari de perfil dentro de un arco de medio punto |
| Tono | Romántico, luminoso | Desenfadado, viajero |

**Riesgos abiertos** (hay que resolverlos antes de cerrar el nombre):
- **«Mehari»** es una marca de Citroën (Stellantis) y la primera palabra de la marca antigua. Ver
  CLAUDE.md §2. Por eso los dos logos ponen el peso en la segunda palabra: así se puede quitar
  «Mehari» sin rehacerlos.
- **Gateway / Getaway**: la maqueta usa *Getaway* (escapada). Si se prefiere *Gateway* (puerta), el
  símbolo del arco sigue valiendo.

## Colores

| Token | Nombre | Hex | Uso |
|---|---|---|---|
| `--naranja` | Naranja Méhari | `#EE7D1F` | Color principal, fondos y símbolo |
| `--beige` | Beige arena | `#DCC6A0` | Segundo color, fondos |
| `--cal` | Cal | `#F7F1E6` | Fondo claro por defecto |
| `--tinta` | Tinta capota | `#2B211A` | Texto y fondo oscuro (no usar negro puro) |
| `--naranja-oscuro` | Naranja tostado | `#C2560E` | Texto naranja sobre fondo claro (el naranja principal no tiene contraste suficiente para texto pequeño) |
| `--verde-naranjo` | Verde naranjo | `#55703F` | Solo acentos |
| `--azahar` | Blanco azahar | `#FFFCF5` | Texto y símbolo sobre naranja o tinta |

## Tipografía (pendiente de elegir)

Todas son de Google Fonts con licencia OFL: gratis para uso comercial.

1. **Fraunces + Jost**: serif suave con un punto setentero para titulares y palo seco geométrico para el texto. Va con la propuesta A. Es la provisional de `tokens.css`.
2. **Jost + Instrument Serif**: mayúsculas espaciadas con un acento en cursiva. Va con la propuesta B.
3. **Cormorant Garamond + DM Sans**: la más clásica y nupcial. Se parece más al logo antiguo y es la más vista en bodas.

Reglas: nada de caligrafía (la usa el logo antiguo) y una sola familia de titular en todo el sistema.

## Recurso gráfico: las costillas

Los paneles acanalados de las puertas del Méhari, convertidos en franjas horizontales naranja y
naranja tostado. Sirven de fondo, separador o transición en vídeo.

## Lo que no se hace

- Monograma «M» serif, caligrafía o sello circular: son los rasgos del logo antiguo.
- Usar el logo con el texto como fuente web en piezas finales: se usa el SVG con el texto convertido a trazos.
- Inventar colores fuera de esta tabla. Si hace falta uno nuevo, se añade aquí y en `tokens.css`.
