# PulseUp Backend

API REST de PulseUp, app móvil de hábitos saludables. Proyecto académico SENA,
Tecnología en Análisis y Desarrollo de Software (ADSO), Ficha 3223873.

> El cliente móvil Android está en el repositorio `pulseup_adroid_studio`.

## Problema y solución

La app necesita guardar y proteger los datos de cada persona, y controlar qué
puede hacer cada rol. Este backend ofrece una API REST con autenticación por
token y permisos por rol, validados siempre en el servidor.

## Características

- Registro e inicio de sesión con JWT.
- Roles: Administrador, Usuario y SuperAdministrador.
- Administración de usuarios: listar, cambiar rol, eliminar y estadísticas.
- Hábitos por usuario.
- Perfil: editar datos y cambiar contraseña.
- Catálogo de ejercicios y rutinas (plantillas y propias).
- Plan semanal con regla de descanso muscular de 48 h, rutina del día y calendario con racha.

## Estado de los módulos

| Módulo                                    | Estado       |
| ----------------------------------------- | ------------ |
| Autenticación (registro, login, JWT)      | Implementado |
| Roles y administración de usuarios        | Implementado |
| Perfil (editar datos, cambiar contraseña) | Implementado |
| Hábitos                                   | Implementado |
| Catálogo de ejercicios y rutinas          | Implementado |
| Plan semanal, rutina del día y calendario | Implementado |
| Progreso detallado (series y cargas)      | Pendiente    |
| Notificación de rutinas incumplidas       | Pendiente    |
| Alimentación                              | Pendiente    |
| Sueño                                     | Pendiente    |

### Endpoints de ejercicio (requieren token)

| Método | Ruta                          | Descripción                                          |
| ------ | ----------------------------- | ---------------------------------------------------- |
| GET    | `/api/ejercicios/`            | Catálogo. Filtros: `musculo`, `equipo`, `nivel`, `q` |
| GET    | `/api/ejercicios/filtros`     | Valores disponibles para los filtros                 |
| GET    | `/api/ejercicios/<id>`        | Detalle con instrucciones                            |
| GET    | `/api/rutinas/`               | Plantillas + rutinas propias. Filtros: `objetivo`, `nivel` |
| GET    | `/api/rutinas/<id>`           | Rutina con sus ejercicios en orden                   |
| POST   | `/api/rutinas/`               | Crear rutina propia                                  |
| DELETE | `/api/rutinas/<id>`           | Eliminar una rutina propia (las plantillas no)       |

El catálogo (48 ejercicios) y las 7 rutinas plantilla se cargan solos al
arrancar, sin duplicarse (`pulseup/seeds/`). Una rutina que está en el plan
semanal no se puede eliminar (409): primero hay que quitarla del plan.

### Endpoints del plan semanal y calendario (requieren token)

Los días van de `1` (lunes) a `7` (domingo). Un día sin rutina es día de descanso.

| Método | Ruta                          | Descripción                                                    |
| ------ | ----------------------------- | -------------------------------------------------------------- |
| GET    | `/api/plan/`                  | Los 7 días con su rutina y grupos musculares (`null` = descanso) |
| PUT    | `/api/plan/<dia>`             | Asigna o reemplaza la rutina del día. Cuerpo: `{"id_rutina": N}` |
| DELETE | `/api/plan/<dia>`             | Deja el día en descanso                                        |
| POST   | `/api/plan/validar`           | Dice si se podría asignar, sin guardar. Cuerpo: `{"dia_semana": N, "id_rutina": N}` → `{"valido", "conflictos"}` |
| POST   | `/api/plan/completar`         | Marca como cumplida la rutina de **hoy** (201)                 |
| GET    | `/api/plan/incumplidos`       | Días pasados con rutina y sin cumplir. Filtro: `desde=YYYY-MM-DD` (por defecto ayer) |
| GET    | `/api/calendario/`            | Mes con el estado de cada día y la racha. Filtro: `mes=YYYY-MM` (por defecto el actual) |

**Regla de descanso muscular (48 h).** Un grupo muscular no puede entrenarse dos
días seguidos: entre dos días que trabajan el mismo grupo debe haber al menos
`PULSEUP_DESCANSO_MUSCULAR_HORAS / 24` días (2 por defecto). Se aplica al asignar
(`PUT`) y en `/validar`:

- Cuenta el grupo **principal** de cada ejercicio; los músculos secundarios no bloquean.
- Abdomen, pantorrillas, cardio y cuerpo completo están exentos.
- La semana es circular: domingo y lunes son consecutivos.
- Al reemplazar la rutina de un día, la rutina anterior de ese día no cuenta.
- Si hay conflicto responde 409:
  `{"error": "Pecho ya se entrena el lunes; necesita 48 h de descanso antes de volver a trabajarlo", "conflictos": [{"grupo": "pecho", "dia_semana": 1, "nombre_dia": "lunes"}]}`

**Rutina del día.** Solo se puede marcar la rutina planificada para hoy. En día de
descanso responde 400, si ya está marcada 409, y no se aceptan otras fechas ni otra
rutina: el día perdido no se recupera. "Hoy" se calcula en la zona `PULSEUP_TZ`.

**Calendario.** Cada día trae `estado`:

| Estado       | Significado                                                       |
| ------------ | ----------------------------------------------------------------- |
| `cumplido`   | Se marcó la rutina ese día (se muestra con fuego)                 |
| `pendiente`  | Hoy o un día futuro con rutina planificada                        |
| `incumplido` | Día pasado con rutina planificada y sin marcar                    |
| `descanso`   | Sin rutina, o anterior a la fecha en que se planificó ese día     |

La `racha` (`actual` y `mejor`) cuenta los días planificados cumplidos seguidos;
los descansos no la cortan, un incumplido sí. El calendario se calcula con el plan
**actual**: cambiar el plan cambia cómo se ven los días pasados sin sesión.

## Tecnologías

Python, Flask y SQLite, con arquitectura por capas (routes → service → repository). Las dependencias y sus versiones
están en `requirements.txt`.

## Requisitos previos

- Python 3 y pip
- Git

## Instalación

```bash
git clone https://github.com/tihago1998/pulse_up_backend.git
cd pulse_up_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

La aplicación lee sus ajustes de variables de entorno. Copia el archivo de ejemplo y define tu propia clave:

```bash
copy .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Pega la clave generada en `PULSEUP_SECRET_KEY` dentro de `.env`. Ese archivo no se sube al repositorio. Si falta la clave, la aplicación no arranca y muestra un mensaje indicándolo.

| Variable             | Obligatoria | Descripción                                            |
| -------------------- | ----------- | ------------------------------------------------------ |
| `PULSEUP_SECRET_KEY` | Sí          | Clave para firmar los tokens JWT                       |
| `PULSEUP_DB_NAME`    | No          | Archivo de la base de datos (por defecto `pulseup.db`) |
| `PULSEUP_HOST`       | No          | Dirección de escucha (por defecto `0.0.0.0`)           |
| `PULSEUP_PORT`       | No          | Puerto (por defecto `5050`)                            |
| `PULSEUP_DEBUG`      | No          | Modo de depuración (por defecto `true`)                |
| `PULSEUP_TZ`         | No          | Zona horaria para decidir qué día es hoy (por defecto `America/Bogota`) |
| `PULSEUP_DESCANSO_MUSCULAR_HORAS` | No | Horas mínimas entre dos días con el mismo grupo muscular (por defecto `48`) |

## Ejecución

```bash
python app.py
```

El servidor queda en el puerto 5050. La base de datos SQLite se crea sola en el
primer arranque, con los roles iniciales.

## Pruebas

```
pip install -r requirements-dev.txt
python -m pytest -q tests
```

Las pruebas fijan la fecha "hoy" con el fixture `fijar_hoy` (sustituye
`pulseup.core.tiempo.hoy`), así no dependen del reloj real.

## Estructura

```
app.py                 Punto de entrada (app = create_app())
config.py              Configuración desde variables de entorno
pulseup/
  __init__.py          Fábrica de la app y creación de tablas
  core/                Piezas compartidas: BD, seguridad, auth, errores, roles, tiempo (hoy)
  modules/
    auth/              Registro e inicio de sesión
    usuarios/          Usuarios, perfil y roles
    habitos/           Hábitos y resumen del calendario
    ejercicios/        Catálogo de ejercicios con filtros
    rutinas/           Plantillas y rutinas propias
    plan/              Plan semanal, regla de 48 h, rutina del día y calendario
    <módulo>/          routes.py (HTTP) → service.py (reglas) → repository.py (SQL)
tests/                 Pruebas del contrato de la API
```

## Autores

- Santiago Varela Peña: desarrollador full stack, líder del proyecto
- Sebastián Navarro López: desarrollador full stack

Aprendices ADSO SENA, Ficha 3223873. Las responsabilidades son compartidas
entre backend y aplicación Android.

## Licencia

MIT. Ver `LICENSE`.
