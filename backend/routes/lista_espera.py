from flask import Blueprint, request, jsonify
from models import db, Clase, ListaEspera, Usuario

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