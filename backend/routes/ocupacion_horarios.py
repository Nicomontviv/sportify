"""
Endpoint del reporte de ocupación por día y horario.
HU: Como administrador quiero consultar un reporte mensual que muestre
qué días y horarios concentran mayor asistencia.

Reglas de negocio cubiertas:
- Regla 1: acceso exclusivo administrador (mismo patrón que reportes.py)
- Regla 2: filtro por mes (obligatorio) y actividad (opcional)
- Regla 3: día de la semana, franja horaria (horario_inicio-horario_fin
  del Turno) y cantidad de asistentes promedio en el período
- Regla 4: se marca con 'es_mayor_ocupacion' / 'es_menor_ocupacion' la
  fila (o filas, en caso de empate) de mayor y menor promedio
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import extract
from models import db, Turno, Clase, Reserva

ocupacion_horario_bp = Blueprint('ocupacion_horario', __name__)

ORDEN_DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']


@ocupacion_horario_bp.route('/api/reportes/ocupacion-horario', methods=['GET'])
def reporte_ocupacion_horario():
    # Regla 1: acceso exclusivo administrador
    role = request.headers.get('X-User-Role')
    if role != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'Acceso exclusivo para administrador'
        }), 403

    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    actividad_id = request.args.get('actividad_id', type=int)  # Regla 2: opcional

    if not mes or not anio:
        return jsonify({
            'status': 'error',
            'message': 'Debe indicar mes y año'
        }), 400

    # Traemos los turnos que apliquen (filtrando por actividad si corresponde)
    turnos_query = Turno.query
    if actividad_id:
        turnos_query = turnos_query.filter(Turno.actividad_id == actividad_id)
    turnos = turnos_query.all()

    # Agrupamos por (dia_semana, horario_inicio, horario_fin)
    grupos = {}

    for turno in turnos:
        clave = (turno.dia_semana, turno.horario_inicio, turno.horario_fin)

        clases_del_mes = (
            Clase.query
            .filter(Clase.turno_id == turno.id)
            .filter(extract('month', Clase.fecha) == mes)
            .filter(extract('year', Clase.fecha) == anio)
            .all()
        )

        for clase in clases_del_mes:
            asistentes = (
                Reserva.query
                .filter(Reserva.clase_id == clase.id)
                .filter(Reserva.estado == 'asistio')
                .count()
            )

            if clave not in grupos:
                grupos[clave] = []
            grupos[clave].append(asistentes)

    # Regla 3: armamos la lista con el promedio de asistentes por grupo
    reporte = []
    for (dia, hora_inicio, hora_fin), lista_asistentes in grupos.items():
        promedio = round(sum(lista_asistentes) / len(lista_asistentes), 2)
        reporte.append({
            'dia_semana': dia,
            'franja_horaria': f'{hora_inicio.strftime("%H:%M")} - {hora_fin.strftime("%H:%M")}',
            'asistentes_promedio': promedio,
            'es_mayor_ocupacion': False,
            'es_menor_ocupacion': False,
        })

    # Regla 4: marcamos mayor y menor ocupación (si hay datos)
    if reporte:
        max_valor = max(fila['asistentes_promedio'] for fila in reporte)
        min_valor = min(fila['asistentes_promedio'] for fila in reporte)
        for fila in reporte:
            if fila['asistentes_promedio'] == max_valor:
                fila['es_mayor_ocupacion'] = True
            if fila['asistentes_promedio'] == min_valor:
                fila['es_menor_ocupacion'] = True

    # Orden: día de la semana (lunes a viernes) y luego por horario
    def orden_key(fila):
        indice_dia = ORDEN_DIAS.index(fila['dia_semana']) if fila['dia_semana'] in ORDEN_DIAS else 99
        return (indice_dia, fila['franja_horaria'])

    reporte.sort(key=orden_key)

    return jsonify({
        'status': 'success',
        'mes': mes,
        'anio': anio,
        'actividad_id': actividad_id,
        'data': reporte,  # Escenario de sin datos: [] si no hay clases en el período
    })