# Documentación de PulseUp

**PulseUp: aplicación móvil de entrenamiento con plan semanal**  
Santiago Varela Peña y Sebastián Navarro López · Tecnología en Análisis y Desarrollo de Software, SENA · Ficha 3223873  
Versión de la documentación: **2.0 — 24 de noviembre de 2026**

Esta carpeta reúne, en orden, la documentación del proyecto y sus diagramas. Todo está alineado con lo que la aplicación hace hoy: cada historia de usuario indica si está *implementada*, *parcial*, *planeada* o *retirada*.

> **Repositorios:** este repositorio contiene el **backend** (API Flask y SQLite) y la documentación completa. El repositorio de la **aplicación Android** tiene su propio `docs/README.md` con lo específico de la app y un enlace a esta documentación.

## Contenido

1. [Documentos del proyecto](#1-documentos-del-proyecto)
2. [El producto en una página](#2-el-producto-en-una-pagina)
3. [Diagramas de casos de uso](#3-diagramas-de-casos-de-uso)
4. [Diagramas de actividad](#4-diagramas-de-actividad)
5. [Diagramas de secuencia](#5-diagramas-de-secuencia)
6. [Diagramas BPMN](#6-diagramas-bpmn)
7. [Referencias](#7-referencias)
8. [Diagramas históricos](#8-diagramas-historicos)
9. [Cómo se mantiene esta documentación](#9-como-se-mantiene-esta-documentacion)

## 1. Documentos del proyecto

| Documento | Qué contiene | Lectura | Descarga |
|---|---|---|---|
| **DOC-01** Formulación y constitución | Contexto, objetivos, alcance, entregables, equipo, recursos, cronograma y riesgos | [Markdown](DOC-01.%20Formulaci%C3%B3n%20y%20Constituci%C3%B3n%20del%20Proyecto_PulseUp.md) | [Word](DOC-01.%20Formulaci%C3%B3n%20y%20Constituci%C3%B3n%20del%20Proyecto_PulseUp.docx) |
| **DOC-02** Gestión de interesados | Interesados, encuesta (anónima), matriz de interés e influencia, comunicación y riesgos | [Markdown](DOC-02.%20Gesti%C3%B3n%20de%20Interesados%20y%20del%20Proyecto_PulseUp.md) | [Word](DOC-02.%20Gesti%C3%B3n%20de%20Interesados%20y%20del%20Proyecto_PulseUp.docx) |
| **DOC-03** Alcance y requisitos | Requisitos funcionales y no funcionales, reglas de negocio, 43 historias de usuario con su estado, trazabilidad y limitaciones conocidas | [Markdown](DOC-03.%20Alcance%20y%20Especificaci%C3%B3n%20de%20Requisitos_PulseUp.md) | [Word](DOC-03.%20Alcance%20y%20Especificaci%C3%B3n%20de%20Requisitos_PulseUp.docx) |

## 2. El producto en una página

PulseUp ayuda a entrenar con orden. El usuario completa su perfil físico, explora un catálogo de **150 ejercicios con fotos**, recibe una **recomendación personalizada** de series, repeticiones, descanso y peso, arma su **plan semanal** (con un aviso de descanso muscular de 48 horas que orienta sin bloquear) y marca cada día cumplido en un **calendario con racha**.

| Pieza | Tecnología |
|---|---|
| Aplicación | Android nativo: Kotlin, Jetpack Compose, Retrofit y Coil |
| API | Python, Flask, en capas (rutas, servicio y repositorio) |
| Base de datos | SQLite, con esquema aditivo y semillas idempotentes |
| Pruebas | 340 en el backend y 174 en la aplicación |

**Estado de las 43 historias y tareas:** 20 implementadas, 10 parciales, 12 planeadas y 1 retirada. Lo planeado (notificaciones, sesión guiada, resumen semanal completo, administración del catálogo) está identificado en DOC-03.

## 3. Diagramas de casos de uso

![Casos de uso general](diagrams/casos-de-uso/UC-01-casos-de-uso-general.png)

*UC-01. Actores y funciones actuales. Fuente: [`UC-01-casos-de-uso-general.dot`](diagrams/casos-de-uso/UC-01-casos-de-uso-general.dot).*

## 4. Diagramas de actividad

### ACT-01 · Registro e inicio de sesión

*Historias: HU001, HU002.*

![Registro e inicio de sesión](diagrams/actividad/ACT-01-registro-e-inicio-de-sesion.png)

Fuente: [`ACT-01-registro-e-inicio-de-sesion.mmd`](diagrams/actividad/ACT-01-registro-e-inicio-de-sesion.mmd)

### ACT-02 · Completar el perfil físico

*Historias: HU029.*

![Completar el perfil físico](diagrams/actividad/ACT-02-completar-perfil-fisico.png)

Fuente: [`ACT-02-completar-perfil-fisico.mmd`](diagrams/actividad/ACT-02-completar-perfil-fisico.mmd)

### ACT-03 · Explorar el catálogo y ver la recomendación

*Historias: HU009–HU010, HU030–HU032.*

![Explorar el catálogo y ver la recomendación](diagrams/actividad/ACT-03-explorar-catalogo-y-ver-recomendacion.png)

Fuente: [`ACT-03-explorar-catalogo-y-ver-recomendacion.mmd`](diagrams/actividad/ACT-03-explorar-catalogo-y-ver-recomendacion.mmd)

### ACT-04 · Agregar un ejercicio al plan

*Historias: HU017, HU033.*

![Agregar un ejercicio al plan](diagrams/actividad/ACT-04-agregar-ejercicio-al-plan.png)

Fuente: [`ACT-04-agregar-ejercicio-al-plan.mmd`](diagrams/actividad/ACT-04-agregar-ejercicio-al-plan.mmd)

### ACT-05 · Editar el plan del día

*Historias: HU034.*

![Editar el plan del día](diagrams/actividad/ACT-05-editar-plan-del-dia.png)

Fuente: [`ACT-05-editar-plan-del-dia.mmd`](diagrams/actividad/ACT-05-editar-plan-del-dia.mmd)

### ACT-06 · Crear una rutina y asignarla

*Historias: HU012, HU035.*

![Crear una rutina y asignarla](diagrams/actividad/ACT-06-crear-rutina-y-asignarla.png)

Fuente: [`ACT-06-crear-rutina-y-asignarla.mmd`](diagrams/actividad/ACT-06-crear-rutina-y-asignarla.mmd)

### ACT-07 · Marcar el día y la racha

*Historias: HU018–HU020.*

![Marcar el día y la racha](diagrams/actividad/ACT-07-marcar-dia-y-racha.png)

Fuente: [`ACT-07-marcar-dia-y-racha.mmd`](diagrams/actividad/ACT-07-marcar-dia-y-racha.mmd)

### ACT-08 · Administrar usuarios

*Historias: HU004–HU006.*

![Administrar usuarios](diagrams/actividad/ACT-08-administrar-usuarios.png)

Fuente: [`ACT-08-administrar-usuarios.mmd`](diagrams/actividad/ACT-08-administrar-usuarios.mmd)

## 5. Diagramas de secuencia

### SEQ-01 · Registro de usuario

*Historias: HU001.*

![Registro de usuario](diagrams/secuencia/SEQ-01-registro-usuario.png)

Fuente: [`SEQ-01-registro-usuario.mmd`](diagrams/secuencia/SEQ-01-registro-usuario.mmd)

### SEQ-02 · Inicio y cierre de sesión

*Historias: HU002.*

![Inicio y cierre de sesión](diagrams/secuencia/SEQ-02-inicio-sesion.png)

Fuente: [`SEQ-02-inicio-sesion.mmd`](diagrams/secuencia/SEQ-02-inicio-sesion.mmd)

### SEQ-03 · Administrar usuarios

*Historias: HU004–HU006.*

![Administrar usuarios](diagrams/secuencia/SEQ-03-administrar-usuarios.png)

Fuente: [`SEQ-03-administrar-usuarios.mmd`](diagrams/secuencia/SEQ-03-administrar-usuarios.mmd)

### SEQ-04 · Explorar el catálogo con fotos y filtros

*Historias: HU009, HU010, HU031, HU032.*

![Explorar el catálogo con fotos y filtros](diagrams/secuencia/SEQ-04-explorar-catalogo.png)

Fuente: [`SEQ-04-explorar-catalogo.mmd`](diagrams/secuencia/SEQ-04-explorar-catalogo.mmd)

### SEQ-05 · Recomendación personalizada

*Historias: HU029, HU030.*

![Recomendación personalizada](diagrams/secuencia/SEQ-05-recomendacion-personalizada.png)

Fuente: [`SEQ-05-recomendacion-personalizada.mmd`](diagrams/secuencia/SEQ-05-recomendacion-personalizada.mmd)

### SEQ-06 · Agregar un ejercicio al plan con aviso de 48 h

*Historias: HU017, HU033.*

![Agregar un ejercicio al plan con aviso de 48 h](diagrams/secuencia/SEQ-06-agregar-ejercicio-al-plan.png)

Fuente: [`SEQ-06-agregar-ejercicio-al-plan.mmd`](diagrams/secuencia/SEQ-06-agregar-ejercicio-al-plan.mmd)

### SEQ-07 · Editar o quitar ejercicios de un día

*Historias: HU034.*

![Editar o quitar ejercicios de un día](diagrams/secuencia/SEQ-07-editar-plan-del-dia.png)

Fuente: [`SEQ-07-editar-plan-del-dia.mmd`](diagrams/secuencia/SEQ-07-editar-plan-del-dia.mmd)

### SEQ-08 · Crear una rutina y asignarla al plan

*Historias: HU012, HU035.*

![Crear una rutina y asignarla al plan](diagrams/secuencia/SEQ-08-crear-rutina-y-asignar.png)

Fuente: [`SEQ-08-crear-rutina-y-asignar.mmd`](diagrams/secuencia/SEQ-08-crear-rutina-y-asignar.mmd)

### SEQ-09 · Marcar el día cumplido, calendario y racha

*Historias: HU018–HU020.*

![Marcar el día cumplido, calendario y racha](diagrams/secuencia/SEQ-09-marcar-dia-cumplido-y-racha.png)

Fuente: [`SEQ-09-marcar-dia-cumplido-y-racha.mmd`](diagrams/secuencia/SEQ-09-marcar-dia-cumplido-y-racha.mmd)

## 6. Diagramas BPMN

### BPMN-01 · Armar mi plan semanal

![BPMN-01](diagrams/bpmn/BPMN-01-armar-plan-semanal.png)

Archivo editable: [`BPMN-01-armar-plan-semanal.bpmn`](diagrams/bpmn/BPMN-01-armar-plan-semanal.bpmn)

### BPMN-02 · Entrenar y marcar el día

![BPMN-02](diagrams/bpmn/BPMN-02-entrenar-y-marcar-el-dia.png)

Archivo editable: [`BPMN-02-entrenar-y-marcar-el-dia.bpmn`](diagrams/bpmn/BPMN-02-entrenar-y-marcar-el-dia.bpmn)

## 7. Referencias

- **free-exercise-db** — catálogo de ejercicios e imágenes con licencia Unlicense: https://github.com/yuhonas/free-exercise-db. Los créditos también se publican en `GET /api/ejercicios/creditos` y en la pantalla «Créditos de las fotos» de la app.
- **Open Gym** — aplicación consultada como referencia de diseño. Sus medios son de su autor y no se reutilizan.
- Guía de repeticiones y pesos por nivel de PulseUp (documento del equipo), base de las reglas de recomendación.
- American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7.ª ed.).

## 8. Diagramas históricos

Los diagramas de la primera versión (aplicación de hábitos) se conservan en [`diagrams/historico/`](diagrams/historico/README.md). No describen el sistema actual.

## 9. Cómo se mantiene esta documentación

- Los diagramas de actividad y secuencia se escriben en [Mermaid](https://mermaid.js.org/) (`.mmd`) y se exportan a PNG con `mmdc -i archivo.mmd -o archivo.png -b white -s 2`.
- El caso de uso se escribe en Graphviz (`.dot`) y se exporta con `dot -Tpng`.
- Los BPMN se entregan como `.bpmn` (editable en [bpmn.io](https://demo.bpmn.io/)) y PNG.
- Al cambiar el comportamiento de la app, se actualiza primero el estado de la historia en DOC-03 y después el diagrama afectado.