# Identidad de marca

Referencia única de la identidad visual: nombre, logo, colores, tipografía y recursos gráficos.
Cualquier pieza (vídeo, post, web) sale de aquí. Los valores que se usan en código viven en
[`tokens.css`](tokens.css).

> **Estado:** el nombre (**Méhari We · Wedding & Events**) y el logo están aprobados (2026-10-28). También
> lo están las costillas como recurso y la paleta. La tipografía de las piezas sigue pendiente.

## Contenido

| Fichero | Qué es |
|---|---|
| [`tokens.css`](tokens.css) | Variables CSS de colores y tipografías. Se importan en las composiciones de HyperFrames, en Remotion y en la web |
| [`logo/`](logo/) | **Logo aprobado.** SVG de la versión principal (03) en naranja, blanco y tinta, SVG de las versiones 01 y 02 y los PNG originales de la grafista |
| [`propuestas/mehari-we.html`](propuestas/mehari-we.html) | Histórico: ocho propuestas de logo para Mehari We: cinco con las costillas y una pieza delantera del coche (frontal, parabrisas, capó, perfil y frontal a trazo) y tres de lettering (monograma MWE, coche formado con las letras y monograma con costillas), con logotipo, avatar y pantalla de carga. Se abre en el navegador |
| [`propuestas/logos.html`](propuestas/logos.html) | Histórico: propuestas A (Azahar) y B (Getaway), descartadas con el nombre |
| [`propuestas/costillas.html`](propuestas/costillas.html) | Histórico: propuesta C. Gustan las costillas; el símbolo (trasera con rueda) se descarta porque parece un carro |

## Logo

Lo diseñó una grafista contratada por el cliente y el cliente lo aprobó el 2026-10-28. **Se usa tal
cual**: no se redibuja, no se recoloca el texto ni se cambian proporciones.

- **Idea:** la M de arriba es la de Méhari y la W de abajo, la de Wedding; las dos enmarcan el nombre.
- **Versión principal: 03**, trazo fino y los cuatro brazos iguales. Las versiones 01 (trazo grueso,
  subtítulo en serif) y 02 (trazo fino, M más estrecha) son de la misma entrega y quedan como alternativas.
- **Colores:** naranja del logo (`--naranja-logo`, `#F35F03`) sobre fondo claro; blanco azahar sobre
  naranja, tinta o foto; tinta sobre beige o cal. No se usa en otros colores.
- **Tipografías del logo:** Charter (el nombre) y Metropolis Bold (el subtítulo). En los SVG van
  convertidas a trazos, así que no hace falta instalarlas. Charter venía en un `.ttc` del Mac: no se
  sube al repo hasta confirmar su licencia. Metropolis es OFL.

| Fichero | Uso |
|---|---|
| `logo/mehari-we-naranja.svg` | Principal, sobre fondo claro |
| `logo/mehari-we-blanco.svg` | Sobre naranja, tinta o foto |
| `logo/mehari-we-tinta.svg` | Sobre beige o cal, cuando el naranja no conviene |
| `logo/mehari-we-v01-naranja.svg`, `logo/mehari-we-v02-naranja.svg` | Versiones alternativas |
| `logo/original/LOGO_0X.png` | PNG originales de la grafista (A4, transparentes) |

Los SVG están **vectorizados desde los PNG** con `herramientas/marca/vectorizar_logo.py`, porque la
grafista entregó EPS de Illustrator y aquí no hay con qué abrirlos. Coinciden con el original en más del
99 % de los píxeles. Cuando la grafista mande el SVG o el PDF exportado desde Illustrator, se sustituyen.
Los EPS originales están en Drive · `Mehari We/03_Marca/`.

## Nombre: Méhari We

**Méhari We · Wedding & Events**, con tilde y en singular, como en el logo (2026-10-28). Sustituye a
«Mehari We · Weddings & Events», aprobado el 2026-10-16. Las dos propuestas anteriores de nombre quedan
como histórico:

### Propuestas descartadas

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
| `--naranja` | Naranja Méhari | `#EE7D1F` | Color principal, fondos y costillas |
| `--naranja-logo` | Naranja del logo | `#F35F03` | Solo el logo. Es el de la entrega de la grafista |
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
- Redibujar, deformar o recolorear el logo, o componer el nombre con otra fuente en su lugar.
- Usar el logo con el texto como fuente web en piezas finales: se usa el SVG con el texto convertido a trazos.
- Inventar colores fuera de esta tabla. Si hace falta uno nuevo, se añade aquí y en `tokens.css`.
