"""
Endpoint para enviar un recordatorio de pago a un usuario moroso.
HU: Notificación de recordatorio de pago a morosos.

Reglas de negocio cubiertas:
- Regla 1: acceso exclusivo administrador
- Regla 2: (se valida contra el mismo criterio de morosidad: reserva
  'confirmada' con monto_pagado < monto_total)
- Regla 3: se registra la fecha de envío en Usuario.ultimo_recordatorio_enviado
- Regla 4 (Escenario 2, bloquear reenvío): si ya se envió un recordatorio
  hoy, se rechaza el reenvío con status 409

Nota: el envío es SIMULADO (no se manda un email real). Se registra la
fecha y se devuelve un mensaje de confirmación, como corresponde a un
proyecto académico sin servidor de mail configurado.
"""

from datetime import datetime, timezone, date
from flask import Blueprint, jsonify, request
from models import db, Usuario, Clase, Reserva

recordatorio_bp = Blueprint('recordatorio', __name__)


@recordatorio_bp.route('/api/reportes/morosidad/recordatorio/<int:usuario_id>', methods=['POST'])
def enviar_recordatorio(usuario_id):
    # Regla 1: acceso exclusivo administrador
    role = request.headers.get('X-User-Role')
    if role != 'admin':
        return jsonify({
            'status': 'error',
            'message': 'Acceso exclusivo para administrador'
        }), 403

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({
            'status': 'error',
            'message': 'Usuario no encontrado'
        }), 404

    # Regla 2: solo se puede notificar a usuarios que efectivamente son morosos
    tiene_deuda = (
        Reserva.query
        .filter(Reserva.usuario_id == usuario_id)
        .filter(Reserva.estado == 'confirmada')
        .filter(Reserva.monto_pagado < Reserva.monto_total)
        .first()
    )
    if not tiene_deuda:
        return jsonify({
            'status': 'error',
            'message': 'El usuario no tiene deuda pendiente, no corresponde enviar recordatorio'
        }), 400

    # Regla 4: bloquear reenvío si ya se envió hoy
    hoy = date.today()
    if usuario.ultimo_recordatorio_enviado and usuario.ultimo_recordatorio_enviado.date() == hoy:
        return jsonify({
            'status': 'error',
            'message': f'Ya se envió un recordatorio a {usuario.nombre} {usuario.apellido} hoy'
        }), 409

    # Regla 3: registrar el envío (simulado)
    usuario.ultimo_recordatorio_enviado = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f'Recordatorio enviado a {usuario.nombre} {usuario.apellido}',
        'ultimo_recordatorio_enviado': usuario.ultimo_recordatorio_enviado.isoformat()
    })