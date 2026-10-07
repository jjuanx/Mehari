# CLAUDE.md — Proyecto [MARCA POR DEFINIR] (antes conocido internamente como "Mehari")

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
- **Nombre y logo nuevos: pendientes** (hay que hablarlo con el cliente). Hasta entonces se usa el marcador visible `[MARCA POR DEFINIR]` y `@[usuario_por_definir]`. Nunca te inventes un nombre como si fuera definitivo.
- "Citroën Méhari" se puede usar **como descripción del vehículo**. Es un modelo de Citroën, así que no conviene que sea el nombre de la marca.

## 3. El negocio (datos verificados en `Referencia/`)

Detalle completo en [docs/cliente/brief.md](docs/cliente/brief.md). En resumen:

- **Flota**: dos **Citroën Méhari** clásicos (1968–1988), uno **naranja** y otro **beige**.
- **Línea Bodas**: salida de la iglesia y llegada a la hacienda o lugar de celebración. Puede ir **con chófer** o lo pueden **conducir los novios** (o alguien cercano), con una **clase de conducción previa** a la boda. El techo admite **3 configuraciones**: abierto, semiabierto y cerrado con techo solar. Lleva **dos cestas de mimbre** traseras para decorar con flores.
- **Línea Turismo** ("Sevilla Experience"): ruta por Sevilla con chófer y recogida en el hotel, de 2 h a 2 h 30. Hasta 3 personas por coche (de 1 a 6 en total) y el mismo precio de 1 a 3 personas. Hay dos tours: **Monumental** y **Romántico/Iluminado**, con paradas en Plaza de América y Plaza de España. **Entra en nuestro alcance.**
- **Zona**: Sevilla y provincia de Cádiz (Sanlúcar, San Fernando…), sobre todo haciendas e iglesias.
- **Prensa**: el *Diario de Sevilla* (19-10-2025, sección Pasarela) publicó la boda de Alberto Herrera y Blanca Llandres en Sanlúcar, con los novios saliendo "en un informal Mehari". Hay además fotos de **Carlos Herrera** con el Méhari naranja. **Tenemos consentimiento** de los Herrera y de las parejas para usar su imagen. Es el material con más gancho.
- **Precios y packs**: no hay. Nos ceñimos a lo que dicen los dossiers ("consultar disponibilidad y presupuesto").
- **Contacto**: el de los dossiers pertenece a la marca antigua. **El contacto de la marca nueva está pendiente.** Usa `[EMAIL POR DEFINIR]` y `[WHATSAPP POR DEFINIR]`.

## 4. Reglas de contenido

1. **Nada de la marca antigua a la vista.** Antes de usar una foto, revisa fundas de rueda ("@MEHARI_TOURSUR"), pegatinas, logos y marcas de agua. Si aparece, descarta la foto o márcala para retoque. Usa la skill `revision-marca`.
2. **Cada publicación tiene un objetivo y una llamada a la acción** (pedir presupuesto, escribir por WhatsApp, guardar, compartir).
3. **No inventes datos**: ni precios, ni número de bodas, ni testimonios, ni nombres. Si falta algo, pon un marcador `[ASÍ]`.
4. **Famosos y prensa**: hay consentimiento, pero se usa con elegancia y como prueba social, no como reclamo sensacionalista.
5. **Coherencia**: el nombre de la marca, los nombres de los servicios y los datos de contacto deben ser idénticos en todos los ficheros. Salen de `docs/cliente/brief.md`.

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
│  └─ planes/                ← plan de proyecto, estrategia de redes, etc.
├─ redes/instagram/          ← publicaciones, calendario editorial y reels/<fecha>_<tema>/ (fuente HyperFrames)
├─ marca/                    ← identidad: README (colores, tipos, logo), tokens.css y propuestas/
├─ web/                      ← landing (más adelante)
└─ Referencia/               ← material del cliente: dossiers, logos antiguos, fotos, prensa
```

**Ficheros pesados**: los PDF y vídeos de `Referencia/` (unos 100 MB) **no se suben a Git** (ver `.gitignore`). Se comparten por fuera del repo; el canal está pendiente de acordar. Las imágenes ligeras sí se versionan.

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
- **Estrategia y contenido de redes**: la estrategia vigente está en [docs/planes/estrategia-instagram.md](docs/planes/estrategia-instagram.md). Para ganchos, guiones y carruseles se usa la skill de terceros `social` (en inglés); nuestras reglas mandan sobre ella. **Máximo 5 hashtags** por publicación.

## 8. Mantener este fichero vivo

Actualiza `CLAUDE.md` cuando:
- se tome una decisión con el cliente (nombre, logo, contacto, precios, presupuesto de Ads…);
- cambie la estructura de carpetas o una convención;
- se cierre una pregunta de §9 (muévela a la sección correspondiente y quítala de la lista).

Las decisiones también van, con fecha y motivo, a `docs/decisiones.md`.

## 9. Pendiente de definir

- [ ] Nombre de la marca nueva y usuario de Instagram. En estudio: «Mehari Azahar» y «Mehari Getaway» (ver `marca/README.md`).
- [ ] Logo e identidad visual nuevos. No deben parecerse al logo antiguo. Paleta casi cerrada (naranja y beige de los coches); logos y tipografía en propuesta en `marca/`.
- [ ] Email, WhatsApp y teléfono de la marca nueva.
- [ ] Precios y packs (de momento, "consultar presupuesto").
- [ ] Presupuesto para publicidad en Meta.
- [ ] Reparto de tareas en el equipo (de momento, todos en todo).
- [ ] Canal para compartir los ficheros pesados (Drive, Git LFS…).
- [ ] Objetivos numéricos: bodas al año actuales y objetivo, seguidores, solicitudes al mes.
- [ ] TikTok u otras redes: ¿entran en el alcance?
- [ ] Validar con el cliente la estrategia de Instagram (v1).
- [ ] Quién responde los mensajes y solicitudes de presupuesto (cliente o equipo) y en qué plazo.
- [ ] Flujo de aprobación del contenido por parte del cliente.
- [ ] Sesión de grabación de vídeo con los dos coches y vídeos de bodas anteriores.
- [ ] Permiso del Diario de Sevilla o del fotógrafo para usar sus fotos de la boda Herrera.
