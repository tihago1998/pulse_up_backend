# DOC-01. Acta de constitución del proyecto — PulseUp

**PulseUp: aplicación móvil de entrenamiento con plan semanal**

**Elaborado por:** Santiago Varela Peña y Sebastián Navarro López  
**Instructor:** Richard Betancur  
**Programa:** Tecnología en Análisis y Desarrollo de Software — Ficha 3223873  
**Institución:** Servicio Nacional de Aprendizaje (SENA)  
**Versión:** 2.0 — 24 de noviembre de 2026

---

## Contenido

1. [Contexto](#1-contexto)
2. [Justificación técnica](#2-justificación-técnica)
3. [Objetivo general](#3-objetivo-general)
4. [Objetivos específicos](#4-objetivos-específicos)
5. [Beneficios e indicadores de éxito](#5-beneficios-e-indicadores-de-éxito)
6. [Alcance general](#6-alcance-general)
7. [Entregables principales](#7-entregables-principales)
8. [Líder del proyecto](#8-líder-del-proyecto)
9. [Equipo de trabajo](#9-equipo-de-trabajo)
10. [Recursos](#10-recursos)
11. [Cronograma general](#11-cronograma-general)
12. [Riesgos identificados](#12-riesgos-identificados)
13. [Control de cambios](#13-control-de-cambios)

---

## 1. Contexto

Muchas personas quieren empezar a entrenar o mantener una rutina, pero el trabajo y el estudio hacen difícil sostenerla. No siempre se sabe qué ejercicios hacer, con qué carga, cuántas repeticiones, ni si se está dejando descansar el músculo lo suficiente entre una sesión y otra.

PulseUp **no** busca reemplazar a un entrenador, a un médico ni al gimnasio. Busca poner orden: ofrece a quien está comenzando, o retomando, una forma sencilla de elegir ejercicios, recibir una guía de carga acorde a su nivel y a su cuerpo, armar un plan semanal y llevar el registro de lo que cumple. Quien necesite acompañamiento profesional debe acudir a él; para el resto, la aplicación aporta estructura y seguimiento.

**Cambio de enfoque.** La idea inicial del proyecto (mayo de 2026) integraba tres módulos: ejercicio, alimentación y sueño. Durante el desarrollo el equipo decidió concentrarse en el entrenamiento, porque es el hábito que los encuestados señalaron como más difícil de mantener (ver DOC-02) y porque permite entregar una primera versión completa y comprobable en el plazo del programa. Los módulos de alimentación y sueño quedan fuera del alcance de esta versión.

## 2. Justificación técnica

Existen muchas aplicaciones de entrenamiento, pero la mayoría exige suscripción o no adapta la carga al perfil físico de quien la usa. PulseUp reúne en una sola aplicación:

- un catálogo de 150 ejercicios con fotos de la posición inicial y final, pasos y errores comunes;
- una recomendación de series, repeticiones, descanso y peso según el nivel y el perfil físico (peso, estatura, edad y sexo);
- un plan semanal con aviso de descanso muscular de 48 horas, que orienta sin bloquear al usuario;
- un calendario con la racha de días cumplidos.

Como estudiantes de desarrollo de software, el proyecto nos permite aplicar lo aprendido en una solución completa: aplicación Android nativa, API REST propia, base de datos, pruebas automáticas y documentación.

## 3. Objetivo general

Desarrollar una aplicación móvil Android que permita al usuario explorar ejercicios, recibir recomendaciones personalizadas, armar su plan semanal de entrenamiento y registrar su cumplimiento, para ayudarle a crear y mantener una rutina de manera sencilla y organizada.

## 4. Objetivos específicos

- Construir un catálogo de ejercicios con fotos y filtros por lugar de entrenamiento, músculo, equipo y nivel.
- Calcular una recomendación personalizada de series, repeticiones, descanso y peso a partir del nivel y del perfil físico del usuario.
- Permitir crear rutinas propias, agregar ejercicios al plan semanal y editar el plan de cada día, con avisos de descanso muscular de 48 horas.
- Registrar el cumplimiento diario en un calendario con cuatro estados y una racha de días cumplidos.
- Implementar registro, inicio de sesión y tres roles (Usuario, Administrador y SuperAdministrador) para que cada persona tenga su propio perfil y sus datos.
- Ofrecer una interfaz sencilla e intuitiva que cualquier persona pueda usar sin dificultad.
- Documentar el proyecto con requisitos, historias de usuario y diagramas coherentes con lo construido.

## 5. Beneficios e indicadores de éxito

**Beneficios para el usuario:** orden en su entrenamiento, una guía de carga adecuada a su nivel, avisos para descansar el músculo y motivación mediante la racha.

**Indicadores de éxito** (medibles a la fecha de este documento):

| Indicador | Resultado |
|---|---|
| Ejercicios en el catálogo | 150, con fotos de posición inicial y final |
| Historias de usuario implementadas | 20 de 43 ítems del backlog; 10 más parciales (ver DOC-03) |
| Pruebas automáticas del backend | 340 pruebas aprobadas |
| Pruebas automáticas de la aplicación | 174 pruebas aprobadas |
| Flujo principal probado en un teléfono Android real | Catálogo, recomendación, plan, calendario y racha |
| Usuarios piloto | Pendiente de la fase de pruebas de usabilidad |

## 6. Alcance general

**Incluye:** registro e inicio de sesión; roles y administración de usuarios; perfil físico; catálogo de ejercicios con fotos; recomendación personalizada; rutinas propias y plantillas; plan semanal con aviso de descanso muscular; marcado del día, calendario y racha; mensajes motivadores.

**Planeado para sprints siguientes:** notificaciones de recordatorio y de día incumplido, sesión guiada con temporizador, resumen semanal completo, administración del catálogo desde la aplicación y endurecimiento de seguridad.

**No incluye:** módulos de alimentación y sueño, cálculo de calorías, integración con relojes inteligentes o aplicaciones de terceros, versión web ni versión iOS. El enfoque es una primera versión funcional en Android.

El detalle de cada función y su estado se encuentra en el **DOC-03**.

## 7. Entregables principales

| N° | Entregable | Descripción | Estado |
|---|---|---|---|
| 1 | Documento de requisitos | Requisitos, reglas de negocio e historias de usuario (DOC-03) | Versión 2.0 |
| 2 | Prototipo de interfaz | Maquetas de las pantallas del catálogo, el detalle y la creación de rutinas | Entregado |
| 3 | Aplicación móvil funcional | Aplicación Android y API REST | En desarrollo (Sprint 2 en curso) |
| 4 | Manual de usuario | Guía para usar la aplicación | Por elaborar |
| 5 | Documentación final | Documentos y diagramas del proyecto | En curso |

## 8. Líder del proyecto

**Nombre:** Santiago Varela Peña  
**Correo:** (pendiente por definir)  
**Responsabilidades:** organizar las tareas del equipo, hacer seguimiento al avance, coordinar con el instructor y revisar que los entregables estén listos a tiempo.

## 9. Equipo de trabajo

| Nombre | Rol | Funciones |
|---|---|---|
| Santiago Varela Peña | Product owner y desarrollador | Lógica de la aplicación, base de datos y coordinación del proyecto |
| Sebastián Navarro López | Desarrollador y Scrum master | Diseño de interfaces y experiencia de usuario |

## 10. Recursos

- **Equipos:** computadores personales de cada integrante y un teléfono Android para las pruebas.
- **Aplicación móvil:** Android Studio, Kotlin, Jetpack Compose, Retrofit y Coil.
- **Backend:** Python, Flask y SQLite.
- **Gestión y control de versiones:** GitHub (repositorios de la aplicación y del backend) y Jira (épicas, historias de usuario y sprints).
- **Herramientas de apoyo:** Visual Studio Code y asistentes de inteligencia artificial para el desarrollo y la documentación.
- **Contenido:** imágenes del repositorio free-exercise-db (licencia Unlicense); sus créditos se publican en la API y en la documentación.
- **Tiempo disponible:** 4 a 5 meses.
- **Apoyo:** instructor del SENA y recursos de aprendizaje en línea.

## 11. Cronograma general

| Fase | Duración | Inicio | Fin | Estado |
|---|---|---|---|---|
| Análisis y planeación | 1 mes | Mayo 2026 | Junio 2026 | Completada |
| Diseño de interfaces | 1 mes | Junio 2026 | Julio 2026 | Completada (maquetas del catálogo en noviembre) |
| Desarrollo de la aplicación | 4 a 5 meses | Julio 2026 | Noviembre 2026 | En curso (Sprint 2 y 3 pendientes) |
| Pruebas y cierre | 1 mes | Diciembre 2026 | Enero 2027 | Pendiente |

Las fechas son estimadas y se ajustan según el avance de los sprints.

## 12. Riesgos identificados

| Riesgo | Probabilidad | Impacto | Plan de acción | Estado |
|---|---|---|---|---|
| Falta de tiempo por otras materias | Media | Alto | Calendario de trabajo semanal y sprints cortos | Vigente |
| Dificultades con la tecnología móvil | Media | Alto | Tutoriales, práctica y revisión con el instructor | Mitigado: la aplicación ya funciona en un teléfono real |
| Pérdida de archivos o código | Baja | Alto | GitHub como respaldo desde el inicio | Mitigado |
| Cambio de alcance durante el desarrollo | Media | Medio | Retiro de alimentación y sueño documentado; backlog priorizado en Jira | Controlado |
| Limitaciones de seguridad conocidas del backend | Media | Medio | Registradas en DOC-03 (LIM-01 a LIM-10); corrección planeada en la tarea TK003 | Vigente |
| Contenido de terceros (imágenes del catálogo) | Baja | Medio | Uso de un repositorio con licencia abierta y créditos visibles | Controlado |

## 13. Control de cambios

| Versión | Fecha | Descripción del cambio | Responsable |
|---|---|---|---|
| 1.0 | Mayo 2026 | Creación inicial del acta (tres módulos: ejercicio, alimentación y sueño) | Santiago Varela Peña |
| 2.0 | 24 de noviembre de 2026 | Redefinición del enfoque hacia el entrenamiento con plan semanal; alcance, objetivos, recursos, cronograma y riesgos alineados con la implementación | Santiago Varela Peña |
