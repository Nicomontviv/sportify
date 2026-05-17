import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, Usuario, Administrador, Actividad

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------------------------------------------------------
# 1. ENDPOINT DE INICIO DE SESIÓN (LOGIN)
# ------------------------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password') # En producción usaría bcrypt, para la demo validamos directo

    user = Usuario.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401
        
    # Verificar si el usuario está registrado en la tabla de administradores
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

# ------------------------------------------------------------
# 2. ENDPOINT: ALTA DE ACTIVIDAD (REQUERIMIENTO HU)
# ------------------------------------------------------------
@app.route('/api/actividades', methods=['POST'])
def crear_actividad():
    # Simulación de verificación de autenticación mediante Headers para la Demo
    user_role = request.headers.get('X-User-Role')
    if user_role != 'admin':
        return jsonify({"status": "error", "message": "No autorizado"}), 403

    data = request.get_json()
    nombre_ingresado = data.get('nombre')
    precio_ingresado = data.get('precio_base')
    descripcion_ingresada = data.get('descripcion', '')

    if not nombre_ingresado or not precio_ingresado:
        return jsonify({"status": "error", "message": "Faltan campos obligatorios"}), 400

    # REGLA DE NEGOCIO 1: El nombre de la actividad debe ser único en el sistema
    actividad_existente = Actividad.query.filter_by(nombre=nombre_ingresado).first()
    if actividad_existente:
        # ESCENARIO 2: Mensaje exacto solicitado
        return jsonify({"status": "error", "message": "La actividad ya se encuentra registrada"}), 400

    try:
        nueva_actividad = Actividad(
            nombre=nombre_ingresado,
            precio_base=float(precio_ingresado),
            descripcion=descripcion_ingresada,
            activa=True # Estado activo por defecto (Escenario 1)
        )
        db.session.add(nueva_actividad)
        db.session.commit()
        
        # ESCENARIO 1: Alta exitosa con mensaje exacto
        return jsonify({
            "status": "success", 
            "message": "Actividad creada correctamente",
            "actividad": {
                "id": nueva_actividad.id,
                "nombre": nueva_actividad.nombre,
                "precio_base": float(nueva_actividad.precio_base)
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)