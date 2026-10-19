# Guía de contribución

## Ramas

- `main`: versión estable y entregable. Solo se integra por Pull Request.
- `dev`: integración del trabajo. Solo se integra por Pull Request.
- `feature/*`: una funcionalidad por rama, sale de `dev` y vuelve a `dev`.
- `fix/*`: corrección no urgente, sale de `dev` y vuelve a `dev`.
- `chore/*`: mantenimiento y archivos del repositorio.
- `release/*`: preparación de una versión, vuelve a `main` y a `dev`.

## Commits

Formato `tipo(scope): descripción` en español, en una línea, empezando con un verbo.

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.

Ejemplo: `feat(profile): agregar edición de perfil`

## Pull Requests

- Se abre hacia `dev`, con la plantilla de la guía: resumen, requisito
  relacionado, tipo de cambio, pruebas, evidencia, riesgos, migraciones
  y checklist.
- Cuando haya otra persona disponible, lo revisa antes del merge.
- Nunca se hace push directo a `main` ni a `dev`.

## Reglas generales

- Cada integrante hace commits con su propio usuario de Git.
- No se suben secretos, archivos `.env` ni bases de datos.
- Cambios pequeños y coherentes: un tema por commit.
