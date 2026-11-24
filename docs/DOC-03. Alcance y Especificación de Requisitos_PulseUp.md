# DOC-03. Alcance y especificación de requisitos — PulseUp

**Proyecto:** PulseUp — aplicación Android de entrenamiento con plan semanal  
**Autores:** Santiago Varela Peña y Sebastián Navarro López  
**Programa:** Tecnología en Análisis y Desarrollo de Software, SENA — Ficha 3223873  
**Versión:** 2.0 — 24 de noviembre de 2026 (alineada con la implementación; auditoría del backend y de la app)

---

## Contenido

1. [Introducción](#1-introduccion)
2. [Alcance](#2-alcance)
3. [Requisitos funcionales](#3-requisitos-funcionales)
4. [Requisitos no funcionales](#4-requisitos-no-funcionales)
5. [Reglas de negocio](#5-reglas-de-negocio)
6. [Historias de usuario y estado](#6-historias-de-usuario-y-estado)
7. [Trazabilidad](#7-trazabilidad)
8. [Limitaciones conocidas](#8-limitaciones-conocidas)
9. [Fuera del alcance](#9-fuera-del-alcance)
10. [Referencias](#10-referencias)

---

## 1. Introducción

PulseUp es una aplicación móvil para entrenar con orden: el usuario explora un catálogo de ejercicios con fotos, recibe una recomendación de series, repeticiones y peso según su nivel y su perfil físico, arma su plan semanal y marca cada día cumplido en un calendario con racha. Este documento especifica lo que el sistema **hace hoy** y lo que está **planeado**, de modo que cada afirmación pueda comprobarse en la aplicación y en la API.

Cada historia de usuario lleva un **estado** (Implementada, Parcial, Planeada o Retirada) obtenido de una auditoría de solo lectura del código del backend (Flask y SQLite) y de la app Android (Kotlin y Jetpack Compose).

## 2. Alcance

**Dentro del alcance:** cuentas y roles; catálogo de 150 ejercicios con imágenes; perfil físico y recomendación personalizada; rutinas propias y plantillas; plan semanal con aviso de descanso muscular; calendario, racha y marcado diario; mensajes motivadores.

**Planeado:** notificaciones, sesión guiada con temporizador, resumen semanal completo, administración del catálogo desde la app y endurecimiento de seguridad.

## 3. Requisitos funcionales

| ID | Requisito | Historias | Estado |
|---|---|---|---|
| RF-001 | Registro, inicio y cierre de sesión con correo y contraseña; edición del perfil y de la contraseña. | HU001–HU003 | Implementado (con limitaciones) |
| RF-002 | Roles Usuario, Administrador y SuperAdministrador con permisos diferenciados; administración de usuarios. | HU004–HU006 | Implementado (con limitaciones) |
| RF-003 | Catálogo de 150 ejercicios con fotos, búsqueda y filtros por lugar de entrenamiento, músculo, equipo y nivel. | HU009, HU010, HU031, HU032 | Implementado |
| RF-015 | Créditos de las imágenes y vista del inicio con la semana y la tarjeta «Hoy toca». | HU036, HU037 | Implementado |
| RF-004 | Perfil físico del usuario (peso, estatura, fecha de nacimiento, sexo y nivel). | HU029 | Implementado |
| RF-005 | Recomendación personalizada de series, repeticiones, descanso y peso según nivel y perfil físico. | HU030 | Implementado |
| RF-006 | Creación, consulta y eliminación de rutinas propias y consulta de plantillas del sistema. | HU011–HU013, HU035 | Implementado (HU012 parcial) |
| RF-007 | Plan semanal: asignar rutina o descanso a cada día, agregar, editar y quitar ejercicios de un día. | HU016, HU033, HU034 | Implementado |
| RF-008 | Aviso de descanso muscular de 48 horas al armar el plan, sin bloquear al usuario. | HU017 | Implementado |
| RF-009 | Marcar la rutina del día, calendario con cuatro estados y racha de días cumplidos. | HU018–HU020 | Implementado (HU018 y HU019 parciales) |
| RF-010 | Resumen semanal de cumplimiento. | HU021 | Parcial |
| RF-011 | Mensajes y frases motivadoras. | HU026–HU028 | Parcial |
| RF-012 | Notificaciones de recordatorio y de día incumplido, configurables. | HU023–HU025 | Planeado (Sprint 2) |
| RF-013 | Sesión guiada de entrenamiento con temporizador y registro de series. | HU015 | Planeado (Sprint 2) |
| RF-014 | Administración del catálogo y de las plantillas desde la aplicación. | HU007, HU008 | Planeado (futuro) |

## 4. Requisitos no funcionales

| ID | Categoría | Descripción |
|---|---|---|
| RNF-001 | Seguridad | Las contraseñas se almacenan cifradas; la API usa tokens con expiración de 24 horas y control de acceso por rol (respuesta 403). Las limitaciones conocidas se listan en la sección 8. |
| RNF-002 | Rendimiento y livianidad | La aplicación debe ser liviana y responder con fluidez en un teléfono Android de gama media. El catálogo se entrega paginado y las imágenes se cargan de forma diferida con caché. |
| RNF-003 | Usabilidad | Interfaz en español con mensajes de error claros; las credenciales incorrectas no revelan cuál dato falló. Tiempo de espera de red de 30 s para conectar y 30 s para leer. |
| RNF-004 | Compatibilidad | Aplicación Android nativa (Kotlin y Jetpack Compose) que consume una API REST propia. |
| RNF-005 | Mantenibilidad | Backend en capas (rutas, servicio, repositorio); cambios de base de datos aditivos y semillas idempotentes; 340 pruebas automáticas en el backend y 174 en la app. |
| RNF-006 | Zona horaria | El corte del día se calcula en la zona horaria configurada en el servidor (America/Bogota por defecto). |
| RNF-007 | Licenciamiento de contenido | Las imágenes del catálogo provienen del repositorio free-exercise-db (licencia Unlicense) y sus créditos se publican en la API y en la documentación. |

## 5. Reglas de negocio

| ID | Regla | Descripción |
|---|---|---|
| RN-01 | Descanso muscular | Se compara el grupo muscular principal del ejercicio con los días vecinos del plan (semana circular). Con el valor por defecto de 48 horas solo chocan días consecutivos. Los músculos secundarios no cuentan. Abdomen, pantorrillas, cardio y cuerpo completo están exentos. Se evalúa sobre la plantilla semanal. Solo se avisa; nunca se bloquea. |
| RN-02 | Marcar cumplimiento | Solo se puede marcar el día de hoy. Un día no marcado pasa a incumplido y no se recupera. Un día ya cumplido no se deshace al editar el plan. |
| RN-03 | Historial | El historial de días pasados protege el pasado: cambiar el plan no altera lo ya ocurrido. |
| RN-04 | Copia por día | Si la rutina de un día es plantilla, propia o está compartida con otros días, al editar o agregar ejercicios se copia solo para ese día y la original no cambia. Si el día no tiene rutina se crea una propia del plan («<Día> · <músculo>»). Asignar una rutina a un día con contenido lo reemplaza, previa confirmación. |
| RN-05 | Límites | Máximo 20 ejercicios por día y por rutina; series entre 1 y 10; descanso entre 0 y 600 segundos; duración de la rutina entre 5 y 240 minutos; peso entre 0 y 500 kg; un ejercicio no se repite en el mismo día. Los cardios tienen descanso 0 y no lo muestran. |
| RN-06 | Recomendación de peso | 1RM estimado = razón por nivel y sexo × peso corporal (con tope de 113 kg); peso sugerido con la fórmula de Epley con repeticiones = punto medio del rango + 2; prensa con razones sin distinción de sexo; ×0,80 si es menor de 18 años y ×0,85 si es mayor de 50; se redondea hacia abajo a 2,5 kg. |
| RN-07 | Duraciones | Las duraciones por defecto de ejercicios por tiempo se redondean a múltiplos de 5 segundos. |
| RN-08 | Días | El día se identifica con un entero de 1 a 7 (lunes = 1). |
| RN-09 | Perfil físico | Edad entre 14 y 100 años calculada desde la fecha de nacimiento, peso entre 30 y 300 kg, estatura entre 100 y 250 cm; sexo opcional; nivel obligatorio. |

## 6. Historias de usuario y estado

**Resumen:** Implementada: 20, Parcial: 10, Planeada: 12, Retirada: 1. Total: 43 (incluye tareas técnicas).

| Estado | Significado |
|---|---|
| Implementada | Funciona en la app y en la API y fue probada. |
| Parcial | Funciona, pero con alguna diferencia respecto al criterio original (se indica en la nota). |
| Planeada | No existe todavía; tiene sprint o fecha prevista. |
| Retirada | Se decidió no hacerla; se conserva por trazabilidad. |

### EP-001 · Registro y acceso

#### HU001 · Registrarme

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 0

- **Como:** Usuario nuevo
- **Quiero:** registrarme con nombre, correo y contraseña
- **Para:** tener mi cuenta personal

**Criterios de aceptación:**

1. El correo no puede estar repetido (error claro)
2. Todos los campos son obligatorios
3. La cuenta nueva queda con el rol Usuario
4. La contraseña se guarda encriptada

> **Nota:** Limitación: el servidor no valida el formato del correo ni la longitud de la contraseña, acepta nombres con solo espacios y distingue mayúsculas en el correo; la app sí exige mínimo 8 caracteres y confirmación de la contraseña (LIM-03). El registro no devuelve token: después hay que iniciar sesión.

#### HU002 · Iniciar y cerrar sesión

**Estado:** Parcial · **Prioridad:** Must · **Puntos:** 3 · **Sprint:** Sprint 0

- **Como:** Usuario registrado
- **Quiero:** iniciar sesión con correo y contraseña y cerrar sesión
- **Para:** acceder a mis datos de forma segura

**Criterios de aceptación:**

1. Las credenciales incorrectas muestran el mismo mensaje sin revelar cuál falló
2. El token de sesión expira a las 24 horas
3. Cerrar sesión borra la sesión del dispositivo

> **Nota:** Parcial: la sesión vive solo en memoria y se pierde al cerrar la app; el servidor no invalida el token al cerrar sesión; ante un 401 las pantallas nuevas avisan «Tu sesión expiró» pero no vuelven solas al inicio de sesión, y las pantallas antiguas muestran «Error (código 401)» (LIM-01, LIM-02). El botón «Ingresar» se deshabilita mientras haya campos vacíos y cerrar sesión pide confirmación.

#### HU003 · Editar mi perfil y contraseña

**Estado:** Implementada · **Prioridad:** Should · **Puntos:** 3 · **Sprint:** Sprint 0

- **Como:** Usuario
- **Quiero:** editar mi nombre y correo y cambiar mi contraseña
- **Para:** mantener mis datos al día

**Criterios de aceptación:**

1. El correo nuevo no puede pertenecer a otro usuario
2. Para cambiar la contraseña se pide la actual
3. Con la contraseña nueva se puede iniciar sesión y con la anterior no

> **Nota:** Limitaciones: cualquier error 400 al cambiar la contraseña se muestra como «La contraseña actual es incorrecta»; la pantalla no pide confirmar la nueva contraseña ni valida su longitud; si falla la carga inicial del perfil los campos quedan vacíos sin aviso.

### EP-002 · Roles y administración

#### HU004 · Permisos por rol

**Estado:** Parcial · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 0

- **Como:** Equipo de desarrollo
- **Quiero:** tres roles (Usuario, Administrador, SuperAdministrador) con permisos distintos
- **Para:** que cada persona solo acceda a lo que le corresponde

**Criterios de aceptación:**

1. Un usuario sin rol de administración recibe 403 en las rutas de administración
2. El rol viaja dentro del token
3. La app muestra la opción «Administrar usuarios» solo a Administrador y SuperAdministrador

> **Nota:** Parcial: la app lee los roles de la respuesta del inicio de sesión, no del token; la ruta de usuarios no está protegida en la navegación (solo se oculta el botón, y el servidor responde 403); los permisos no se refrescan hasta volver a iniciar sesión (LIM-02).

#### HU005 · Ver usuarios y estadísticas

**Estado:** Implementada · **Prioridad:** Should · **Puntos:** 3 · **Sprint:** Sprint 0

- **Como:** Administrador
- **Quiero:** ver la lista de usuarios y cuántos hay por rol
- **Para:** conocer quién usa la app

**Criterios de aceptación:**

1. Muestra nombre, correo y roles de cada usuario
2. Muestra el total y la cantidad por rol
3. Nunca se envía la contraseña

#### HU006 · Cambiar roles y eliminar usuarios

**Estado:** Parcial · **Prioridad:** Should · **Puntos:** 5 · **Sprint:** Sprint 0

- **Como:** Administrador o SuperAdministrador
- **Quiero:** cambiar el rol de un usuario y, si soy SuperAdministrador, eliminarlo
- **Para:** controlar el acceso a la app

**Criterios de aceptación:**

1. Un Administrador no puede modificar a otro Administrador ni asignar SuperAdministrador
2. Solo el SuperAdministrador elimina usuarios
3. Nadie puede eliminar su propia cuenta
4. Al eliminar un usuario se borran sus datos

> **Nota:** Parcial: la app elimina sin pedir confirmación; eliminar un usuario inexistente responde 200; un SuperAdministrador puede quitarse su rol, quitárselo a otros y dejar a un usuario sin roles (LIM-04, LIM-05). Un Administrador sí puede convertir a un Usuario en Administrador. En la app, el Administrador solo ve «Hacer admin» sobre usuarios comunes; el SuperAdministrador puede cambiar el rol de cualquiera que no sea SuperAdministrador y eliminar a cualquiera salvo a sí mismo; la app no ofrece asignar el rol SuperAdministrador.

### EP-003 · Catálogo de ejercicios

#### HU007 · Administrar el catálogo desde la app

**Estado:** Planeada · **Prioridad:** Could · **Puntos:** 8 · **Sprint:** Futuro

- **Como:** Administrador
- **Quiero:** crear, editar y desactivar ejercicios del catálogo desde la aplicación
- **Para:** mantener el catálogo sin tocar archivos

**Criterios de aceptación:**

1. Un ejercicio lleva nombre, grupo muscular, equipo, nivel e instrucciones
2. El nombre no puede repetirse
3. Un ejercicio desactivado no aparece al usuario pero se conserva en rutinas ya creadas
4. Un usuario sin rol de administración recibe 403

> **Nota:** Planeada: hoy el catálogo se carga con el importador y archivos de semillas (TK002); no hay pantalla ni endpoints de administración.

#### HU009 · Explorar el catálogo de ejercicios

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** buscar ejercicios y filtrarlos por músculo y equipo
- **Para:** encontrar el ejercicio que necesito

**Criterios de aceptación:**

1. Búsqueda por texto en el nombre
2. Filtros por músculo y por equipo, combinables
3. Si no hay resultados se muestra un mensaje claro
4. Los filtros disponibles salen del catálogo real

> **Nota:** La búsqueda espera 300 ms tras la última tecla y no ignora tildes («biceps» no encuentra «bíceps»). Si falla la carga de filtros, las filas de músculo y equipo no se muestran.

#### HU010 · Ver detalle de un ejercicio

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 3 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** ver el detalle de un ejercicio con sus instrucciones
- **Para:** hacerlo con buena técnica

**Criterios de aceptación:**

1. Muestra músculo principal, secundarios, equipo y nivel
2. Muestra las instrucciones paso a paso numeradas

#### TK002 · Importador de catálogo y semillas

**Estado:** Implementada · **Prioridad:** Should · **Puntos:** 5 · **Sprint:** Sprint 1

- **Como:** Equipo de desarrollo
- **Quiero:** cargar el catálogo, las plantillas y las reglas de recomendación con el importador
- **Para:** poblar la base de datos de forma repetible

**Criterios de aceptación:**

1. python -m tools.importar_catalogo carga ejercicios e imágenes
2. Las semillas son idempotentes: ejecutarlas dos veces no duplica datos
3. Las reglas de recomendación se cargan desde un JSON versionado

### EP-004 · Rutinas

#### HU008 · Administrar rutinas plantilla desde la app

**Estado:** Planeada · **Prioridad:** Could · **Puntos:** 5 · **Sprint:** Futuro

- **Como:** Administrador
- **Quiero:** crear, editar y desactivar las rutinas plantilla del sistema
- **Para:** ofrecer buenas rutinas de partida

**Criterios de aceptación:**

1. Las plantillas editadas se reflejan para todos los usuarios
2. Las rutinas propias no se modifican
3. Un usuario sin rol de administración recibe 403

> **Nota:** Planeada: las plantillas se cargan con semillas; no hay administración desde la app.

#### HU011 · Ver plantillas y mis rutinas

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 3 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** ver las rutinas del sistema y las mías, filtradas por objetivo
- **Para:** elegir con qué entrenar

**Criterios de aceptación:**

1. Las rutinas propias aparecen primero (el servidor las ordena), luego por nombre
2. Filtro por objetivo (general, fuerza, hipertrofia, resistencia) y por nivel
3. Cada tarjeta muestra la cantidad de ejercicios y la duración
4. Nadie ve las rutinas de otro usuario (responde 404)

> **Nota:** La duración es un valor guardado (45 minutos por defecto), no se calcula a partir de series y descansos. Las rutinas que crea el plan automáticamente (origen «plan») se ocultan en la lista de la app.

#### HU012 · Crear mi rutina

**Estado:** Parcial · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** crear una rutina eligiendo ejercicios, series, repeticiones y descanso
- **Para:** entrenar con un plan hecho a mi medida

**Criterios de aceptación:**

1. Nombre obligatorio y entre 1 y 20 ejercicios
2. Series entre 1 y 10 y descanso entre 0 y 600 segundos (60 por defecto)
3. Duración entre 5 y 240 minutos (45 por defecto) y peso entre 0 y 500 kg o sin peso
4. Se pueden poner varios ejercicios del mismo músculo
5. Al guardar se ofrece asignarla al plan semanal (ver HU035)

> **Nota:** Parcial: no se impide repetir el mismo ejercicio dentro de una rutina (LIM-06). El selector de ejercicios de «Nueva rutina» es un diálogo con todo el catálogo, sin paginación ni fotos (TK006).

#### HU013 · Eliminar mi rutina

**Estado:** Implementada · **Prioridad:** Should · **Puntos:** 2 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** eliminar una rutina que creé
- **Para:** quitar las que ya no uso

**Criterios de aceptación:**

1. Pide confirmación antes de borrar
2. Las plantillas del sistema no se pueden eliminar (403)
3. Si la rutina está en mi plan semanal no se puede eliminar (409): primero hay que quitarla del plan
4. El historial de días cumplidos se conserva con el nombre de la rutina

> **Nota:** La app no avisa antes de borrar si la rutina está en el plan: muestra el error que devuelve el servidor.

#### HU014 · Editar mi rutina

**Estado:** Planeada · **Prioridad:** Should · **Puntos:** 5 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** editar el nombre y los ejercicios de una rutina mía
- **Para:** corregirla sin crearla de nuevo

**Criterios de aceptación:**

1. Solo puedo editar mis rutinas, no las plantillas
2. Se aplican las mismas validaciones que al crearla

> **Nota:** Planeada: hoy se editan los ejercicios de cada día dentro del plan (HU034), pero no la rutina original.

#### HU015 · Sesión guiada de entrenamiento

**Estado:** Planeada · **Prioridad:** Should · **Puntos:** 8 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** hacer mi rutina ejercicio por ejercicio con temporizador de descanso y registrando repeticiones y peso
- **Para:** entrenar con orden y ver mi progreso

**Criterios de aceptación:**

1. Muestra un ejercicio a la vez con sus series pendientes
2. El temporizador de descanso arranca al terminar cada serie
3. Se guardan repeticiones y peso de cada serie
4. Al terminar la última serie el día queda cumplido
5. Solo se puede iniciar la rutina del día de hoy

> **Nota:** Planeada: hoy el usuario marca el día como cumplido manualmente (HU018); la app no tiene temporizador ni registro de series hechas.

#### HU035 · Crear una rutina y asignarla al plan

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** crear una rutina y asignarla a un día de mi plan semanal
- **Para:** pasar de crear la rutina a entrenarla sin pasos extra

**Criterios de aceptación:**

1. Al guardar la rutina se ofrece asignarla a un día
2. Se aplican los mismos avisos de descanso que al agregar
3. La rutina original no se modifica: el día recibe una copia

### EP-005 · Plan semanal y calendario

#### HU016 · Armar mi plan semanal

**Estado:** Parcial · **Prioridad:** Must · **Puntos:** 8 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** asignar una rutina a cada día de la semana o marcar el día como descanso
- **Para:** saber qué me toca entrenar cada día

**Criterios de aceptación:**

1. Cada día tiene una rutina o es descanso
2. Cambiar el plan no borra el historial de días ya cumplidos
3. El plan se repite cada semana hasta que lo cambie
4. Se puede asignar un día con rutina existente, plantilla o propia
5. Si el día ya tiene contenido, la app pide confirmar «Reemplazar» antes de asignar

> **Nota:** Parcial: no hay restricción de «solo días futuros»; se puede cambiar cualquier día (incluido hoy) y el cambio aplica desde hoy, el pasado queda protegido por el historial.

#### HU017 · Aviso de descanso muscular de 48 horas

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 8 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** recibir un aviso cuando agrego un músculo que trabajé hace menos de 48 horas
- **Para:** entrenar con buena recuperación sin que la app me bloquee

**Criterios de aceptación:**

1. Al asignar o agregar se compara el grupo muscular principal con los días vecinos, incluido el cambio de semana
2. El aviso explica cuál músculo y cuándo puede volver a entrenarse
3. Solo avisa: el usuario decide con «Asignar igual» o «Agregar igual»; nunca se bloquea
4. Los músculos secundarios no cuentan
5. Abdomen, pantorrillas, cardio y cuerpo completo quedan exentos
6. El valor es configurable en el servidor (48 horas por defecto)

> **Nota:** Reescrita: la versión original decía que la app «no deja» entrenar; el comportamiento real es un aviso sin bloqueo. Con 48 h solo chocan días consecutivos; domingo y lunes cuentan como consecutivos. La app muestra los mensajes del servidor; el valor «48 h» aparece además en un texto fijo de la pantalla del plan, que quedaría desactualizado si se cambiara la configuración.

#### HU018 · Marcar la rutina del día

**Estado:** Parcial · **Prioridad:** Must · **Puntos:** 3 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** marcar como cumplida la rutina del día cuando la hago
- **Para:** registrar que cumplí

**Criterios de aceptación:**

1. Solo se puede marcar el día de hoy
2. No se pueden marcar días pasados ni futuros
3. No se puede marcar un día de descanso
4. Al marcarla aparece el fuego en el calendario

> **Nota:** Parcial: una vez marcado, el día no se puede desmarcar; «hoy» sale de la fecha del teléfono.

#### HU019 · Calendario del plan

**Estado:** Parcial · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** ver un calendario con el estado de cada día
- **Para:** saber de un vistazo cómo voy

**Criterios de aceptación:**

1. Estados: cumplido (fuego), pendiente, incumplido y descanso
2. El día incumplido queda perdido: no se puede recuperar
3. Al tocar un día se ve su rutina
4. El día pasa a incumplido a las 00:00 de la zona horaria configurada (Bogotá por defecto)

> **Nota:** Parcial: los días anteriores al plan se muestran como descanso, no como «sin estado»; la fecha se muestra como AAAA-MM-DD, sin formato en español.

#### HU020 · Racha de días cumplidos

**Estado:** Implementada · **Prioridad:** Should · **Puntos:** 3 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** ver mi racha de días cumplidos seguidos
- **Para:** mantener la constancia

**Criterios de aceptación:**

1. Los días de descanso no rompen la racha
2. Un día incumplido reinicia la racha
3. Se muestra la racha en el inicio y el calendario

#### HU021 · Resumen semanal

**Estado:** Parcial · **Prioridad:** Should · **Puntos:** 3 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** ver cuántos días cumplí de mi plan en la semana y cuáles fallé
- **Para:** evaluar mi progreso

**Criterios de aceptación:**

1. Muestra días cumplidos sobre días planeados
2. Lista los días incumplidos con su rutina
3. Se puede ver la semana anterior

> **Nota:** Parcial: se muestra el avance de la semana; faltan la lista de días incumplidos y la semana anterior (el servidor ya expone /api/plan/incumplidos).

#### HU022 · Plan sugerido automático

**Estado:** Retirada · **Prioridad:** Could · **Puntos:** 8 · **Sprint:** —

- **Como:** Usuario nuevo
- **Quiero:** responder un cuestionario corto y recibir un plan semanal sugerido
- **Para:** empezar sin armar todo a mano

> **Nota:** Retirada: la necesidad queda cubierta por la recomendación personalizada (HU030), agregar al plan (HU033) y crear rutina y asignarla (HU035).

#### HU033 · Agregar un ejercicio a mi plan

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 8 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** agregar un ejercicio a un día de mi plan
- **Para:** armar mi semana desde el catálogo

**Criterios de aceptación:**

1. Elijo el día al que se agrega
2. Se muestra el aviso de descanso de 48 h sin bloquear (ver HU017)
3. Máximo 20 ejercicios por día (400)
4. Un mismo ejercicio no puede repetirse en el mismo día (409)
5. Si el día no tiene rutina se crea una propia del plan; si la rutina es plantilla, propia o compartida con otros días, se copia solo para ese día y la original no cambia
6. Los cardios no muestran descanso entre series

#### HU034 · Editar o quitar ejercicios de un día del plan

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** editar series, repeticiones y peso, o quitar ejercicios de un día
- **Para:** ajustar mi plan a como me sienta

**Criterios de aceptación:**

1. Se pueden editar series, repeticiones y peso de cada ejercicio
2. Se pueden quitar ejercicios del día
3. Quitar un ejercicio pide confirmación; si era el último, el día queda en descanso
4. Editar el plan no deshace un día ya cumplido
5. El historial de días pasados no cambia
6. La unidad (repeticiones, segundos o minutos) no se puede cambiar desde la app

#### HU037 · Ver mi semana en el inicio

**Estado:** Implementada · **Prioridad:** Should · **Puntos:** 5 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** ver en el inicio la tira de la semana, la tarjeta «Hoy toca» y mi progreso
- **Para:** saber de inmediato qué me toca hoy y cómo voy

**Criterios de aceptación:**

1. La tira L–D muestra el estado de cada día
2. La tarjeta «Hoy toca» muestra la rutina del día y permite marcarla
3. El progreso de la semana muestra días cumplidos sobre días planeados
4. La barra inferior da acceso a Inicio, Calendario, Ejercicios y Perfil

#### TK001 · Retirar el módulo de hábitos

**Estado:** Parcial · **Prioridad:** Should · **Puntos:** 3 · **Sprint:** Sprint 2

- **Como:** Equipo de desarrollo
- **Quiero:** quitar los hábitos del Home y del backend
- **Para:** que el calendario del plan sea la única fuente de cumplimiento

**Criterios de aceptación:**

1. El Home muestra la tarjeta «Hoy» con la rutina del día
2. Se eliminan las pantallas de hábitos y sus pruebas
3. Los endpoints de hábitos responden 404

> **Nota:** Parcial: en la app está hecho; en el backend quedan la tabla habito (sin uso), el borrado de esas filas al eliminar un usuario y menciones en documentación antigua (se corrigen con esta actualización).

### EP-006 · Notificaciones

#### HU023 · Recordatorio de la rutina del día

**Estado:** Planeada · **Prioridad:** Should · **Puntos:** 5 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** recibir una notificación a la hora que elija los días que me toca entrenar
- **Para:** no olvidar mi rutina

**Criterios de aceptación:**

1. Muestra el nombre de la rutina del día
2. No se envía en días de descanso ni si ya cumplí
3. Se programa en el celular, sin depender del servidor
4. La app pide el permiso de notificaciones

> **Nota:** Planeada: la app aún no solicita permiso de notificaciones.

#### HU024 · Aviso de día incumplido

**Estado:** Planeada · **Prioridad:** Should · **Puntos:** 5 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** recibir una notificación si no cumplí la rutina de un día
- **Para:** retomar el ritmo

**Criterios de aceptación:**

1. Se envía al final del día si la rutina no se marcó
2. El tono es de ánimo, sin regaños
3. No se envía en días de descanso ni cumplidos

> **Nota:** Planeada.

#### HU025 · Configurar mis notificaciones

**Estado:** Planeada · **Prioridad:** Should · **Puntos:** 3 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** activar o desactivar las notificaciones y elegir la hora
- **Para:** recibir avisos cuando me sirven

**Criterios de aceptación:**

1. Interruptores separados para recordatorio y aviso
2. La hora es configurable
3. La configuración se conserva al cerrar la app

> **Nota:** Planeada.

### EP-007 · Mensajes motivadores

#### HU026 · Mensaje al terminar mi rutina

**Estado:** Parcial · **Prioridad:** Could · **Puntos:** 3 · **Sprint:** Sprint 2

- **Como:** Usuario
- **Quiero:** recibir un mensaje motivador al cumplir la rutina del día
- **Para:** sentirme reconocido y seguir constante

**Criterios de aceptación:**

1. Se muestra al marcar el día como cumplido
2. El mensaje cambia entre cumplimientos
3. Está escrito en español, breve y positivo

> **Nota:** Parcial: hoy el servidor devuelve un mensaje fijo («¡Rutina de hoy cumplida!»); falta la variación.

#### HU027 · Mensajes por racha y semana completa

**Estado:** Planeada · **Prioridad:** Could · **Puntos:** 5 · **Sprint:** Sprint 3

- **Como:** Usuario
- **Quiero:** recibir mensajes especiales al llegar a 3, 7 y 14 días de racha o al completar la semana
- **Para:** celebrar mis logros

**Criterios de aceptación:**

1. Cada hito se celebra una sola vez
2. Al completar la semana se muestra un mensaje especial

> **Nota:** Planeada.

#### HU028 · Frase motivadora en el inicio

**Estado:** Implementada · **Prioridad:** Could · **Puntos:** 2 · **Sprint:** Sprint 0

- **Como:** Usuario
- **Quiero:** ver una frase motivadora en el inicio de la app
- **Para:** empezar cada sesión con ánimo

**Criterios de aceptación:**

1. La frase cambia al iniciar sesión
2. Nunca se repite la anterior

> **Nota:** Pendiente de ajuste: algunas frases aún hablan de hábitos y de tomar agua (TK005).

#### TK005 · Actualizar las frases motivadoras

**Estado:** Planeada · **Prioridad:** Could · **Puntos:** 1 · **Sprint:** Sprint 2

- **Como:** Equipo de desarrollo
- **Quiero:** reemplazar las frases que hablan de hábitos y de agua
- **Para:** que el mensaje corresponda al entrenamiento

**Criterios de aceptación:**

1. Todas las frases hablan de entrenar, constancia y descanso

### EP-008 · Perfil físico y recomendaciones

#### HU029 · Completar mi perfil físico

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** registrar mi peso, estatura, fecha de nacimiento, sexo y nivel
- **Para:** recibir recomendaciones acordes a mi cuerpo

**Criterios de aceptación:**

1. La app pide la fecha de nacimiento y calcula la edad (entre 14 y 100 años)
2. Peso entre 30 y 300 kg y estatura entre 100 y 250 cm
3. El sexo es opcional (hombre, mujer o prefiero no decirlo) y el nivel es obligatorio
4. El perfil puede editarse cuando quiera
5. Se pueden borrar los datos físicos con confirmación

#### HU030 · Ver mi recomendación personalizada

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 8 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** ver series, repeticiones, descanso y peso sugerido para cada ejercicio
- **Para:** entrenar con una carga adecuada a mi nivel y perfil

**Criterios de aceptación:**

1. La recomendación depende del nivel y del perfil físico (peso, edad y sexo)
2. El peso se redondea hacia abajo a múltiplos de 2,5 kg
3. Las duraciones por defecto se redondean a múltiplos de 5 segundos
4. Con perfil incompleto se muestra la recomendación general y una invitación a completarlo
5. Es una recomendación: el usuario puede armar su rutina como quiera

### EP-009 · Catálogo ampliado con imágenes

#### HU031 · Explorar el catálogo con fotos y filtros

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 8 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** explorar el catálogo ampliado filtrando por dónde entreno, músculo, equipo y nivel
- **Para:** encontrar rápido el ejercicio que me sirve

**Criterios de aceptación:**

1. Catálogo de 150 ejercicios, 12 grupos musculares y 7 tipos de equipo
2. Filtros combinables por dónde entreno (gimnasio, casa, calistenia), músculo, equipo y nivel, más búsqueda por texto
3. Paginación de 20 en 20 con opción de reintentar si falla
4. Miniatura de la foto en cada tarjeta, con mensaje si no hay foto o no carga

> **Nota:** Los créditos de las imágenes están en /api/ejercicios/creditos y en la sección de referencias.

#### HU032 · Ver el detalle del ejercicio con fotos y pasos

**Estado:** Implementada · **Prioridad:** Must · **Puntos:** 5 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** ver las fotos de posición inicial y final, los pasos y los errores comunes
- **Para:** hacer el ejercicio con buena técnica

**Criterios de aceptación:**

1. Se muestran las fotos disponibles del ejercicio
2. Se muestran los pasos numerados y los errores comunes
3. Incluye la recomendación personalizada y el botón para agregar al plan

#### HU036 · Ver los créditos de las fotos

**Estado:** Implementada · **Prioridad:** Could · **Puntos:** 2 · **Sprint:** Sprint 1

- **Como:** Usuario
- **Quiero:** consultar la fuente, la licencia y los autores de las fotos del catálogo
- **Para:** conocer el origen de las imágenes

**Criterios de aceptación:**

1. Hay una pantalla «Créditos de las fotos» accesible desde el catálogo
2. Muestra fuentes, licencias y autores que entrega la API

#### TK006 · Selector de ejercicios con fotos y paginación

**Estado:** Planeada · **Prioridad:** Should · **Puntos:** 5 · **Sprint:** Sprint 2

- **Como:** Equipo de desarrollo
- **Quiero:** reemplazar el diálogo de ejercicios de «Nueva rutina» por el catálogo paginado, con fotos y valores prellenados
- **Para:** crear rutinas con la misma experiencia del catálogo

**Criterios de aceptación:**

1. Usa el catálogo paginado con filtros y fotos
2. Prellena series, repeticiones y peso con la recomendación personalizada

### EP-010 · Calidad técnica y seguridad

#### TK003 · Endurecimiento de seguridad

**Estado:** Planeada · **Prioridad:** Should · **Puntos:** 8 · **Sprint:** Sprint 3

- **Como:** Equipo de desarrollo
- **Quiero:** corregir las limitaciones de seguridad conocidas
- **Para:** cumplir mejor el requisito de seguridad

**Criterios de aceptación:**

1. Validar formato de correo y longitud mínima de contraseña
2. Normalizar el correo a minúsculas
3. Invalidar tokens al cambiar la contraseña o eliminar al usuario
4. Impedir que el sistema se quede sin SuperAdministrador
5. Responder 404 al eliminar un usuario inexistente
6. Unificar códigos de error de día inválido (400)

> **Nota:** Cubre LIM-01 a LIM-07.

#### TK004 · Limpiar el módulo de hábitos del backend

**Estado:** Planeada · **Prioridad:** Could · **Puntos:** 2 · **Sprint:** Sprint 3

- **Como:** Equipo de desarrollo
- **Quiero:** eliminar la tabla habito y su borrado en cascada
- **Para:** dejar el código sin restos del módulo anterior

**Criterios de aceptación:**

1. La tabla habito se elimina o se archiva
2. No quedan referencias en código ni README

## 7. Trazabilidad

| Historia | Épica | Estado | Sprint |
|---|---|---|---|
| HU001 | EP-001 | Implementada | Sprint 0 |
| HU002 | EP-001 | Parcial | Sprint 0 |
| HU003 | EP-001 | Implementada | Sprint 0 |
| HU004 | EP-002 | Parcial | Sprint 0 |
| HU005 | EP-002 | Implementada | Sprint 0 |
| HU006 | EP-002 | Parcial | Sprint 0 |
| HU007 | EP-003 | Planeada | Futuro |
| HU008 | EP-004 | Planeada | Futuro |
| HU009 | EP-003 | Implementada | Sprint 1 |
| HU010 | EP-003 | Implementada | Sprint 1 |
| HU011 | EP-004 | Implementada | Sprint 1 |
| HU012 | EP-004 | Parcial | Sprint 1 |
| HU013 | EP-004 | Implementada | Sprint 1 |
| HU014 | EP-004 | Planeada | Sprint 2 |
| HU015 | EP-004 | Planeada | Sprint 2 |
| HU016 | EP-005 | Parcial | Sprint 1 |
| HU017 | EP-005 | Implementada | Sprint 1 |
| HU018 | EP-005 | Parcial | Sprint 1 |
| HU019 | EP-005 | Parcial | Sprint 1 |
| HU020 | EP-005 | Implementada | Sprint 1 |
| HU021 | EP-005 | Parcial | Sprint 2 |
| HU022 | EP-005 | Retirada | — |
| HU023 | EP-006 | Planeada | Sprint 2 |
| HU024 | EP-006 | Planeada | Sprint 2 |
| HU025 | EP-006 | Planeada | Sprint 2 |
| HU026 | EP-007 | Parcial | Sprint 2 |
| HU027 | EP-007 | Planeada | Sprint 3 |
| HU028 | EP-007 | Implementada | Sprint 0 |
| HU029 | EP-008 | Implementada | Sprint 1 |
| HU030 | EP-008 | Implementada | Sprint 1 |
| HU031 | EP-009 | Implementada | Sprint 1 |
| HU032 | EP-009 | Implementada | Sprint 1 |
| HU033 | EP-005 | Implementada | Sprint 2 |
| HU034 | EP-005 | Implementada | Sprint 2 |
| HU035 | EP-004 | Implementada | Sprint 2 |
| HU036 | EP-009 | Implementada | Sprint 1 |
| HU037 | EP-005 | Implementada | Sprint 1 |
| TK001 | EP-005 | Parcial | Sprint 2 |
| TK002 | EP-003 | Implementada | Sprint 1 |
| TK003 | EP-010 | Planeada | Sprint 3 |
| TK004 | EP-010 | Planeada | Sprint 3 |
| TK006 | EP-009 | Planeada | Sprint 2 |
| TK005 | EP-007 | Planeada | Sprint 2 |

## 8. Limitaciones conocidas

Se documentan para que el comportamiento real sea transparente. Su corrección está prevista en TK003.

| ID | Limitación | Historias |
|---|---|---|
| LIM-01 | La sesión de la app vive solo en memoria y se pierde al cerrar la aplicación (la dependencia DataStore está declarada pero no se usa); ante un 401 la app avisa pero no regresa sola al inicio de sesión. | HU002 |
| LIM-02 | El token dura 24 horas fijas, sigue siendo válido tras cambiar la contraseña o eliminar al usuario, y los permisos por rol no cambian hasta iniciar sesión de nuevo. | HU002, HU004 |
| LIM-03 | El servidor no valida el formato del correo ni la longitud de la contraseña (la app exige 8 caracteres solo al registrarse), acepta nombres con solo espacios y distingue mayúsculas de minúsculas en el correo. | HU001, HU003 |
| LIM-04 | Eliminar un usuario inexistente responde 200 y la app elimina sin pedir confirmación. | HU006 |
| LIM-05 | Un SuperAdministrador puede quitarse su rol y se puede dejar a un usuario sin roles, de modo que el sistema podría quedar sin SuperAdministrador. | HU006 |
| LIM-06 | La app no impide repetir el mismo ejercicio dentro de una misma rutina. | HU012 |
| LIM-08 | «Hoy» se calcula con la fecha del teléfono en la app y con la zona horaria del servidor en la API; si no coinciden, el botón de marcar y el calendario pueden diferir. | HU018, HU019 |
| LIM-09 | La duración de una rutina es un valor guardado y no se calcula a partir de sus ejercicios. | HU011 |
| LIM-10 | Las pantallas antiguas (inicio de sesión, registro, editar perfil y cambiar contraseña) muestran códigos HTTP y el texto técnico de las excepciones en lugar de mensajes amigables. | HU001–HU003 |
| LIM-07 | Algunos códigos de error son inconsistentes (un día fuera de 1-7 responde 400 en un endpoint y 404 en otro). | Varias |

## 9. Fuera del alcance

| Elemento | Motivo |
|---|---|
| Módulos de alimentación y sueño | Retirados del proyecto; el producto se concentra en el entrenamiento. |
| Cálculo de calorías | Retirado junto con la alimentación. |
| Seguimiento de hábitos genéricos | Reemplazado por el plan semanal y el calendario (TK001). |
| Plan sugerido automático por cuestionario | Retirado (HU022); cubierto por la recomendación personalizada. |
| Versión iOS y sitio web | Fuera del alcance académico. |
| Pagos, planes premium y red social | Fuera del alcance. |

## 10. Referencias

- Guía de repeticiones y pesos por nivel de PulseUp (documento del equipo).
- free-exercise-db, repositorio de ejercicios con licencia Unlicense: https://github.com/yuhonas/free-exercise-db
- Open Gym, aplicación consultada como referencia de diseño (sus medios son de su autor y no se reutilizan).
- American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7.ª ed.).