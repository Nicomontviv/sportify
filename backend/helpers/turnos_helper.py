import calendar
from datetime import date, timedelta
from models import Clase

# Mapeo de la base de datos a los días de Python (0 = Lunes, 6 = Domingo)
DIAS_SEMANA_MAP = {
    'lunes': 0,
    'martes': 1,
    'miercoles': 2,
    'jueves': 3,
    'viernes': 4,
    'sabado': 5,
    'domingo': 6
}


def generar_clases_para_mes(turno, anio, mes):
    """
    [LEGACY - usada por seeds.py]
    Recibe una instancia de Turno, un año y un mes.
    Devuelve una lista de instancias de Clase (no guardadas en DB aún)
    para todas las fechas de ese mes que coincidan con el dia_semana del turno.
    """
    clases_generadas = []
    dia_objetivo = DIAS_SEMANA_MAP.get(turno.dia_semana.lower())

    if dia_objetivo is None:
        return clases_generadas

    cantidad_dias = calendar.monthrange(anio, mes)[1]

    for dia in range(1, cantidad_dias + 1):
        fecha_actual = date(anio, mes, dia)
        if fecha_actual.weekday() == dia_objetivo:
            nueva_clase = Clase(
                turno_id=turno.id,
                fecha=fecha_actual,
                cupo_disponible=turno.cupo_maximo,
                activo=True
            )
            clases_generadas.append(nueva_clase)

    return clases_generadas


def generar_clases_para_rango(turno, fecha_desde, fecha_hasta):
    """
    [NUEVA - usada por gestión de turnos]
    Recibe una instancia de Turno y un rango de fechas.
    Devuelve una lista de instancias de Clase (no guardadas en DB aún)
    para todas las fechas del rango que coincidan con el dia_semana del turno.

    Útil para generar las clases a 3 meses vista cada vez que se crea o
    modifica un turno.
    """
    clases_generadas = []
    dia_objetivo = DIAS_SEMANA_MAP.get(turno.dia_semana.lower())

    if dia_objetivo is None:
        return clases_generadas

    fecha_actual = fecha_desde
    while fecha_actual <= fecha_hasta:
        if fecha_actual.weekday() == dia_objetivo:
            nueva_clase = Clase(
                turno_id=turno.id,
                fecha=fecha_actual,
                cupo_disponible=turno.cupo_maximo,
                activo=True
            )
            clases_generadas.append(nueva_clase)
        fecha_actual += timedelta(days=1)

    return clases_generadas