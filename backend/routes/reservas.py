from flask import Blueprint, request, jsonify
from models import Credito, db, Reserva, Clase, Turno, Actividad, Usuario
from datetime import date, datetime, timedelta

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('', methods=['POST'])
def crear_reserva():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    clase_id = data.get('clase_id')
    metodo_pago = data.get('metodo_pago')

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    
    clase_seleccionada = db.session.get(Clase, clase_id)
    if not clase_seleccionada:
        return jsonify({"status": "error", "message": "Clase no encontrada"}), 404
    
    # REGLA DE NEGOCIO: La clase debe tener cupo disponible antes de ser reservada
    if clase_seleccionada.cupo_disponible <= 0:
        return jsonify({"status": "error", "message": "La clase no posee cupos disponibles"}), 409
    
    turno = db.session.get(Turno, clase_seleccionada.turno_id)
    actividad = db.session.get(Actividad, turno.actividad_id)
    monto_total = actividad.precio_base

    nueva_reserva = Reserva(
            clase_id=clase_id,
            usuario_id=usuario_id,
            metodo_pago=metodo_pago,
            monto_total=monto_total,
            estado='pendiente_pago' # Toda reserva empieza sin pago confirmado; cambia al procesar el pago
        )

    # Si el usuario es un abonado se le aplica el descuento correspondiente sobre el monto final
    if usuario.is_abonado_actual:
        ahora = datetime.now()
        credito_usuario = Credito.query.filter(Credito.usuario_id == usuario_id, Credito.anio == ahora.year, Credito.mes == ahora.month).first()
        if not credito_usuario:
            return jsonify({"status": "error", "message": "Credito no encontrado"}), 404
        
        monto_total -=  monto_total * credito_usuario.monto_descuento / 100
        nueva_reserva.monto_total = monto_total
        nueva_reserva.monto_pagado = monto_total
        nueva_reserva.estado = 'confirmada'

    else:
        nueva_reserva.monto_pagado = monto_total / 2


    try:
        db.session.add(nueva_reserva)
        db.session.commit()
        return jsonify({"status": "success", "message": "Reserva creada correctamente"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
@reservas_bp.route('/<int:id>', methods=['PUT'])
def cancelar_reserva(id):
    user_id = request.headers.get('X-User-Id')
    
    reserva = db.session.get(Reserva, id)
    if not reserva:
        return jsonify({"status": "error", "message": "Reserva no encontrada"}), 404

    if str(reserva.usuario_id) != user_id: #Preguntar tipo de error
        return jsonify({"error": "La reserva especificada no existe"}), 404
    
    # No se debe cancelar un reserva ya cancelada
    if reserva.estado == 'cancelada_usuario' or reserva.estado == 'cancelada_centro':
        return jsonify({"error": "La reserva ya se encuentra cancelada"}), 409
    
    try:
        reserva.estado='cancelada_usuario'
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "La reserva se cancelo con exito"
            }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    

@reservas_bp.route('/<int:user_id>', methods=['GET'])
def ver_reservas(user_id):
    try:
        # Solo mostramos reservas activas, las canceladas no le sirven al usuario
        reservas = Reserva.query.filter(Reserva.usuario_id == user_id).all()
        
        resultado = []
        for r in reservas:
            clase = db.session.get(Clase, r.clase_id)
            if clase.fecha > date.today():
                turno = db.session.get(Turno, clase.turno_id)
                inicio_clase = datetime.combine(clase.fecha, turno.horario_inicio)
                limite_cancelacion = inicio_clase - timedelta(hours=1)
                if datetime.now() > limite_cancelacion:
                    actividad = db.session.get(Actividad, turno.actividad_id)
                    
                    if r.estado != 'cancelada_usuario' and r.estado != 'cancelada_centro':
                        resultado.append({
                            "nombre_actividad" : actividad.nombre,
                            "dia_actividad" : turno.dia_semana,
                            "horario_inicio" : str(turno.horario_inicio),
                            "horario_fin" : str(turno.horario_fin),
                            "fecha": str(clase.fecha),
                            "estado" : r.estado
                                        })

        return jsonify({"status": "success", "reservas": resultado}), 200
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500