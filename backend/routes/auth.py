import re  # Para validar el carácter especial exigido por el SRS
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, Usuario, Administrador

# Creamos el Blueprint para Autenticación
auth_bp = Blueprint('auth', __name__)

# -----------------------------------------------------------------
# 1. ENDPOINT: REGISTRAR USUARIO 
# -----------------------------------------------------------------
@auth_bp.route('/registro', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    
    # Extraer datos del JSON enviado por el cliente
    nombre = datos.get('nombre')
    apellido = datos.get('apellido')
    dni = datos.get('dni')
    email = datos.get('email')
    password = datos.get('password')
    fecha_nacimiento_str = datos.get('fecha_nacimiento') # Formato esperado: 'YYYY-MM-DD'

    # Validación de campos obligatorios
    if not all([nombre, apellido, dni, email, password, fecha_nacimiento_str]):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"}), 400

    # REGLA DEL SRS: Contraseña mínimo 6 caracteres
    if len(password) < 6:
        return jsonify({"status": "error", "message": "La contraseña debe tener al menos 6 caracteres"}), 400

    # REGLA DEL SRS: Debe incluir al menos un carácter especial (ej: !, @, #, etc.)
    if not re.search(r"[^a-zA-Z0-9]", password):
        return jsonify({
            "status": "error", 
            "message": "La contraseña debe incluir al menos un carácter especial"
        }), 400

    try:
        # Convertir el texto de la fecha a un formato de fecha real para Python
        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
        
        # REGLA DEL SRS: Validar Mayoría de Edad (Exigido por Mercado Pago)
        hoy = datetime.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad < 18:
            return jsonify({
                "status": "error", 
                "message": "Debes ser mayor de edad para registrarte "
            }), 400

    except ValueError:
        return jsonify({"status": "error", "message": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400

    # Validar que el Email no exista previamente
    usuario_existente_email = Usuario.query.filter(Usuario.email == email).first()
    if usuario_existente_email:
        return jsonify({"status": "error", "message": "El Email ya se encuentra registrado"}), 400

    # Validar que el DNI no exista previamente
    usuario_existente_dni = Usuario.query.filter(Usuario.dni == dni).first()
    if usuario_existente_dni:
        return jsonify({"status": "error", "message": "El DNI ya se encuentra registrado"}), 400
    try:
        # Encriptar la contraseña antes de guardarla (Seguridad básica)
        hash_encriptado = generate_password_hash(password)

        # Creamos la instancia según el modelo físico limpio de Nico
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            email=email,
            password_hash=hash_encriptado,
            fecha_nacimiento=fecha_nacimiento,
            activo=True # Alta lógica inicial
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "¡Usuario registrado con éxito en Sportify!"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error en el servidor al registrar: {str(e)}"
        }), 500


# -----------------------------------------------------------------
# 2. ENDPOINT: LOGIN 
# -----------------------------------------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Usuario.query.filter_by(email=email).first()
    
    # 1. Comprobamos si las credenciales coinciden usando check_password_hash
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401
        
    # 2. Buscamos si existe en la tabla de administradores
    admin_profile = Administrador.query.filter_by(usuario_id=user.id).first()
    
    # 3. SI ES ADMIN: Respondemos con éxito y le mandamos el objeto administrador para React
    if admin_profile:
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "administrador": { "id": admin_profile.id } # Esto activa la vista de Nico en React
            }
        }), 200
        
    # 4. SI NO ES ADMIN (O sea, es un cliente común): ¡También respondemos con éxito!
    else:
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "administrador": None # Al ser None, activa tu vista de InicioCliente en React
            }
        }), 200