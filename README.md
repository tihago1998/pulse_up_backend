# PulseUp Backend

API REST de PulseUp, aplicación móvil de entrenamiento con plan semanal. Proyecto académico SENA,
Tecnología en Análisis y Desarrollo de Software (ADSO), Ficha 3223873.

> Documentación del proyecto (acta, interesados, requisitos, historias de usuario y diagramas): [docs/README.md](docs/README.md).

> El cliente móvil Android está en el repositorio `pulseup_adroid_studio`.

## Problema y solución

La app necesita guardar y proteger los datos de cada persona, y controlar qué
puede hacer cada rol. Este backend ofrece una API REST con autenticación por
token y permisos por rol, validados siempre en el servidor.

## Características

- Registro e inicio de sesión con JWT.
- Roles: Administrador, Usuario y SuperAdministrador.
- Administración de usuarios: listar, cambiar rol, eliminar y estadísticas.
- Perfil: editar datos y cambiar contraseña.
- Catálogo de 150 ejercicios de gimnasio, casa y calistenia, con 2 fotos (posición inicial y final),
  pasos, respiración, errores comunes y variantes en español; rutinas plantilla y propias.
- Plan semanal con regla de descanso muscular de 48 h, rutina del día y calendario con racha.
- Perfil físico (fecha de nacimiento, sexo, peso, estatura y nivel), base para recomendar cargas.

## Estado de los módulos

| Módulo                                    | Estado       |
| ----------------------------------------- | ------------ |
| Autenticación (registro, login, JWT)      | Implementado |
| Roles y administración de usuarios        | Implementado |
| Perfil (editar datos, cambiar contraseña) | Implementado |
| Catálogo de ejercicios y rutinas          | Implementado |
| Plan semanal, rutina del día y calendario | Implementado |
| Perfil físico                             | Implementado |
| Progreso detallado (series y cargas)      | Pendiente    |
| Notificación de rutinas incumplidas       | Pendiente    |
| Alimentación                              | Pendiente    |
| Sueño                                     | Pendiente    |

### Endpoints de ejercicio (requieren token)

| Método | Ruta                          | Descripción                                          |
| ------ | ----------------------------- | ---------------------------------------------------- |
| GET    | `/api/ejercicios/`            | Catálogo. Filtros: `musculo`, `equipo`, `nivel`, `ambiente`, `q`; paginación: `limit`, `offset` |
| GET    | `/api/ejercicios/filtros`     | Valores disponibles para los filtros (músculos, equipos, niveles, ambientes) |
| GET    | `/api/ejercicios/creditos`    | Fuentes, licencias y atribuciones de las fotos       |
| GET    | `/api/ejercicios/<id>`        | Detalle: pasos, respiración, errores, variantes, fotos y recomendación |
| GET    | `/api/ejercicios/<id>/recomendacion` | Solo la recomendación (para armar rutinas)    |
| GET    | `/api/rutinas/`               | Plantillas + rutinas propias. Filtros: `objetivo`, `nivel` |
| GET    | `/api/rutinas/<id>`           | Rutina con sus ejercicios en orden                   |
| POST   | `/api/rutinas/`               | Crear rutina propia (cada ejercicio admite `peso_kg` y `unidad` opcionales) |
| DELETE | `/api/rutinas/<id>`           | Eliminar una rutina propia (las plantillas no)       |

El catálogo (150 ejercicios) y las 7 rutinas plantilla se cargan solos al
arrancar, sin duplicarse (`pulseup/seeds/`). Una rutina que está en el plan
semanal no se puede eliminar (409): primero hay que quitarla del plan.

**Peso y unidad de cada ejercicio de una rutina.** `rutina_ejercicio` tiene dos columnas
opcionales: `peso_kg` (número de 0 a 500 o `null`) y `unidad` (`repeticiones` por defecto,
`segundos` o `minutos`). Con `segundos` o `minutos`, el campo de texto `repeticiones` guarda
la **duración** y se interpreta según `unidad`: `{"repeticiones": "30", "unidad": "segundos"}`
es una plancha de 30 s. Los clientes que no envían estos campos siguen funcionando igual y
el detalle de la rutina los devuelve siempre. Cada rutina trae además `origen`: `"plan"` si
la creó el plan semanal al agregar ejercicios a un día, `null` si la creó el usuario.

**Listado.** Siempre responde `{"ejercicios": [...], "total": n}`. Sin `limit` ni `offset`
devuelve todos los ejercicios, como antes (así no se rompe la app actual). Con `limit`,
`offset` o `formato=paginado` pagina (`limit` por defecto 20, máximo 100) y añade `items`
(la misma lista), `limit` y `offset`. Cada ejercicio trae, además de los campos de siempre,
`musculo_principal`, `ambientes` (`gimnasio`, `casa`, `calistenia`), `mecanica` e
`imagen_miniatura` (foto de la posición inicial o `null`).

**Detalle.** Añade `pasos`, `respiracion`, `errores_comunes`, `variante_facil`,
`variante_dificil`, `descanso_seg`, `imagenes` (`[{"orden": 0, "url": ...}, {"orden": 1, ...}]`),
`recomendacion` y `recomendacion_motivo` (ver la sección siguiente).
Las `url` de las fotos son relativas al servidor (`/static/ejercicios/...`).

### Recomendación personalizada

El detalle (y `GET /api/ejercicios/<id>/recomendacion`) devuelve, según el nivel del perfil físico:

```json
{"nivel": "intermedio", "unidad": "repeticiones", "reps_min": 6, "reps_max": 12,
 "series_min": 3, "series_max": 4, "descanso_seg": 150, "rir": "2-3", "dias_semana": null,
 "rpe": null, "peso_kg": 72.5, "nota": null,
 "aviso": "Es una guía general y no reemplaza a un entrenador ni a un médico."}
```

- `unidad` es `repeticiones`, `segundos` (isométricos, como la plancha) o `minutos` (cardio,
  con `dias_semana` y `rpe`). Sin perfil físico: `recomendacion: null` y
  `recomendacion_motivo: "Completa tu perfil físico para ver la recomendación"`.
- Las reglas dependen de `tipo_recomendacion` del ejercicio (`carga_compuesto`,
  `carga_aislamiento`, `carga_brazos`, `peso_corporal`, `isometrico`, `abdomen`, `cardio`) y
  del nivel. Están en `pulseup/seeds/recomendaciones_reglas.json`: se editan ahí y se aplican
  al reiniciar, sin tocar código. Dominadas tiene sus propias series y repeticiones
  (`recomendacion_override` en `catalogo_seleccion.json`).
- **Peso** (`peso_kg`): solo para los 7 ejercicios que son exactamente un levantamiento de
  referencia (`referencia_fuerza`: press de banca, sentadilla y press militar con barra, peso
  muerto convencional, remo con barra, jalón al pecho y prensa). El peso muerto rumano no la
  tiene: con la proporción del convencional daba un peso demasiado alto. Se calcula así:
  1RM = proporción × peso corporal (máximo 113 kg); peso = 1RM / (1 + reps/30) (Epley);
  × 0.80 si tiene menos de 18 años y × 0.85 si tiene más de 50; redondeado hacia abajo a
  múltiplos de 2.5 kg, mínimo 2.5 kg.
- **Repeticiones para Epley = punto medio del rango + 2.** Epley da el peso máximo con el que
  se llega justo a esas repeticiones; sumar 2 deja unas 2 repeticiones en reserva (RIR ~2),
  como pide la guía. Ejemplo: intermedio 6–12 → 9 + 2 = 11; hombre de 80 kg, press de banca:
  1RM 100 kg → 100 / (1 + 11/30) = 73.2 → 72.5 kg.
- **Niveles de la guía.** Las proporciones de fuerza tienen 4 niveles (Beginner, Novice,
  Intermediate, Advanced) y la app 3: principiante = promedio de Beginner y Novice,
  intermedio = Intermediate y avanzado = Advanced. La prensa trae directamente los 3 niveles
  y no distingue sexo. Si el sexo es `no_indica` se usa la columna de mujer (la más conservadora).
- En el resto de ejercicios con carga `peso_kg` es `null` y la nota explica cómo elegir el peso;
  bíceps y tríceps tienen su propia nota. Peso corporal, abdomen, isométricos y cardio no llevan
  peso.

### Catálogo ampliado y fotos

La selección curada está en `pulseup/seeds/catalogo_seleccion.json`: 150 ejercicios con su
`id_externo` de [free-exercise-db](https://github.com/yuhonas/free-exercise-db) y textos
redactados en español. Al arrancar se aplica como upsert: los ejercicios que ya existían se
actualizan sin cambiar su id, nombre ni grupo muscular (las rutinas y el plan dependen de
ellos) y los nuevos se crean.

Las fotos no se guardan en el repositorio. Para descargarlas (unos 18 MB) y registrarlas:

```bash
python -m tools.importar_catalogo              # base de datos de PULSEUP_DB_NAME o pulseup.db
python -m tools.importar_catalogo --verificar  # además comprueba los ids contra el dataset
python -m tools.importar_catalogo --forzar     # vuelve a descargar las que ya están
```

Quedan en `pulseup/static/ejercicios/<id_externo>/0.jpg` y `1.jpg` (en `.gitignore`) y Flask
las sirve en `/static/ejercicios/...`. Es seguro repetirlo: no duplica filas ni vuelve a bajar
lo que ya existe. Si una foto falla se anota en `pulseup/static/ejercicios/errores_importacion.log`
y sigue con las demás. Licencia: el repositorio free-exercise-db es Unlicense, pero el origen de
las fotos no está documentado; la fuente y la licencia se guardan por foto en `ejercicio_imagen`
para poder cambiar de proveedor sin tocar el resto del catálogo.

### Endpoints del plan semanal y calendario (requieren token)

Los días van de `1` (lunes) a `7` (domingo). Un día sin rutina es día de descanso.

| Método | Ruta                          | Descripción                                                    |
| ------ | ----------------------------- | -------------------------------------------------------------- |
| GET    | `/api/plan/`                  | Los 7 días con su rutina, grupos musculares y `ejercicios` (`null` = descanso) |
| PUT    | `/api/plan/<dia>`             | Asigna o reemplaza la rutina del día. Cuerpo: `{"id_rutina": N}` → `{"dia", "avisos"}` |
| GET    | `/api/plan/previsualizar`     | Avisos de 48 h de poner `ejercicio_id=N` o `rutina_id=N` en cada uno de los 7 días |
| POST   | `/api/plan/<dia>/ejercicios`  | Agrega un ejercicio del catálogo al día (201) → `{"item", "rutina_copiada", "avisos"}` |
| PUT    | `/api/plan/<dia>/ejercicios/<item_id>` | Edita `series`, `repeticiones`, `peso_kg`, `unidad` o `descanso_seg` |
| DELETE | `/api/plan/<dia>/ejercicios/<item_id>` | Quita el ejercicio; si el día queda vacío pasa a descanso |
| DELETE | `/api/plan/<dia>`             | Deja el día en descanso                                        |
| POST   | `/api/plan/validar`           | Dice si se podría asignar, sin guardar. Cuerpo: `{"dia_semana": N, "id_rutina": N}` → `{"valido", "conflictos"}` |
| POST   | `/api/plan/completar`         | Marca como cumplida la rutina de **hoy** (201)                 |
| GET    | `/api/plan/incumplidos`       | Días pasados con rutina y sin cumplir. Filtro: `desde=YYYY-MM-DD` (por defecto ayer) |
| GET    | `/api/calendario/`            | Mes con el estado de cada día y la racha. Filtro: `mes=YYYY-MM` (por defecto el actual) |

**Regla de descanso muscular (48 h): avisa, no bloquea.** Entre dos días que trabajan
el mismo grupo debería haber al menos `PULSEUP_DESCANSO_MUSCULAR_HORAS / 24` días
(2 por defecto). El usuario **siempre puede guardar**: `PUT /api/plan/<dia>`, `POST
/api/plan/<dia>/ejercicios` y `/previsualizar` devuelven los choques en `avisos` y
`/validar` los sigue informando en `conflictos`:

- Cuenta el grupo **principal** de cada ejercicio; los músculos secundarios no bloquean.
- Abdomen, pantorrillas, cardio y cuerpo completo están exentos.
- La semana es circular: domingo y lunes son consecutivos.
- Al reemplazar la rutina de un día, la rutina anterior de ese día no cuenta.
- La regla mide la distancia **entre** días: varios ejercicios del mismo músculo el
  mismo día están permitidos y no avisan.
- Cada aviso: `{"tipo": "descanso_48h", "musculo": "pecho", "dia_conflicto": 1,
  "mensaje": "El lunes ya trabajas pecho: tu pecho necesita 48 horas de descanso"}`.
  `dia_conflicto` es el día del plan que ya trabaja ese músculo.

**Ejercicios del catálogo en un día del plan.** Detrás sigue el modelo plan → rutina →
ejercicios: cada día apunta a una rutina.

- **Agregar** (`POST /api/plan/<dia>/ejercicios`, cuerpo `{"ejercicio_id", "series"?,
  "repeticiones"?, "peso_kg"?, "unidad"?, "descanso_seg"?}`):
  - Día sin rutina: se crea una rutina del usuario con `origen = "plan"` y nombre
    `"<Día> · <músculo principal>"` (por ejemplo `"Lunes · pecho"`), y se asigna con el
    mismo servicio que `PUT /api/plan/<dia>`, así queda en el historial del plan.
  - Día con una rutina propia de origen `plan` que no está en otros días: se agrega a esa.
  - Día con una plantilla, una rutina creada por el usuario en su pantalla de rutinas o
    una rutina asignada también a otros días: se crea una **copia** solo para este día
    (`"<Día> · <nombre>"`), se reasigna el día a la copia y la respuesta trae
    `rutina_copiada: true`. Los demás días y la rutina original no cambian.
  - Lo que no se envía sale de la recomendación personalizada: `series = series_max`,
    `repeticiones` = punto medio del rango (con `segundos` o `minutos`, redondeado al
    múltiplo de 5 más cercano: 30–45 s → 40, 30–40 min → 35), `unidad`, `descanso_seg`
    (0 en cardio) y `peso_kg`. Sin recomendación (sin perfil físico): 3 series, 10 repeticiones, 60 s y
    peso `null`.
  - Si el ejercicio ya está en ese día: 409 `"Ese ejercicio ya está en este día"`.
- **Editar** y **quitar** usan el `item_id` que devuelve `GET /api/plan/` y aplican la misma
  copia si la rutina está compartida. Validaciones: `series` 1–10, `peso_kg` 0–500 o `null`,
  `descanso_seg` 0–600 y `unidad` en `repeticiones | segundos | minutos` (400 con mensaje).
- Al quitar el último ejercicio de una rutina de origen `plan`, la rutina se elimina y el día
  queda en descanso (por el mismo servicio que `DELETE /api/plan/<dia>`). Si una sesión
  cumplida usa esa rutina (por ejemplo la de hoy), la rutina se conserva para que el
  calendario no pierda su nombre.
- Día fuera de 1–7, día sin rutina o `item_id` que no es de ese día: 404. Solo se tocan
  rutinas del usuario autenticado. No se puede mover un ejercicio entre días.
- **Hoy ya cumplido:** el cambio se guarda, pero la sesión de hoy no se toca: el día sigue
  `cumplido` en el calendario, la racha no cambia y `/completar` sigue respondiendo 409.

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
los descansos no la cortan, un incumplido sí.

**Historial del plan.** Cada día del plan guarda desde cuándo y hasta cuándo tuvo
cada rutina (`plan_historial`). El calendario, la racha y `/incumplidos` evalúan
cada fecha con la rutina que estaba planificada **en esa fecha**: cambiar o quitar
un día del plan aplica desde hoy y no borra los incumplidos que ya ocurrieron.
Cambios hechos y deshechos el mismo día no dejan rastro.

### Endpoints del perfil físico (requieren token)

Cada usuario tiene como máximo un perfil físico. Es la base para recomendar
repeticiones y pesos según el nivel.

| Método | Ruta                  | Descripción                                                        |
| ------ | --------------------- | ------------------------------------------------------------------ |
| GET    | `/api/perfil-fisico/` | `{"perfil": null}` si aún no lo llenó; si existe, `{"perfil": {...}}` |
| PUT    | `/api/perfil-fisico/` | Crea o reemplaza el perfil. Responde `{"message": "Perfil guardado", "perfil": {...}}` |
| DELETE | `/api/perfil-fisico/` | Borra el perfil (200 aunque no existiera)                          |

Cuerpo del `PUT`:

```json
{"fecha_nacimiento": "1998-03-10", "sexo": "hombre", "peso_kg": 72.5, "estatura_cm": 175, "nivel": "intermedio"}
```

El `perfil` que devuelven `GET` y `PUT` trae `fecha_nacimiento`, `edad`, `sexo`,
`peso_kg`, `estatura_cm`, `nivel` y `actualizado_en` (ISO 8601 con zona, por ejemplo
`2026-11-16T18:30:00-05:00`). La `edad` no se guarda: se calcula en cada respuesta con la
fecha de hoy en Colombia (`PULSEUP_TZ`).

**Validaciones** (400 con `{"error": "..."}`):

| Campo              | Regla                                                                         |
| ------------------ | ----------------------------------------------------------------------------- |
| `fecha_nacimiento` | Obligatoria, `YYYY-MM-DD`, no futura; edad entre 14 y 100 años               |
| `peso_kg`          | Obligatorio, número (no texto ni booleano) entre 30 y 300; se guarda con 1 decimal |
| `estatura_cm`      | Obligatoria, número (no texto ni booleano) entre 100 y 250; se guarda con 1 decimal |
| `nivel`            | Obligatorio: `principiante`, `intermedio` o `avanzado`                        |
| `sexo`             | Opcional: `hombre`, `mujer` o `no_indica` (por defecto `no_indica`)           |

Si faltan campos obligatorios el mensaje los nombra todos
(`"Faltan campos obligatorios: peso_kg, nivel"`). Los campos desconocidos se ignoran.
Los rangos están en `pulseup/core/dominio.py`. Al eliminar un usuario se borra también
su perfil físico.

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

PulseUp es solo para Colombia: todos los usuarios comparten la zona `PULSEUP_TZ`
(`America/Bogota`, UTC-5, sin horario de verano). Con ella se decide qué día es "hoy" en el
plan semanal y el calendario, sin importar la zona horaria del
servidor. Solo el vencimiento de los tokens usa UTC.

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
    ejercicios/        Catálogo de ejercicios con filtros
    rutinas/           Plantillas y rutinas propias
    plan/              Plan semanal, regla de 48 h, rutina del día y calendario
    perfil_fisico/     Perfil físico (edad, peso, estatura y nivel)
    recomendaciones/   Series, repeticiones, descanso y peso recomendados por ejercicio
    <módulo>/          routes.py (HTTP) → service.py (reglas) → repository.py (SQL)
  seeds/               ejercicios.json (base), catalogo_seleccion.json (ampliado), rutinas.json,
                       recomendaciones_reglas.json (reglas y proporciones de fuerza)
  static/ejercicios/   Fotos descargadas por el importador (no se suben al repositorio)
tools/
  importar_catalogo.py Descarga y registra las fotos del catálogo
tests/                 Pruebas del contrato de la API
```

## Autores

- Santiago Varela Peña: desarrollador full stack, líder del proyecto
- Sebastián Navarro López: desarrollador full stack

Aprendices ADSO SENA, Ficha 3223873. Las responsabilidades son compartidas
entre backend y aplicación Android.

## Licencia

MIT. Ver `LICENSE`.
