---
name: gitflow
description: Flujo GitFlow del equipo para cualquier cambio en el repo (documento, publicación, skill, web). Úsala al empezar una tarea nueva, al hacer commit, al abrir un PR o al preparar una entrega. Incluye la obligación de actualizar CLAUDE.md, SKILLS.md y docs/decisiones.md.
---

# GitFlow del equipo

Ramas: `main` (lo publicado), `Desarrollo` (integración), `feature/*`, `fix/*`, `release/*` y `hotfix/*`. La tabla completa está en `CLAUDE.md` §6.

## 1. Empezar una tarea

```bash
git checkout Desarrollo
git pull origin Desarrollo
git checkout -b feature/<tema-en-minusculas-con-guiones>
```

- Usa `fix/` si corriges algo ya integrado y `hotfix/` (desde `main`) si es urgente y ya está publicado.
- Una rama por cada cosa. Si la tarea crece, ábrela en otra rama.
- Antes de crear la rama, comprueba que no hay cambios sin guardar (`git status`). Si los hay, pregunta al usuario qué hacer con ellos.

## 2. Durante el trabajo

- Commits pequeños, en español e imperativo: `Añade calendario de noviembre`, `Corrige CTA del reel 03`.
- Nunca hagas commit en `main` ni en `Desarrollo`.
- No subas ficheros pesados (PDF o vídeos de `Referencia/`, exportaciones de vídeo). Revisa `git status` antes de `git add`.

## 3. Antes de abrir el PR: checklist de contexto

- [ ] ¿Cambia algún dato del negocio? → actualiza `docs/cliente/brief.md`.
- [ ] ¿Se ha tomado una decisión? → añade una fila a `docs/decisiones.md`.
- [ ] ¿Cambia la estructura, una convención o se cierra un pendiente? → actualiza `CLAUDE.md`.
- [ ] ¿Has creado o cambiado una skill? → actualiza `SKILLS.md`.
- [ ] ¿Aparece la marca antigua en algo nuevo? → pasa la skill `revision-marca`.

## 4. Abrir el PR

```bash
git push -u origin <rama>
gh pr create --base Desarrollo --title "<Título en español>" --body "<qué cambia y por qué>"
```

- Base: `Desarrollo`, salvo en `release/*` y `hotfix/*`, que van contra `main`.
- Lo revisa **otro miembro** del equipo (Alejandro, Juan o Nico). No te apruebes tus propios PR.
- Pide confirmación al usuario antes de hacer push o abrir el PR.

## 5. Entregas (release)

```bash
git checkout Desarrollo && git pull
git checkout -b release/<AAAA-MM-DD-o-version>
# últimos retoques; después, PR contra main
```

Cuando se fusione en `main`, fusiona también `main` en `Desarrollo` para que no se separen.
