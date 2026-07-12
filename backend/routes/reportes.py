"""
Endpoint del reporte de concurrencia por actividad.
HU: Como administrador quiero consultar un reporte mensual con las
actividades de mayor y menor concurrencia.

Reglas de negocio cubiertas:
- Regla 1: acceso exclusivo administrador (chequeo por header X-User-Role,
  igual patrón que ya usan en actividades.py)
- Regla 2: asistencia real = reservas con estado 'asistio', filtradas por
  mes/año de la Clase (instancia con fecha)
- Regla 3: nombre de actividad, total de asistentes, % ocupación promedio
  respecto al cupo (cupo_maximo del Turno)
- Regla 4: orden de mayor a menor concurrencia
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import extract
from models import db, Actividad, Turno, Clase, Reserva

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/api/reportes/concurrencia', methods=['GET'])
def reporte_concurrencia():
    # Regla 1: acceso exclusivo administrador
    role = request.headers.get('X-User-Role')
    if role != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'Acceso exclusivo para administrador'
        }), 403

    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)

    if not mes or not anio:
        return jsonify({
            'status': 'error',
            'message': 'Debe indicar mes y año'
        }), 400

    # Traemos, por cada clase dictada en el mes/año pedido, la actividad
    # a la que pertenece, su cupo_maximo (del turno plantilla) y la
    # cantidad de asistencias reales ('asistio') registradas en esa clase.
    filas = (
        db.session.query(
            Actividad.id.label('actividad_id'),
            Actividad.nombre.label('actividad_nombre'),
            Clase.id.label('clase_id'),
            Turno.cupo_maximo.label('cupo_maximo'),
        )
        .select_from(Clase)
        .join(Turno, Clase.turno_id == Turno.id)
        .join(Actividad, Turno.actividad_id == Actividad.id)
        .filter(extract('month', Clase.fecha) == mes)
        .filter(extract('year', Clase.fecha) == anio)
        .all()
    )

    # Agregamos en Python: por cada clase calculamos su % de ocupación
    # real (asistentes / cupo_maximo), y por actividad promediamos esos
    # porcentajes y sumamos el total de asistentes.
    datos_por_actividad = {}

    for fila in filas:
        asistentes_clase = (
            db.session.query(Reserva)
            .filter(Reserva.clase_id == fila.clase_id)
            .filter(Reserva.estado == 'asistio')
            .count()
        )

        if fila.actividad_id not in datos_por_actividad:
            datos_por_actividad[fila.actividad_id] = {
                'nombre': fila.actividad_nombre,
                'total_asistentes': 0,
                'porcentajes_ocupacion': [],
            }

        datos_por_actividad[fila.actividad_id]['total_asistentes'] += asistentes_clase

        if fila.cupo_maximo:
            porcentaje = (asistentes_clase / fila.cupo_maximo) * 100
            datos_por_actividad[fila.actividad_id]['porcentajes_ocupacion'].append(porcentaje)

    # Armamos la lista final, Regla 3 y Regla 4
    reporte = []
    for datos in datos_por_actividad.values():
        porcentajes = datos['porcentajes_ocupacion']
        ocupacion_promedio = round(sum(porcentajes) / len(porcentajes), 2) if porcentajes else 0.0

        reporte.append({
            'nombre_actividad': datos['nombre'],
            'total_asistentes': datos['total_asistentes'],
            'porcentaje_ocupacion_promedio': ocupacion_promedio,
        })

    # Regla 4: orden de mayor a menor concurrencia
    reporte.sort(key=lambda x: x['total_asistentes'], reverse=True)

    return jsonify({
        'status': 'success',
        'mes': mes,
        'anio': anio,
        'data': reporte,  # Escenario 2: si no hay datos, esto queda como []
    })