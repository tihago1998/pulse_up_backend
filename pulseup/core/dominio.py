"""Valores permitidos que comparten ejercicios, rutinas y el perfil físico."""
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

# Perfil físico: valores y rangos aceptados
SEXOS = ("hombre", "mujer", "no_indica")
EDAD_MINIMA = 14
EDAD_MAXIMA = 100
PESO_MIN_KG = 30
PESO_MAX_KG = 300
ESTATURA_MIN_CM = 100
ESTATURA_MAX_CM = 250
