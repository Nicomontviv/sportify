from flask import Blueprint, request, jsonify
from models import Usuario, Administrador

# Creamos el Blueprint para Autenticación
auth_bp = Blueprint('auth', __name__)

# CORRECCIÓN: Dejamos SOLAMENTE el decorador del blueprint
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Usuario.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401
        
    admin_profile = Administrador.query.filter_by(usuario_id=user.id).first()
    
    if admin_profile:
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "role": "admin"
            }
        }), 200
    else:
        return jsonify({"status": "error", "message": "Acceso denegado. No sos administrador."}), 403