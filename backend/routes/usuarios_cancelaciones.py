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

Decisión de diseño actualizada: "usuarios activos" = usuarios cuya
cuenta no estaba dada de baja durante el mes consultado. Se calcula
de forma histórica usando Usuario.fecha_alta y Usuario.fecha_baja,
para que reportes de meses pasados no cambien retroactivamente
cuando se da de baja a un usuario en el presente.
"""

import calendar
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import extract, or_
from models import db, Usuario, Clase, Reserva

usuarios_cancelaciones_bp = Blueprint('usuarios_cancelaciones', __name__)


def usuarios_activos_en_periodo(mes, anio):
    """
    Cuenta usuarios cuya cuenta estaba habilitada en algún momento
    del mes/año indicado: ya existían (fecha_alta <= fin de mes) y
    no fueron dados de baja antes de que termine ese mes
    (fecha_baja es None o es posterior al fin de mes).
    """
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fin_del_mes = datetime(anio, mes, ultimo_dia, 23, 59, 59)

    return Usuario.query.filter(
        Usuario.fecha_alta <= fin_del_mes,
        or_(
            Usuario.fecha_baja.is_(None),
            Usuario.fecha_baja > fin_del_mes
        )
    ).count()


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

    # Escenario 2 de la HU: si no hubo reservas registradas en el
    # período, se informa explícitamente en vez de devolver ceros.
    if total_reservas == 0:
         return jsonify({
           'status': 'success',
           'mes': mes,
           'anio': anio,
           'data': {},  # objeto vacío en vez de None
           'message': 'No hay datos disponibles para ese período'
        })

    cancelaciones_usuario = sum(1 for r in reservas_del_mes if r.estado == 'cancelada_usuario')
    cancelaciones_centro = sum(1 for r in reservas_del_mes if r.estado == 'cancelada_centro')
    total_cancelaciones = cancelaciones_usuario + cancelaciones_centro

    tasa_cancelacion = round((total_cancelaciones / total_reservas) * 100, 2) if total_reservas > 0 else 0.0

    # Usuarios activos: foto histórica del mes consultado, no del
    # estado actual (ver usuarios_activos_en_periodo).
    usuarios_activos = usuarios_activos_en_periodo(mes, anio)

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