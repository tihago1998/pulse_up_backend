"""Valores permitidos que comparten ejercicios y rutinas."""
NIVELES = ("principiante", "intermedio", "avanzado")
OBJETIVOS = ("general", "fuerza", "hipertrofia", "resistencia")

# Días de la semana según ISO 8601: 1 = lunes ... 7 = domingo (igual que date.isoweekday())
DIAS_SEMANA = {
    1: "lunes",
    2: "martes",
    3: "miércoles",
    4: "jueves",
    5: "viernes",
    6: "sábado",
    7: "domingo",
}

# Grupos que se pueden entrenar días seguidos: no aplican a la regla de descanso muscular
GRUPOS_SIN_DESCANSO = ("abdomen", "pantorrillas", "cardio", "cuerpo completo")
