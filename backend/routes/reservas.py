from flask import Blueprint, request, jsonify
from models import db, Reserva, Clase, Turno, Actividad, Usuario

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('', methods=['POST'])
def crear_reserva():
    data = request.get_json()
    usuario = data.get('usuario_id')
    clase_seleccionada = data.get('clase_id')
    metodo_pago = data.get('metodo_pago')


    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404
    if not clase_seleccionada:
        return jsonify({"status": "error", "message": "Clase no encontrada"}), 404
    
    clase = db.session.get(Clase, clase_seleccionada)
    turno = db.session.get(Turno, clase.turno_id)
    actividad = db.session.get(Actividad, turno.actividad_id)
    monto_total = actividad.precio_base


    try:
        nueva_reserva = Reserva(
            clase_id=clase_seleccionada,
            usuario_id=usuario,
            metodo_pago=metodo_pago,
            monto_total=monto_total,
            estado='pendiente_pago'
        )
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

    if str(reserva.usuario_id) != user_id:
        return jsonify({"error": "La reserva especificada no existe"}), 404
    
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
        reservas = Reserva.query.filter(Reserva.usuario_id == user_id).all()
        
        resultado = []
        for r in reservas:
            clase = db.session.get(Clase, r.clase_id)
            turno = db.session.get(Turno, clase.turno_id)
            actividad = db.session.get(Actividad, turno.actividad_id)
            
            resultado.append({
                "nombre_actividad" : actividad.nombre,
                "dia_actividad" : turno.dia_semana,
                "horario_inicio" : str(turno.horario_inicio),
                "horario_fin" : str(turno.horario_fin),
                "estado" : r.estado
                            })

        return jsonify({"status": "success", "reservas": resultado}), 200
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500