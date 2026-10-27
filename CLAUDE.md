# CLAUDE.md — Proyecto Mehari We

Contexto compartido por las sesiones de Claude Code de **Alejandro, Juan y Nico**.
Léelo entero antes de tocar nada. Todo el contenido del proyecto se redacta en **español**.

> **Regla viva:** este fichero se actualiza en la misma rama en la que cambia algo relevante
> (una decisión, un dato del cliente, una convención, una carpeta nueva). Si tu cambio deja
> algo de aquí desactualizado, lo corriges en el mismo PR. Ver §8.

---

## 1. El encargo

Somos un equipo de tres (Alejandro, Juan y Nico) contratado para **lanzar una marca nueva desde cero** y gestionar su comunicación:

1. **Gestión de redes sociales** (la parte principal del contrato): creamos y publicamos nosotros en una **cuenta de Instagram nueva**. Es probable que haya publicidad pagada en Meta (presupuesto pendiente).
2. **Web**: más adelante, una *landing page* muy estética con *motion graphics*. Todavía no se empieza.
3. **Objetivo del cliente**: conseguir clientes nuevos, más facturación y más alcance. Sobre todo, **más bodas contratadas**.

Todo lo que hagamos se juzga por una pregunta: *¿esto acerca a una pareja (o a un turista) a pedir presupuesto?*

## 2. Por qué existe la marca nueva (pivotación)

- El negocio de origen es **Mehari Tour Sur** (@mehari_toursur, @mehari_experiences). Lo llevaban **dos socios que se separan**. Nuestro cliente arranca una **marca nueva, con nombre y logo nuevos**.
- El servicio, los coches, la información y el material fotográfico **son los mismos**, y tenemos derecho a usarlos.
- **La marca nueva no debe ligarse a la antigua.** Nunca usamos el nombre "Mehari Tour Sur", su logo, su sello circular ni sus usuarios en el contenido de la marca nueva. Tampoco presentamos la marca como "antes Mehari Tour Sur".
- **Nombre: Mehari We**, con el subtítulo **«Weddings & Events»** (aceptado por el cliente el 2026-10-16). Se escribe siempre así: «Mehari» sin tilde y «We» con mayúscula. El usuario de Instagram sigue pendiente: `@[usuario_por_definir]`.
- **Logo: pendiente.** Al cliente le gustan las costillas y la pantalla de carga de la web, pero no el símbolo de la propuesta C (la parte de atrás con la rueda parecía un carro). Hay ocho propuestas nuevas en `marca/propuestas/mehari-we.html`: cinco con una pieza delantera del coche y tres solo con letras (monograma MWE, el coche formado con letras y el monograma con costillas).
- **"Citroën" no aparece en ningún sitio** del contenido de la marca (textos, hashtags, logo, vídeos, web) para no atarnos a otra marca. El coche se describe como "Méhari", "Méhari clásico" o "nuestros Méhari". El cliente ha elegido un nombre con «Mehari» sabiendo que es una marca registrada del fabricante y la primera palabra de la marca antigua: por eso el logo no imita ningún logotipo del fabricante ni el de la marca antigua.
- **La marca no se presenta como "de Sevilla" ni "de Sevilla y Cádiz".** Hoy se trabaja allí, pero la marca está pensada para abrirse a cualquier sitio. Ni el nombre, ni el logo, ni la bio, ni los eslóganes se atan a una ciudad. Nombrar el lugar concreto de una boda o la ruta de la Sevilla Experience sí está bien.

## 3. El negocio (datos verificados en `Referencia/`)

Detalle completo en [docs/cliente/brief.md](docs/cliente/brief.md). En resumen:

- **Flota**: dos **Méhari** clásicos (1968–1988), uno **naranja** y otro **beige**.
- **Línea Bodas**: salida de la iglesia y llegada a la hacienda o lugar de celebración. Puede ir **con chófer** o lo pueden **conducir los novios** (o alguien cercano), con una **clase de conducción previa** a la boda. El techo admite **3 configuraciones**: abierto, semiabierto y cerrado con techo solar. Lleva **dos cestas de mimbre** traseras para decorar con flores.
- **Línea Turismo** ("Sevilla Experience"): ruta por Sevilla con chófer y recogida en el hotel, de 2 h a 2 h 30. Hasta 3 personas por coche (de 1 a 6 en total) y el mismo precio de 1 a 3 personas. Hay dos tours: **Monumental** y **Romántico/Iluminado**, con paradas en Plaza de América y Plaza de España. **Entra en nuestro alcance.**
- **Zona actual**: Sevilla y provincia de Cádiz (Sanlúcar, San Fernando…), sobre todo haciendas e iglesias. Es donde se trabaja hoy, no la identidad de la marca (ver §2).
- **Prensa**: el *Diario de Sevilla* (19-10-2025, sección Pasarela) publicó la boda de Alberto Herrera y Blanca Llandres en Sanlúcar, con los novios saliendo "en un informal Mehari". Hay además fotos de **Carlos Herrera** con el Méhari naranja. **Tenemos consentimiento** de los Herrera y de las parejas para usar su imagen. Es el material con más gancho.
- **Precios y packs**: no hay. Nos ceñimos a lo que dicen los dossiers ("consultar disponibilidad y presupuesto").
- **Contacto**: el de los dossiers pertenece a la marca antigua y no se usa. **Teléfono y WhatsApp de la marca nueva: 625 06 42 93.** El email sigue pendiente: `[EMAIL POR DEFINIR]`.

## 4. Reglas de contenido

1. **Nada de la marca antigua a la vista.** Antes de usar una foto, revisa fundas de rueda ("@MEHARI_TOURSUR"), pegatinas, logos, marcas de agua, matrículas y caras de menores. Si aparece, descarta la foto o márcala para retoque. Usa la skill `revision-marca`.
2. **Cada publicación tiene un objetivo y una llamada a la acción** (pedir presupuesto, escribir por WhatsApp, guardar, compartir).
3. **No inventes datos**: ni precios, ni número de bodas, ni testimonios, ni nombres. Si falta algo, pon un marcador `[ASÍ]`.
4. **Famosos y prensa**: hay consentimiento, pero se usa con elegancia y como prueba social, no como reclamo sensacionalista.
5. **Menores, sin cara.** Se evita que aparezcan caras de niños o de menores de edad. Si una foto o un vídeo los muestra, se descarta, se recorta o se difumina la cara antes de publicar, aunque los padres hayan dado consentimiento a la boda.
6. **Matrículas, nunca.** La matrícula de ningún coche (los nuestros ni los de terceros) puede ser legible: se recorta, se tapa o se difumina. En fotos se prefiere la placa lisa de `herramientas/material/retocar_foto.py`, que no se nota.
7. **Sin "Citroën" y sin atarnos a Sevilla**: ver §2.
8. **Coherencia**: el nombre de la marca, los nombres de los servicios y los datos de contacto deben ser idénticos en todos los ficheros. Salen de `docs/cliente/brief.md`.

## 5. Mapa del repositorio

```
Mehari/
├─ CLAUDE.md                 ← este fichero (contexto compartido, se mantiene vivo)
├─ SKILLS.md                 ← catálogo de skills del equipo
├─ README.md                 ← presentación corta del repo
├─ .claude/skills/<nombre>/SKILL.md   ← skills compartidas; Claude las carga solas
├─ docs/
│  ├─ cliente/brief.md       ← fuente de verdad de los datos del negocio
│  ├─ decisiones.md          ← registro de decisiones (fecha, decisión, motivo)
│  ├─ material/              ← clasificación de las fotos y vídeos del cliente (clasificacion.csv) y dónde está cada cosa
│  └─ planes/                ← plan de proyecto, estrategia de redes, etc.
├─ redes/instagram/          ← publicaciones, calendario editorial, reels/<fecha>_<tema>/ (fuente HyperFrames) y destacadas/ (portadas)
├─ marca/                    ← identidad: README (colores, tipos, logo), tokens.css y propuestas/
├─ web/                      ← landing (más adelante)
├─ herramientas/material/    ← scripts para analizar, descartar, clasificar y seleccionar lotes de fotos y vídeos, para difuminar matrículas y logos en vídeo y para dejarlos lisos en fotos
└─ Referencia/               ← material del cliente: dossiers, logos antiguos, fotos, prensa
```

**Ficheros pesados**: las fotos y vídeos del cliente y los PDF y vídeos de `Referencia/` **no se suben a Git** (ver `.gitignore`). Se comparten en la carpeta de Google Drive **`Mehari We`**: `01_Material/` (selección de fotos y vídeos y galería), `02_Produccion/`, `03_Marca/` y `04_Cliente/`. Detalle en [docs/material/README.md](docs/material/README.md). Las imágenes ligeras sí se versionan.

**Material del cliente**: antes de buscar una foto o un vídeo, filtra [docs/material/clasificacion.csv](docs/material/clasificacion.csv) (línea, coche, marca antigua, calidad y nota de cada fichero) o abre la galería de Drive. Así no hace falta abrir los originales. La selección de Drive **no está filtrada por matrículas ni por menores**: aplica §4 en cada pieza.

## 6. Forma de trabajar: GitFlow

| Rama | Para qué | Se crea desde | Se fusiona en |
|---|---|---|---|
| `main` | Lo aprobado y publicado | — | — |
| `Desarrollo` | Integración (el `develop` de GitFlow) | `main` | `main` vía `release/` |
| `feature/<tema>` | Cualquier trabajo nuevo: documento, publicación, skill… | `Desarrollo` | `Desarrollo` |
| `fix/<tema>` | Corrección de algo ya integrado | `Desarrollo` | `Desarrollo` |
| `release/<versión-o-fecha>` | Preparar una entrega o publicación al cliente | `Desarrollo` | `main` y `Desarrollo` |
| `hotfix/<tema>` | Arreglo urgente sobre lo publicado | `main` | `main` y `Desarrollo` |

Normas:
- **Una rama por cada cosa.** Nunca se hace commit directo en `main` ni en `Desarrollo`.
- Nombres en minúsculas y con guiones: `feature/plan-de-proyecto`, `fix/errata-brief`.
- Se fusiona mediante **Pull Request en GitHub** (`jjuanx/Mehari`) revisado por **otro miembro** del equipo.
- Commits en español, en imperativo y concretos: `Añade brief del cliente`, `Corrige zona de servicio`.
- Antes de abrir el PR: actualiza `CLAUDE.md`, `SKILLS.md` o `docs/decisiones.md` si tu cambio lo requiere.
- Detalle paso a paso en la skill `gitflow`.

## 7. Skills compartidas

Viven en `.claude/skills/` y están catalogadas en [SKILLS.md](SKILLS.md). Al hacer *pull*, la sesión de Claude de cada uno las tiene disponibles.
- **Si una tarea se repite dos veces, conviértela en skill.**
- **Si una skill se queda corta, mejórala en una rama propia.** Que nadie se quede con versiones locales distintas.
- Toda skill nueva o modificada se registra en `SKILLS.md` en el mismo PR.
- **Motion graphics y vídeo**: tenemos las skills oficiales de **HyperFrames** (por defecto para piezas de Instagram; se entra por `hyperframes`) y de **Remotion** (`remotion-best-practices`). Son de terceros: no se editan, se actualizan copiando de nuevo desde su repositorio. Hacen falta Node.js y FFmpeg.
- **Reels**: se guionizan y producen con la skill `guion-reel` (estructura, ficha por escena y verificación), que delega el render en HyperFrames.
- Toda pieza animada pasa también por `revision-marca` antes de publicarse.
- **Diseño estático y publicidad**: `canvas-design` (oficial de Anthropic) para ilustraciones y piezas en PNG o PDF; `ad-creative` y `ads` (marketingskills) para anuncios y campañas de Meta. Son de terceros y en inglés: nuestras reglas mandan y no se generan con IA fotos de los coches ni de bodas.
- **Animaciones de marca** (entrada, transición y cierre de los reels): proyecto HyperFrames en `marca/animaciones/`, con sus renders ligeros versionados. Propuesta pendiente de aprobación.
- **Estrategia y contenido de redes**: la estrategia vigente está en [docs/planes/estrategia-instagram.md](docs/planes/estrategia-instagram.md). Para ganchos, guiones y carruseles se usa la skill de terceros `social` (en inglés); nuestras reglas mandan sobre ella. **Máximo 5 hashtags** por publicación.

## 8. Mantener este fichero vivo

Actualiza `CLAUDE.md` cuando:
- se tome una decisión con el cliente (nombre, logo, contacto, precios, presupuesto de Ads…);
- cambie la estructura de carpetas o una convención;
- se cierre una pregunta de §9 (muévela a la sección correspondiente y quítala de la lista).

Las decisiones también van, con fecha y motivo, a `docs/decisiones.md`.

## 9. Pendiente de definir

- [ ] Usuario de Instagram de Mehari We.
- [ ] Logo: elegir entre las ocho propuestas de `marca/propuestas/mehari-we.html`. No debe parecerse al logo antiguo. Paleta casi cerrada (naranja y beige de los coches); tipografía en propuesta.
- [ ] Email de la marca nueva. Confirmar que el 625 06 42 93 tiene WhatsApp.
- [ ] Precios y packs (de momento, "consultar presupuesto").
- [ ] Presupuesto para publicidad en Meta.
- [ ] Reparto de tareas en el equipo (de momento, todos en todo).
- [ ] Objetivos numéricos: bodas al año actuales y objetivo, seguidores, solicitudes al mes.
- [ ] TikTok u otras redes: ¿entran en el alcance?
- [ ] Herramienta de publicación: Meta Business Suite a mano, herramienta con API y conector para Claude, o app propia de Meta. Se decide en la semana 5 tras el piloto (ver `docs/planes/automatizacion-contenido.md`).
- [ ] Validar con el cliente la estrategia de Instagram (v1).
- [ ] Quién responde los mensajes y solicitudes de presupuesto (cliente o equipo) y en qué plazo.
- [ ] Flujo de aprobación del contenido por parte del cliente.
- [ ] Sesión de grabación de vídeo con los dos coches y vídeos de bodas anteriores.
- [ ] Permiso del Diario de Sevilla o del fotógrafo para usar sus fotos de la boda Herrera.
- [ ] Autor y permiso de las unas 75 fotos que parecen de fotógrafo profesional (ver `docs/material/README.md`).
- [ ] ¿Se trabaja también en Extremadura? Hay bodas en Cáceres y Plasencia en el material del cliente.
