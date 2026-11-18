**ACTA DE CONSTITUCIÓN DEL PROYECTO**

**PulseUp**

Aplicación Móvil de Hábitos Saludables

**Elaborado por:**

Santiago Varela Peña

Sebastián Navarro López

Servicio Nacional de Aprendizaje – SENA

Tecnología en Análisis y Desarrollo de Software

2026

"PulseUp: Aplicación Móvil de Hábitos Saludables"

### **Alcance Funcional del Proyecto (Requerimientos funcionales y no funcionales)**

**Requerimientos funcionales**

**RF-001**

El sistema debe permitir un registro por correo

**RF-002**

El sistema debe permitir acceso como login

**RF-003**

El sistema debe contener un módulo de alimentación

**RF-004**

El sistema debe contener un módulo de sueño

**RF-005**

El sistema debe contener un módulo de ejercicio

**Requerimientos no funcionales**

**RNF-001**

**SEGURIDAD**

El sistema debe proteger los datos personales del usuario

**RNF-002**

**IMC**

El sistema debe ser liviano para ser usado en cualquier contexto

**Fuera de alcance/Limites**

Funcionalidad Descartada

Razón Técnica / Estratégica (Por qué no)

Planes de entrenamiento automáticos con IA

Implementar un modelo de inteligencia artificial requiere tiempo, datos e infraestructura que no están disponibles en 8 semanas.

Cálculo nutricional preciso de alimentos

Necesita una base de datos nutricional completa (como la de la USDA) que es costosa o compleja de integrar correctamente.

Integración con Google Fit o Apple Health

Requiere certificaciones de Google y Apple, además de un proceso de revisión que tarda semanas.

Alarma de sueño inteligente

Analizar ciclos de sueño requiere sensores del dispositivo que no todos los celulares tienen disponibles para apps externas.

Versión web del sistema

Desarrollar web y móvil al mismo tiempo con solo dos personas en un plazo de 8 semanas no es viable.

Módulo de pagos o suscripciones

Requiere pasarelas de pago, términos legales y certificaciones de seguridad que están fuera del alcance académico.

Recomendación inteligente de hora para dormir

Para que sea útil necesita varios días de datos históricos y un algoritmo de análisis que no es prioridad en esta versión.

**Product Backlog Inicial (20 Historias de Usuario Y épicas)**

**EP-001: Registro y Seguimiento de Ejercicio**

HU001 - Como: Usuario de PulseUp | Quiero: registrarme en la app | Para: tener mi perfil personal de hábitos P.T :5

HU002 - Como: Usuario de PulseUp | Quiero: iniciar sesión | Para: Inrgresar en mi

cuenta P.T :5

HU003 - Como: Usuario de PulseUp | Quiero: Ver el logo de la pp | Para: Identificarla rápidamente P.T :5

HU004 - Como: Usuario activo | Quiero: registrar una rutina de ejercicio | Para: llevar el control de mis entrenamientos P.T : 13

HU005 - Como: Usuario activo | Quiero: seleccionar el tipo de actividad física (correr, pesas, yoga, etc.) | Para: clasificar mis ejercicios correctamente P.H: 8

HU006 - Como: Usuario activo | Quiero: ingresar la duración de mi ejercicio | Para: saber cuánto tiempo llevo entrenando P.T : 8

HU007 - Como: Usuario activo | Quiero: ver las calorías quemadas por actividad | Para: medir mi esfuerzo diario ´P.T : 8

**EP-002: Control de Alimentación**

HU008 - Como: Usuario consciente de su dieta | Quiero: registrar los alimentos que consumo durante el día | Para: llevar un diario de nutrición P.T : 8

HU009 - Como: Usuario consciente de su dieta | Quiero: ver el valor calórico de los alimentos | Para: saber si mi dieta está balanceada P.T : 8

HU010 - Como: Usuario con metas nutricionales | Quiero: establecer una meta calórica diaria | Para: controlar mejor mi consumo de alimentos P.T : 5

HU011 - Como: Usuario organizado | Quiero: categorizar mis comidas por desayuno, almuerzo y cena | Para: organizar mejor mi alimentación diaria P.T : 3

HU012 - Como: Usuario con control calórico | Quiero: recibir una alerta cuando esté cerca de superar mi límite | Para: no excederme en mi consumo diario P.T :13

**EP-003: Monitoreo del Sueño**

HU013 - Como: Usuario que cuida su descanso | Quiero: registrar la hora en que me duermo y me despierto | Para: calcular mis horas de descanso P.T : 8

HU014 - Como: Usuario que cuida su descanso | Quiero: ver un resumen diario de mi sueño | Para: saber si estoy descansando lo suficiente P.T : 8

HU015 - Como: Usuario que busca mejorar su sueño | Quiero: recibir una recomendación de hora para dormir | Para: adaptar mis horarios según mis hábitos registrados P.T : 8

HU016 - Como: Usuario con horarios irregulares | Quiero: configurar una alarma de sueño desde la app | Para: mantener horarios de descanso regulares P.T : 13

**EP-004: Reportes y Progreso**

HU017 - Como: Usuario comprometido con su bienestar | Quiero: ver un resumen semanal de mis tres hábitos | Para: evaluar mi progreso general de forma fácil P.T : 8

HU018 - Como: Usuario motivado | Quiero: visualizar gráficas de mi evolución | Para: entender mis avances de forma visual y clara P.T : 3

HU019 - Como: Usuario constante | Quiero: comparar mi rendimiento semanal con el de la semana anterior | Para: ver si realmente estoy mejorando P.T : 8

HU020 - Como: Usuario que necesita motivación | Quiero: recibir un mensaje motivador al cumplir mis metas del día | Para: mantenerme constante con mis hábitos P.T : 8

**EP-005: Personalización y Recordatorios**

HU019 - Como: Usuario con vida ocupada | Quiero: configurar recordatorios diarios de ejercicio, comida y sueño | Para: no olvidar mis rutinas importantes P.T : 13

HU020 - Como: Usuario que valora la personalización | Quiero: personalizar mi perfil con nombre, foto y metas | Para: sentir que la app es realmente mía P.T : 8

**Priorización del Product Backlog**

**Técnica utilizada: MoSCoW**

Para priorizar las historias de usuario de PulseUp utilizamos la técnica MoSCoW, que clasifica cada historia según su nivel de importancia en cuatro categorías: Must Have (debe tener), Should Have (debería tener), Could Have (podría tener) y Won't Have (no en esta versión). La escogimos porque es fácil de entender y nos permite tomar decisiones rápidas sobre qué desarrollar primero, siendo muy útil para equipos pequeños con tiempo limitado como el nuestro.

**#**

**Historia de Usuario**

**Épica**

**MoSCoW**

**Justificación**

1

Como: Usuario | Quiero: registrarme | Para: tener mi perfil

EP-001

● Must Have

Sin registro no hay app

2

Como: Usuario activo | Quiero: registrar rutina | Para: controlar entrenamientos

EP-001

● Must Have

Funcionalidad central del producto

3

Como: Usuario activo | Quiero: elegir actividad | Para: clasificar ejercicios

EP-001

● Must Have

Necesario para clasificar ejercicios

4

Como: Usuario activo | Quiero: ingresar duración | Para: saber cuánto entrené

EP-001

● Must Have

Dato clave del seguimiento

5

Como: Usuario | Quiero: ver calorías quemadas | Para: medir esfuerzo

EP-0011

● Should Have

Añade valor pero no es crítico

6

Como: Usuario | Quiero: registrar alimentos | Para: diario de nutrición

EP-002

● Must Have

Módulo principal de alimentación

7

Como: Usuario | Quiero: ver calorías | Para: balancear dieta

EP-002

● Must Have

Base del control de nutrición

8

Como: Usuario | Quiero: fijar meta calórica | Para: controlar consumo

EP-002

● Should Have

Importante pero puede iniciar sin esto

9

Como: Usuario | Quiero: categorizar comidas | Para: organizar alimentación

EP-002

● Should Have

Mejora la organización del usuario

10

Como: Usuario | Quiero: recibir alerta calórica | Para: no excederme

EP-002

● Could Have

Útil pero no urgente en primera versión

11

Como: Usuario | Quiero: registrar sueño | Para: calcular descanso

EP-003

● Must Have

Funcionalidad central del módulo sueño

12

Como: Usuario | Quiero: ver resumen sueño | Para: saber si descanso bien

EP-003

● Must Have

El usuario necesita ver sus datos

13

Como: Usuario | Quiero: recibir recomendación de sueño | Para: mejorar mis horarios

EP-003

● Could Have

Valor agregado, no esencial al inicio

14

Como: Usuario | Quiero: alarma de sueño | Para: horarios regulares

EP-003

● Could Have

Puede reemplazarse con alarma del celular

15

Como: Usuario | Quiero: ver resumen semanal | Para: evaluar progreso

EP-004

● Must Have

Esencial para ver el progreso

16

Como: Usuario | Quiero: ver gráficas | Para: entender avances

EP-004

● Should Have

Muy valorado por el usuario

17

Como: Usuario | Quiero: comparar semanas | Para: ver mejoras

EP-004

● Should Have

Útil para motivación y mejora

18

Como: Usuario | Quiero: mensaje motivador | Para: mantener constancia

EP-004

● Could Have

Mejora experiencia pero no es funcional

19

Como: Usuario | Quiero: configurar recordatorios | Para: mantener rutinas

EP-005

● Should Have

Ayuda a mantener la constancia

20

Como: Usuario | Quiero: personalizar perfil | Para: sentirla mía

EP-005

● Could Have

Mejora la experiencia personal del usuario

**Backlog Priorizado para Sprint 1**

Con base en la priorización MoSCoW, el primer sprint se enfocará en las historias Must Have, que son las que permiten que la app funcione de manera básica y completa. Las historias Should Have se trabajarán en el Sprint 2, y las Could Have quedan para versiones posteriores.

**Orden**

**Historia de Usuario**

**Épica**

**Prioridad**

**Sprint**

1

Como: Usuario | Quiero: registrarme | Para: tener mi perfil

EP-001

● Must Have

Sprint 1

2

Como: Usuario activo | Quiero: registrar rutina | Para: controlar entrenamientos

EP-001

● Must Have

Sprint 1

3

Como: Usuario activo | Quiero: elegir actividad | Para: clasificar ejercicios

EP-001

● Must Have

Sprint 1

4

Como: Usuario activo | Quiero: ingresar duración | Para: saber cuánto entrené

EP-001

● Must Have

Sprint 1

5

Como: Usuario | Quiero: registrar alimentos | Para: diario de nutrición

EP-002

● Must Have

Sprint 1

6

Como: Usuario | Quiero: ver calorías | Para: balancear dieta

EP-002

● Must Have

Sprint 1

7

Como: Usuario | Quiero: registrar sueño | Para: calcular descanso

EP-003

● Must Have

Sprint 1

8

Como: Usuario | Quiero: ver resumen sueño | Para: saber si descanso bien

EP-003

● Must Have

Sprint 1

9

Como: Usuario | Quiero: ver resumen semanal | Para: evaluar progreso

EP-004

● Must Have

Sprint 1

10

Como: Usuario | Quiero: ver calorías quemadas | Para: medir esfuerzo

EP-001

● Should Have

Sprint 2

11

Como: Usuario | Quiero: fijar meta calórica | Para: controlar consumo

EP-002

● Should Have

Sprint 2

12

Como: Usuario | Quiero: categorizar comidas | Para: organizar alimentación

EP-002

● Should Have

Sprint 2

13

Como: Usuario | Quiero: ver gráficas | Para: entender avances

EP-004

● Should Have

Sprint 2

14

Como: Usuario | Quiero: comparar semanas | Para: ver mejoras

EP-004

● Should Have

Sprint 2

15

Como: Usuario | Quiero: configurar recordatorios | Para: mantener rutinas

EP-005

● Should Have

Sprint 2

16

Como: Usuario | Quiero: recibir alerta calórica | Para: no excederme

EP-002

● Could Have

Sprint 3

17

Como: Usuario | Quiero: recomendación de sueño | Para: mejorar horarios

EP-003

● Could Have

Sprint 3

18

Como: Usuario | Quiero: alarma de sueño | Para: horarios regulares

EP-003

● Could Have

Sprint 3

19

Como: Usuario | Quiero: mensaje motivador | Para: mantener constancia

EP-004

● Could Have

Sprint 3

20

Como: Usuario | Quiero: personalizar perfil | Para: sentirla mía

EP-005

● Could Have

Sprint 3