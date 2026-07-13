from flask import Blueprint, request, jsonify
from models import db, Clase, ListaEspera, Usuario, Notificacion
from datetime import datetime, timedelta
from models import Reserva
from helpers.espera_helper import procesar_lista_espera_al_cancelar
# Creamos un Blueprint exclusivo para la lista de espera
lista_espera_bp = Blueprint('lista_espera', __name__)

@lista_espera_bp.route('', methods=['POST'])
def unirse_lista_espera():
    # Simulamos el ID del usuario viniendo desde el header por seguridad
    usuario_id = request.headers.get('X-User-Id')
    data = request.get_json()
    clase_id = data.get('clase_id')

    if not usuario_id or not clase_id:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    clase = db.session.get(Clase, clase_id)
    if not clase:
        return jsonify({"status": "error", "message": "La clase no existe"}), 404

    # Validación lógica: Solo se puede unir si NO hay cupo
    if clase.cupo_disponible > 0:
        return jsonify({"status": "error", "message": "La clase aún tiene cupos disponibles. Intenta reservar directamente."}), 400

    # REGLA 1 y ESCENARIO 2: Validar si el usuario ya está esperando
    existente = ListaEspera.query.filter_by(clase_id=clase_id, usuario_id=usuario_id, estado='en_espera').first()
    if existente:
        return jsonify({"status": "error", "message": "Ya te encuentras en espera para este turno."}), 400

    try:
        # Calcular la última posición en la cola para esta clase
        ultima_posicion = db.session.query(db.func.max(ListaEspera.posicion)).filter_by(clase_id=clase_id).scalar() or 0
        nueva_posicion = ultima_posicion + 1

        nueva_espera = ListaEspera(
            clase_id=clase_id,
            usuario_id=usuario_id,
            posicion=nueva_posicion
        )
        db.session.add(nueva_espera)
        db.session.commit()

        # NOTA SOBRE LAS SUB-LISTAS: 
        # La separación visual entre Abonados y No Abonados se resolverá dinámicamente
        # cuando el sistema libere un cupo (se consulta la propiedad `is_abonado_actual` del modelo Usuario).

        return jsonify({"status": "success", "message": "Te has unido a la lista de espera correctamente."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    # ==========================================
# ENDPOINT: Confirmación y Pago (Con Límite de Tiempo)
# ==========================================
@lista_espera_bp.route('/<int:inscripcion_id>/confirmar', methods=['POST'])
def confirmar_lugar_espera(inscripcion_id):
    user_id = request.headers.get('X-User-Id')
    
    inscripcion = db.session.get(ListaEspera, inscripcion_id)
    if not inscripcion or str(inscripcion.usuario_id) != str(user_id):
        return jsonify({"status": "error", "message": "Inscripción no encontrada o no autorizada"}), 404

    if inscripcion.estado != 'notificado':
        return jsonify({"status": "error", "message": "Esta inscripción no está pendiente de confirmación"}), 400

    ahora = datetime.now()
    limite = inscripcion.fecha_notificacion + timedelta(minutes=60)

    # Buscamos la reserva pendiente que le generó el Helper
    reserva = Reserva.query.filter_by(clase_id=inscripcion.clase_id, usuario_id=user_id, estado='pendiente_pago').first()

    # ESCENARIO 2: Expiró el tiempo
    if ahora > limite:
        inscripcion.estado = 'expirado'
        if reserva:
            reserva.estado = 'cancelada_centro' # Anulamos su reserva pendiente
        db.session.commit()
        
        # Cedemos el lugar: El sistema gira la rueda y llama al siguiente en la fila
        procesar_lista_espera_al_cancelar(inscripcion.clase_id, user_id)
        
        return jsonify({"status": "error", "message": "El tiempo ha expirado y la reserva ha sido cedida al siguiente interesado."}), 400

    # ESCENARIO 1: Dentro del tiempo (Éxito)
    try:
        # Simulamos la confirmación del pago
        if reserva:
            reserva.estado = 'confirmada'
            reserva.monto_pagado = reserva.monto_total # Simulamos pago completo
        
        inscripcion.estado = 'confirmado'
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Pago exitoso. Turno confirmado formalmente."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# ENDPOINT: Estadísticas para el Administrador
# ==========================================
@lista_espera_bp.route('/estadisticas/<int:clase_id>', methods=['GET'])
def estadisticas_espera(clase_id):
    user_role = request.headers.get('X-User-Role')
    if user_role != 'admin':
        return jsonify({"status": "error", "message": "No autorizado. Vista exclusiva para Administradores."}), 403

    esperando = ListaEspera.query.filter_by(clase_id=clase_id, estado='en_espera').all()
    
    abonados = 0
    no_abonados = 0
    
    for insc in esperando:
        user = db.session.get(Usuario, insc.usuario_id)
        if user.is_abonado_actual:
            abonados += 1
        else:
            no_abonados += 1

    return jsonify({
        "status": "success",
        "estadisticas": {
            "total_general": len(esperando),
            "abonados": abonados,
            "no_abonados": no_abonados
        }
    }), 200

# NOTA: la reasignación de cupo (procesar_lista_espera_al_cancelar) vive
# ÚNICAMENTE en helpers/espera_helper.py y se usa vía el import de la línea 5.
# Antes había una segunda función con el mismo nombre definida acá abajo,
# que pisaba a la del helper y usaba un campo inexistente (fecha_solicitud),
# provocando el 500. Se eliminó para evitar que esto vuelva a pasar.
# Esa función del helper además crea la Notificacion correspondiente
# ("¡Se liberó un cupo!..."), así que no hace falta duplicarla acá.


# 1. 🕒 RUTA MÁGICA: VIAJAR EN EL TIEMPO
@lista_espera_bp.route('/viajar-tiempo', methods=['POST'])
def viajar_tiempo():
    # Buscamos a los que están notificados (esperando confirmar su lugar)
    pendientes = ListaEspera.query.filter_by(estado='notificado').all()
    
    if not pendientes:
        return jsonify({"message": "No hay nadie pendiente de pago para avanzar el tiempo."}), 400
        
    for p in pendientes:
        # Los marcamos como expirados
        p.estado = 'expirado'

        # Anulamos la reserva pendiente que le había generado el helper al notificarlo
        # (si no hacemos esto, la reserva le queda "viva" aunque perdió su turno)
        reserva_pendiente = Reserva.query.filter_by(
            clase_id=p.clase_id, usuario_id=p.usuario_id, estado='pendiente_pago'
        ).first()
        if reserva_pendiente:
            reserva_pendiente.estado = 'cancelada_centro'

        # Creamos la notificación de "perdiste tu turno"
        db.session.add(Notificacion(
            usuario_id=p.usuario_id, 
            mensaje="Tu tiempo expiró. El lugar pasó al siguiente en la fila."
        ))
        
        # Y acá llamás de nuevo a la función de procesar lista para que le dé el lugar al siguiente
        procesar_lista_espera_al_cancelar(p.clase_id, p.usuario_id)
        
    db.session.commit()
    return jsonify({"message": "Viaje en el tiempo exitoso"}), 200


# 2. 🔔 RUTA DE NOTIFICACIONES (Sin crear tablas nuevas)
@lista_espera_bp.route('/notificaciones', methods=['GET'])
def get_notificaciones():
    user_id = request.headers.get('X-User-Id')
    notas = Notificacion.query.filter_by(usuario_id=user_id, leida=False).all()
    return jsonify([{"id": n.id, "mensaje": n.mensaje} for n in notas]), 200