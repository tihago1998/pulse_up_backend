# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
El proyecto sigue [SemVer](https://semver.org/lang/es/).

## [Unreleased]

### Added

- Registro e inicio de sesión con JWT.
- Roles: Administrador, Usuario y SuperAdministrador.
- Administración de usuarios: listar, cambiar rol, eliminar y estadísticas.
- Módulo de perfil: editar datos y cambiar contraseña.
- Catálogo de 48 ejercicios (filtros por músculo, equipo y nivel) y 7 rutinas plantilla.
- Rutinas propias: crear, ver y eliminar.
- Plan semanal (`/api/plan/`): asignar, reemplazar y quitar la rutina de cada día.
- Regla de descanso muscular de 48 h al armar el plan (semana circular, grupos exentos y
  solo grupos principales) y `POST /api/plan/validar` para comprobarla sin guardar.
- `POST /api/plan/completar`: marcar como cumplida la rutina de hoy, sin recuperar días perdidos.
- Calendario mensual (`/api/calendario/`) con estados cumplido, pendiente, incumplido y descanso, y racha.
- `GET /api/plan/incumplidos` con los días recientes sin cumplir (base de la notificación del Sprint 2).
- Variables `PULSEUP_TZ` (zona horaria, `America/Bogota`) y `PULSEUP_DESCANSO_MUSCULAR_HORAS` (`48`).
- Perfil físico (`/api/perfil-fisico/`): ver, guardar (crea o reemplaza) y borrar la fecha de
  nacimiento, sexo, peso, estatura y nivel, con la edad calculada en hora de Colombia y
  validación de rangos. Al eliminar un usuario se borra también su perfil físico.
- Catálogo ampliado a 150 ejercicios de gimnasio, casa y calistenia
  (`pulseup/seeds/catalogo_seleccion.json`), con pasos, respiración, errores comunes,
  variantes y descanso en español. Los 48 existentes se actualizan sin cambiar su id.
- Fotos de posición inicial y final de free-exercise-db: tabla `ejercicio_imagen` e importador
  idempotente `python -m tools.importar_catalogo`; Flask las sirve en `/static/ejercicios/`.
- `GET /api/ejercicios/`: filtro `ambiente`, `total` y paginación opcional (`limit`, `offset`,
  `items`) sin cambiar la respuesta de siempre. El detalle añade pasos, fotos,
  `recomendacion` y `recomendacion_motivo`.
- `GET /api/ejercicios/creditos` con fuentes, licencias y atribuciones de las fotos, y
  `ambientes` en `GET /api/ejercicios/filtros`.
- Recomendación personalizada por ejercicio según el nivel y el perfil físico: series,
  repeticiones (o segundos / minutos), descanso, RIR, días y RPE para cardio, y peso estimado
  (Epley, ajuste por edad, tope de 113 kg, redondeo a 2.5 kg) en los 8 ejercicios con
  `referencia_fuerza`. Reglas y proporciones editables en
  `pulseup/seeds/recomendaciones_reglas.json` (tablas `recomendacion_regla` y
  `referencia_fuerza_ratio`). Nuevo `GET /api/ejercicios/<id>/recomendacion`.

### Changed

- Reorganización por capas (routes → service → repository) sin cambiar los endpoints.
- `app.py` expone `app = create_app()`; la base de datos se inicializa al arrancar.
- Al eliminar un usuario también se eliminan su plan semanal y sus sesiones.
- `DELETE /api/rutinas/<id>` responde 409 si la rutina está en el plan semanal.
- Nueva dependencia `tzdata` para que las zonas horarias funcionen en Windows.

### Removed

- Módulo de hábitos (TK001): ya no existen `/api/habitos/` (listar y registrar),
  `/api/habitos/<id>/completado` ni `/api/habitos/resumen`; ahora responden 404. La app
  Android dejó de usarlos. La tabla `habito` se conserva sin uso, con sus datos, y podrá
  eliminarse en una migración futura. Al eliminar un usuario se siguen borrando sus filas.

### Fixed

- Historial del plan semanal (`plan_historial`): el calendario, la racha y los incumplidos
  usan la rutina vigente en cada fecha. Quitar o cambiar un día ya no convierte en
  descanso los incumplidos anteriores. Los planes existentes se migran solos al arrancar.

### Security

- La clave de los tokens JWT ya no está escrita en el código: se lee de la variable de entorno `PULSEUP_SECRET_KEY`.
