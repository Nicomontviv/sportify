"""
Endpoint del reporte de usuarios y tasa de cancelaciones.
HU: Como administrador quiero consultar un reporte mensual con la
cantidad de usuarios activos y la tasa de cancelaciones.

Reglas de negocio cubiertas:
- Regla 1: acceso exclusivo administrador
- Regla 2: usuarios activos, total de reservas, cancelaciones y tasa
  de cancelación (cancelaciones / reservas totales)
- Regla 3: filtro por mes (y año)
- Regla 4: se diferencian cancelaciones de usuario ('cancelada_usuario')
  y del establecimiento ('cancelada_centro')

Decisión de diseño confirmada: "usuarios activos" = cantidad de
usuarios con Usuario.activo == True al momento de la consulta (no
depende del mes seleccionado, es una foto del estado actual).
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import extract
from models import db, Usuario, Clase, Reserva

usuarios_cancelaciones_bp = Blueprint('usuarios_cancelaciones', __name__)


@usuarios_cancelaciones_bp.route('/api/reportes/usuarios-cancelaciones', methods=['GET'])
def reporte_usuarios_cancelaciones():
    # Regla 1: acceso exclusivo administrador
    role = request.headers.get('X-User-Role')
    if role != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'Acceso exclusivo para administrador'
        }), 403

    # Regla 3: filtro por mes
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)

    if not mes or not anio:
        return jsonify({
            'status': 'error',
            'message': 'Debe indicar mes y año'
        }), 400

    # Usuarios activos: foto del estado actual, no depende del mes
    usuarios_activos = Usuario.query.filter(Usuario.activo == True).count()  # noqa: E712

    # Reservas del mes: se filtra por la fecha de la Clase asociada,
    # ya que Reserva no tiene una fecha propia en el modelo actual.
    reservas_del_mes = (
        Reserva.query
        .join(Clase, Reserva.clase_id == Clase.id)
        .filter(extract('month', Clase.fecha) == mes)
        .filter(extract('year', Clase.fecha) == anio)
        .all()
    )

    total_reservas = len(reservas_del_mes)
    cancelaciones_usuario = sum(1 for r in reservas_del_mes if r.estado == 'cancelada_usuario')
    cancelaciones_centro = sum(1 for r in reservas_del_mes if r.estado == 'cancelada_centro')
    total_cancelaciones = cancelaciones_usuario + cancelaciones_centro

    tasa_cancelacion = round((total_cancelaciones / total_reservas) * 100, 2) if total_reservas > 0 else 0.0

    return jsonify({
        'status': 'success',
        'mes': mes,
        'anio': anio,
        'data': {
            'usuarios_activos': usuarios_activos,
            'total_reservas': total_reservas,
            'cancelaciones_usuario': cancelaciones_usuario,
            'cancelaciones_centro': cancelaciones_centro,
            'total_cancelaciones': total_cancelaciones,
            'tasa_cancelacion': tasa_cancelacion,  # en porcentaje
        }
    })