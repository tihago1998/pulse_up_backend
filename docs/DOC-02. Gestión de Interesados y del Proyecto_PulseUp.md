# DOC-02. Gestión de interesados y del proyecto — PulseUp

**PulseUp: aplicación móvil de entrenamiento con plan semanal**

**Elaborado por:** Santiago Varela Peña y Sebastián Navarro López  
**Instructor:** Richard Betancur  
**Programa:** Tecnología en Análisis y Desarrollo de Software — Ficha 3223873  
**Institución:** Servicio Nacional de Aprendizaje (SENA)  
**Versión:** 2.0 — 24 de noviembre de 2026

---

## Contenido

1. [Propósito del documento](#1-propósito-del-documento)
2. [Definición de interesado](#2-definición-de-interesado)
3. [Interesados](#3-interesados)
4. [Resultados de la encuesta de identificación de usuarios](#4-resultados-de-la-encuesta-de-identificación-de-usuarios)
5. [Tabla de identificación de interesados](#5-tabla-de-identificación-de-interesados)
6. [Mapa de interesados](#6-mapa-de-interesados)
7. [Estrategia de comunicación](#7-estrategia-de-comunicación)
8. [Riesgos asociados a los interesados](#8-riesgos-asociados-a-los-interesados)
9. [Responsable de la gestión de interesados](#9-responsable-de-la-gestión-de-interesados)
10. [Control de cambios](#10-control-de-cambios)

---

## 1. Propósito del documento

Este documento identifica a las personas, grupos u organizaciones que tienen interés o influencia en el proyecto PulseUp. Define sus roles, necesidades, expectativas, nivel de influencia y participación esperada, para asegurar una comunicación adecuada y una buena toma de decisiones durante todo el ciclo del proyecto.

Complementa el Acta de Constitución (DOC-01) y sirve de base para la estrategia de comunicación y la validación del sistema. La caracterización de los usuarios se apoya en una encuesta aplicada a usuarios potenciales.

## 2. Definición de interesado

Un interesado (*stakeholder*) es cualquier persona u organización que puede afectar, verse afectada o percibirse como afectada por un proyecto. En PulseUp incluye al equipo de desarrollo, al instructor y a los usuarios finales.

## 3. Interesados

| Nombre / Grupo | Rol | Interés en el proyecto |
|---|---|---|
| Instructor del SENA | Asesor y evaluador | Guiar el desarrollo y evaluar los entregables |
| Usuarios finales | Usuario | Contar con una herramienta para organizar su entrenamiento |
| Compañeros de clase | Observadores | Ver el proceso como referencia de aprendizaje |

Dentro de la aplicación existen tres **roles de sistema** (Usuario, Administrador y SuperAdministrador). No son interesados externos: son perfiles de acceso descritos en el DOC-03.

## 4. Resultados de la encuesta de identificación de usuarios

La encuesta se aplicó en mayo de 2026 a **6 personas**, cuando la idea del proyecto incluía ejercicio, alimentación y sueño. Para proteger su privacidad, **las respuestas se presentan de forma anónima**: no se publican nombres ni correos, y solo se conservan el rango de edad y la ocupación.

**Participantes**

| # | Participante | Edad | Ocupación |
|---|---|---|---|
| 1 | Encuestado 1 | Menos de 18 años | Estudiante |
| 2 | Encuestado 2 | 26–35 años | Trabajador |
| 3 | Encuestado 3 | 26–35 años | Trabajador |
| 4 | Encuestado 4 | 26–35 años | Trabajador |
| 5 | Encuestado 5 | 18–25 años | Estudiante |
| 6 | Encuestado 6 | 26–35 años | Estudio y trabajo |

**Hallazgos clave**

- El 100 % de los encuestados no lleva ningún control de sus hábitos saludables; solo uno lo hace de forma manual.
- El hábito más difícil de mantener es el ejercicio físico.
- El 83 % estaría dispuesto a usar PulseUp como usuario piloto.
- Las funciones más solicitadas fueron: registro de rutinas de ejercicio, contador de calorías, control de horas de sueño, recordatorios y alarmas, y gráficas de progreso semanal.
- El sistema operativo predominante es Android (83 %); un encuestado usa iPhone.
- La utilidad de reunir ejercicio, comida y sueño en una sola aplicación fue calificada con 4 o 5 sobre 5 por todos los encuestados.

**Cómo se reflejan los hallazgos en la versión actual**

| Función solicitada | Estado en PulseUp | Referencia |
|---|---|---|
| Registro de rutinas de ejercicio | Implementado: rutinas propias, plan semanal y marcado diario | HU012, HU016, HU018 |
| Gráficas de progreso semanal | Parcial: progreso de la semana en el inicio, calendario y racha | HU019–HU021 |
| Recordatorios y alarmas | Planeado (Sprint 2) | HU023–HU025 |
| Contador de calorías | Fuera de alcance de esta versión | DOC-03, sección 9 |
| Control de horas de sueño | Fuera de alcance de esta versión | DOC-03, sección 9 |
| Plataforma Android | Implementado; no hay versión iOS | RNF-004 |

Como el ejercicio fue el hábito más difícil de sostener, el equipo concentró el producto en el entrenamiento. Se recomienda repetir una encuesta breve con la versión actual durante las pruebas de usabilidad.

## 5. Tabla de identificación de interesados

| ID | Nombre / Grupo | Rol | Interés | Influencia | Expectativas | Participación esperada |
|---|---|---|---|---|---|---|
| STK-01 | Santiago Varela Peña | Líder del proyecto | Alta | Alta | Coordinar el equipo, cumplir el cronograma y entregar con calidad | Toma de decisiones y gestión del proyecto |
| STK-02 | Sebastián Navarro López | Desarrollador y diseño | Alta | Alta | Requisitos claros y buen diseño de interfaz | Diseño e implementación de la aplicación |
| STK-03 | Instructor del SENA | Asesor y evaluador | Alta | Alta | Validar entregables y guiar el proceso de desarrollo | Retroalimentación y aprobación de avances |
| STK-04 | Usuarios finales | Usuarios potenciales | Alta | Media | Una aplicación fácil de usar que les ayude a entrenar con orden | Pruebas de usuario y validación de funciones |
| STK-05 | Compañeros de clase | Observadores y testers | Media | Baja | Ver el proceso como referencia de aprendizaje | Retroalimentación durante las pruebas |

## 6. Mapa de interesados

Matriz de interés frente a influencia:

|  | **Bajo interés** | **Alto interés** |
|---|---|---|
| **Alta influencia** | Mantener satisfechos (no aplica en este proyecto) | **Gestión activa:** STK-01 Santiago Varela, STK-02 Sebastián Navarro, STK-03 Instructor |
| **Baja influencia** | **Monitorear:** STK-05 Compañeros de clase | **Mantener informados:** STK-04 Usuarios finales |

**Estrategia por cuadrante**

- **Gestión activa:** comunicación constante, reuniones de seguimiento y validación de entregables.
- **Mantener informados:** encuestas, pruebas de usabilidad y aviso de avances.
- **Monitorear:** actualizaciones ocasionales y participación en pruebas.

## 7. Estrategia de comunicación

| Interesado | Estrategia | Frecuencia | Medio |
|---|---|---|---|
| Instructor del SENA | Entrega de avances y reuniones de seguimiento | Semanal | Presencial o Teams |
| Santiago Varela (líder) | Reuniones de planeación y revisión de tareas | Diaria | WhatsApp y reuniones |
| Sebastián Navarro (desarrollador) | Coordinación de tareas de diseño y desarrollo | Diaria | WhatsApp, GitHub y Jira |
| Usuarios finales | Pruebas de usabilidad y encuestas de validación | Por iteración | Formulario en línea y presencial |
| Compañeros de clase | Presentaciones de avance | Al finalizar cada sprint | Presencial o video |

## 8. Riesgos asociados a los interesados

| Interesado | Riesgo | Plan de mitigación |
|---|---|---|
| Instructor del SENA | Cambios tardíos en los requisitos evaluados | Validaciones frecuentes con entregas parciales |
| Usuarios finales | Baja disponibilidad para las pruebas de usabilidad | Pruebas breves y flexibles, programadas con anticipación |
| Equipo de desarrollo | Falta de tiempo por otras materias del SENA | Calendario de trabajo semanal compartido |
| Compañeros de clase | Retroalimentación poco útil o superficial | Criterios claros de evaluación antes de cada presentación |
| Participantes de la encuesta | Exposición de datos personales | Respuestas anónimas; no se publican nombres ni correos |

## 9. Responsable de la gestión de interesados

**Santiago Varela Peña — líder del proyecto.** Gestiona las comunicaciones, coordina las validaciones con el instructor, facilita las pruebas con los usuarios finales y mantiene actualizada la documentación.

## 10. Control de cambios

| Versión | Fecha | Descripción del cambio | Responsable |
|---|---|---|---|
| 1.0 | Mayo 2026 | Creación inicial del documento a partir de una encuesta aplicada a 6 usuarios | Santiago Varela Peña |
| 2.0 | 24 de noviembre de 2026 | Anonimización de la encuesta; correspondencia entre hallazgos y funciones actuales; apellido de STK-02 corregido; riesgos y comunicación actualizados | Santiago Varela Peña |
