from flask import Blueprint, request, jsonify
from models import db, Reserva, Clase, Turno, Usuario
from datetime import datetime, timedelta

asistencia_bp = Blueprint('asistencia', __name__)

# Tolerancia: se puede marcar asistencia desde 10 min antes del inicio
# hasta el horario de fin de la clase.
TOLERANCIA_INGRESO = timedelta(minutes=10)


def _validar_reserva(reserva_id):
    """
    Corre toda la cadena de validación sobre una reserva.
    Devuelve una tupla (titular_dict, error_dict, status_code).
    - Si todo OK: (datos, None, 200)
    - Si falla algo: (None, {"status": "error", "message": ...}, codigo)
    """
    # 1. La reserva debe existir
    reserva = db.session.get(Reserva, reserva_id)
    if not reserva:
        return None, {"status": "error", "message": "No existe una reserva con ese número"}, 404

    # 2. No puede estar cancelada
    if reserva.estado in ('cancelada_usuario', 'cancelada_centro'):
        return None, {"status": "error", "message": "La reserva está cancelada"}, 409

    # 3. No puede haber registrado asistencia ya (frena reutilización del QR)
    if reserva.estado == 'asistio':
        return None, {"status": "error", "message": "Esta reserva ya registró asistencia"}, 409

    # 4. Debe estar paga en su totalidad (estado confirmada)
    if reserva.estado != 'confirmada':
        return None, {"status": "error", "message": "La reserva no está paga en su totalidad"}, 409

    # 5. La clase debe existir y estar activa
    clase = db.session.get(Clase, reserva.clase_id)
    if not clase or not clase.activo:
        return None, {"status": "error", "message": "La clase no está disponible"}, 409

    turno = db.session.get(Turno, clase.turno_id)
    inicio_clase = datetime.combine(clase.fecha, turno.horario_inicio)
    fin_clase = datetime.combine(clase.fecha, turno.horario_fin)
    ahora = datetime.now()

    # 6. Todavía falta para el horario de ingreso
    if ahora < inicio_clase - TOLERANCIA_INGRESO:
        return None, {"status": "error", "message": "Todavía no es horario de ingreso para esta clase"}, 409

    # 7. La clase ya finalizó
    if ahora > fin_clase:
        return None, {"status": "error", "message": "La clase ya finalizó"}, 409

    # 8. Pasó todo: armamos los datos del titular para que el empleado
    #    compare el DNI mostrado con el físico antes de confirmar
    usuario = db.session.get(Usuario, reserva.usuario_id)

    titular = {
        "reserva_id": reserva.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "dni": usuario.dni,
        "actividad": turno.actividad.nombre,
        "fecha": str(clase.fecha),
        "horario_inicio": str(turno.horario_inicio),
        "horario_fin": str(turno.horario_fin),
    }
    return titular, None, 200


# GET: busca la reserva por número (manual o QR), valida y devuelve el titular
@asistencia_bp.route('/<int:id>', methods=['GET'])
def consultar_asistencia(id):
    titular, error, codigo = _validar_reserva(id)
    if error:
        return jsonify(error), codigo
    return jsonify({"status": "success", "titular": titular}), codigo


# PUT: re-valida todo de nuevo y, si pasa, marca asistio.
# No confía en el front: revalida la cadena completa antes de escribir.
@asistencia_bp.route('/<int:id>', methods=['PUT'])
def marcar_asistencia(id):
    titular, error, codigo = _validar_reserva(id)
    if error:
        return jsonify(error), codigo

    reserva = db.session.get(Reserva, id)
    try:
        reserva.estado = 'asistio'
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Asistencia registrada correctamente",
            "titular": titular
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500