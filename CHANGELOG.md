# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
El proyecto sigue [SemVer](https://semver.org/lang/es/).

## [Unreleased]

### Added

- Registro e inicio de sesión con JWT.
- Roles: Administrador, Usuario y SuperAdministrador.
- Administración de usuarios: listar, cambiar rol, eliminar y estadísticas.
- Módulo de hábitos: crear y listar por usuario.
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

### Changed

- Reorganización por capas (routes → service → repository) sin cambiar los endpoints.
- `app.py` expone `app = create_app()`; la base de datos se inicializa al arrancar.
- Al eliminar un usuario también se eliminan sus hábitos, su plan semanal y sus sesiones.
- `DELETE /api/rutinas/<id>` responde 409 si la rutina está en el plan semanal.
- Nueva dependencia `tzdata` para que las zonas horarias funcionen en Windows.

### Security

- La clave de los tokens JWT ya no está escrita en el código: se lee de la variable de entorno `PULSEUP_SECRET_KEY`.
