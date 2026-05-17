from flask import Blueprint, request, jsonify
from models import db, Actividad, Turno, Reserva, Usuario
 
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
    user_role = request.headers.get('X-User-Role')
    if user_role != 'admin':
        return jsonify({"status": "error", "message": "No autorizado"}), 403
 
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
 
    actividad = Actividad.query.get(id)
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
 
    actividad = Actividad.query.get(id)
    if not actividad:
        return jsonify({"status": "error", "message": "Actividad no encontrada"}), 404
 
    # 1. Baja lógica de la actividad
    actividad.activa = False
 
    # 2. Buscar y deshabilitar todos sus turnos asociados
    turnos_asociados = Turno.query.filter_by(actividad_id=id).all()
 
    usuarios_afectados_notificados = []
    reembolsos_aplicados = 0
 
    for turno in turnos_asociados:
        turno.activo = False
 
        # REGLA DE NEGOCIO: Cancelar reservas confirmadas o con pago pendiente
        # BUG CORREGIDO: estado='pagada' no existe en el ENUM → buscar 'confirmada' y 'pendiente_pago'
        reservas_activas = Reserva.query.filter(
            Reserva.turno_id == turno.id,
            Reserva.estado.in_(['confirmada', 'pendiente_pago'])
        ).all()
 
        for reserva in reservas_activas:
            # BUG CORREGIDO: estado='cancelada' no existe → usar 'cancelada_centro'
            reserva.estado = 'cancelada_centro'
            
            # REFUERZO 1: Usar db.session.get en lugar de Query.get
            user_afectado = db.session.get(Usuario, reserva.usuario_id)
 
            if user_afectado:
                tipo_cliente = "Abonado" if user_afectado.is_abonado_actual else "Casual"
                
                # REFUERZO 2: Agregar "or 0.0" previene que float() rompa el código si la DB devuelve NULL
                monto_devuelto = float(reserva.monto_pagado or 0.0)
                reembolsos_aplicados += monto_devuelto
 
                usuarios_afectados_notificados.append({
                    "usuario": f"{user_afectado.nombre} {user_afectado.apellido}",
                    "tipo": tipo_cliente,
                    "detalle": f"Devolución de seña de ${monto_devuelto:.2f} acreditada."
                })
 
    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Actividad eliminada correctamente",
            "detalles_demo": {
                "turnos_afectados": len(turnos_asociados),
                "reembolsos_totales": reembolsos_aplicados,
                "notificaciones": usuarios_afectados_notificados
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500