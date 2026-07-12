"""
Endpoint del reporte de morosidad.
HU: Como administrador quiero consultar un reporte de usuarios con
pagos pendientes o incompletos.

Reglas de negocio cubiertas:
- Regla 1: acceso exclusivo administrador
- Regla 2: moroso = usuario con al menos una reserva 'confirmada' con
  monto_pagado < monto_total (puede haber pagado la seña y deber el resto)
- Regla 3: nombre, tipo (abonado/casual vía Usuario.is_abonado_actual)
  y monto adeudado. Antigüedad de la deuda: NO desarrollada por ahora
  (decisión de alcance confirmada, queda para una iteración futura).
- Regla 4: filtro por mes (de la Clase de la reserva) y por tipo de
  usuario (abonado/casual)

ACTUALIZADO: se agrega 'recordatorio_enviado_hoy', para que el frontend
sepa si debe deshabilitar el botón de "Enviar recordatorio" (HU de
notificación de recordatorio de pago).
"""

from datetime import date
from flask import Blueprint, jsonify, request
from sqlalchemy import extract
from models import db, Usuario, Clase, Reserva

morosidad_bp = Blueprint('morosidad', __name__)


@morosidad_bp.route('/api/reportes/morosidad', methods=['GET'])
def reporte_morosidad():
    # Regla 1: acceso exclusivo administrador
    role = request.headers.get('X-User-Role')
    if role != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'Acceso exclusivo para administrador'
        }), 403

    # Regla 4: filtros
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    tipo_usuario = request.args.get('tipo_usuario')  # 'abonado' | 'casual' | None (todos)

    if not mes or not anio:
        return jsonify({
            'status': 'error',
            'message': 'Debe indicar mes y año'
        }), 400

    # Regla 2: reservas confirmadas con saldo pendiente, dentro del mes/año
    reservas_con_deuda = (
        Reserva.query
        .join(Clase, Reserva.clase_id == Clase.id)
        .filter(Reserva.estado == 'confirmada')
        .filter(Reserva.monto_pagado < Reserva.monto_total)
        .filter(extract('month', Clase.fecha) == mes)
        .filter(extract('year', Clase.fecha) == anio)
        .all()
    )

    # Agrupamos por usuario, sumando el monto adeudado de todas sus
    # reservas con deuda en el período.
    deuda_por_usuario = {}
    for reserva in reservas_con_deuda:
        adeudado = float(reserva.monto_total) - float(reserva.monto_pagado)
        if reserva.usuario_id not in deuda_por_usuario:
            deuda_por_usuario[reserva.usuario_id] = 0.0
        deuda_por_usuario[reserva.usuario_id] += adeudado

    hoy = date.today()
    reporte = []
    for usuario_id, monto_adeudado in deuda_por_usuario.items():
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            continue

        es_abonado = usuario.is_abonado_actual
        tipo = 'abonado' if es_abonado else 'casual'

        # Regla 4: filtro opcional por tipo de usuario
        if tipo_usuario and tipo_usuario != tipo:
            continue

        recordatorio_enviado_hoy = bool(
            usuario.ultimo_recordatorio_enviado and
            usuario.ultimo_recordatorio_enviado.date() == hoy
        )

        reporte.append({
            'usuario_id': usuario.id,
            'nombre_completo': f'{usuario.nombre} {usuario.apellido}',
            'tipo': tipo,
            'monto_adeudado': round(monto_adeudado, 2),
            'recordatorio_enviado_hoy': recordatorio_enviado_hoy,
        })

    # Orden: de mayor a menor deuda, para priorizar cobranzas
    reporte.sort(key=lambda x: x['monto_adeudado'], reverse=True)

    return jsonify({
        'status': 'success',
        'mes': mes,
        'anio': anio,
        'tipo_usuario': tipo_usuario,
        'data': reporte,  # Escenario 2: [] si no hay morosos en el período
    })