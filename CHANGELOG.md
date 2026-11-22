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

### Changed

- Reorganización por capas (routes → service → repository) sin cambiar los endpoints.
- `app.py` expone `app = create_app()`; la base de datos se inicializa al arrancar.
- Al eliminar un usuario también se eliminan sus hábitos.

### Security

- La clave de los tokens JWT ya no está escrita en el código: se lee de la variable de entorno `PULSEUP_SECRET_KEY`.
