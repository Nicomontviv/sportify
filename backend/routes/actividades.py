from flask import Blueprint, request, jsonify
from models import db, Actividad, Turno, Reserva, Usuario,Administrador, Clase
from helpers.turnos_helper import dar_de_baja_turno_y_clases

# Creamos el Blueprint para Actividades
actividades_bp = Blueprint('actividades', __name__)
 
@actividades_bp.route('', methods=['GET'])
def obtener_actividades():
    try:
        actividades = Actividad.query.all()
        return jsonify({
            "status": "success",
            "actividades": [{
                "id": a.id,
                "nombre": a.nombre,
                "descripcion": a.descripcion,
                "precio_base": float(a.precio_base),
                "activa": a.activa
            } for a in actividades]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
 
 
@actividades_bp.route('', methods=['POST'])
def crear_actividad():
    # Le pedimos al frontend el ID del usuario que intenta crear la actividad
    user_id = request.headers.get('X-User-Id')
    if user_id:
        user_id = int(user_id)
    print("====================================")
    print(f"VALOR RECIBIDO DESDE REACT: {user_id}")
    print(f"TIPO DE DATO: {type(user_id)}")
    print("====================================")
    # Verificamos en la base de datos si ese ID de usuario es administrador
    es_admin = Administrador.query.filter_by(usuario_id=user_id).first()
    
    if not es_admin:
        return jsonify({"status": "error", "message": "No autorizado. No sos administrador."}), 403
 
    data = request.get_json()
    nombre_ingresado = data.get('nombre')
    precio_ingresado = data.get('precio_base')
    descripcion_ingresada = data.get('descripcion', '')
 
    if not nombre_ingresado or not precio_ingresado:
        return jsonify({"status": "error", "message": "Faltan campos obligatorios"}), 400
 
    actividad_existente = Actividad.query.filter_by(nombre=nombre_ingresado).first()
    if actividad_existente:
        return jsonify({"status": "error", "message": "La actividad ya se encuentra registrada"}), 400
 
    try:
        nueva_actividad = Actividad(
            nombre=nombre_ingresado,
            precio_base=float(precio_ingresado),
            descripcion=descripcion_ingresada,
            activa=True
        )
        db.session.add(nueva_actividad)
        db.session.commit()
        return jsonify({"status": "success", "message": "Actividad creada correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
 
 
@actividades_bp.route('/<int:id>', methods=['PUT'])
def modificar_actividad(id):
    user_role = request.headers.get('X-User-Role')
    if user_role != 'admin':
        return jsonify({"status": "error", "message": "No autorizado"}), 403
 
    actividad = db.session.get(Actividad, id)
    if not actividad:
        return jsonify({"status": "error", "message": "Actividad no encontrada"}), 404
 
    # REGLA DE NEGOCIO: No se puede modificar una actividad inactiva
    if not actividad.activa:
        return jsonify({"status": "error", "message": "No se puede modificar una actividad eliminada"}), 400
 
    data = request.get_json()
    nuevo_nombre = data.get('nombre')
    nuevo_precio = data.get('precio_base')
    nueva_descripcion = data.get('descripcion', '')
 
    duplicada = Actividad.query.filter(Actividad.nombre == nuevo_nombre, Actividad.id != id).first()
    if duplicada:
        return jsonify({"status": "error", "message": "La actividad ya se encuentra registrada"}), 400
 
    try:
        actividad.nombre = nuevo_nombre
        actividad.precio_base = float(nuevo_precio)
        actividad.descripcion = nueva_descripcion
        db.session.commit()
        return jsonify({"status": "success", "message": "Actividad modificada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
 
 
@actividades_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_actividad(id):
    user_role = request.headers.get('X-User-Role')
    if user_role != 'admin':
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    actividad = db.session.get(Actividad, id)
    if not actividad:
        return jsonify({"status": "error", "message": "Actividad no encontrada"}), 404

    try:
        actividad.activa = False
        turnos_asociados = Turno.query.filter_by(actividad_id=id, activo=True).all()

        total_clases = 0
        total_con_reservas = 0
        for turno in turnos_asociados:
            detalle = dar_de_baja_turno_y_clases(turno)
            total_clases += detalle["clases_futuras_dadas_de_baja"]
            total_con_reservas += detalle["clases_con_reservas_canceladas"]

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Actividad eliminada correctamente",
            "detalles": {
                "turnos_afectados": len(turnos_asociados),
                "clases_dadas_de_baja": total_clases,
                "clases_con_reservas": total_con_reservas
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500