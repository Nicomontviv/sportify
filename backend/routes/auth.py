import re  # Para validar el carácter especial exigido por el SRS
import os 
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import current_app
from extensions import mail  # ← poné esto
from models import db, Usuario, Administrador, Empleado

# Creamos el Blueprint para Autenticación
auth_bp = Blueprint('auth', __name__)
  
from itsdangerous import URLSafeTimedSerializer

# Agregá esta función helper arriba, antes de los endpoints
def generar_token(email):
    s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'sportify-secret'))
    return s.dumps(email, salt='recuperar-password')

def verificar_token(token, expiracion=3600):
    s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'sportify-secret'))
    try:
        email = s.loads(token, salt='recuperar-password', max_age=expiracion)
        return email
    except:
        return None

# -----------------------------------------------------------------
# ENDPOINT: RECUPERAR CONTRASEÑA
# -----------------------------------------------------------------
@auth_bp.route('/recuperar-password', methods=['POST'])
def recuperar_password():
    datos = request.get_json()
    email = datos.get('email')

    if not email:
        return jsonify({"status": "error", "message": "El email es obligatorio"}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    # Por seguridad, siempre respondemos igual aunque el email no exista
    if usuario:
        token = generar_token(email)
        link = f"http://localhost:5174/nueva-password?token={token}"

        try:
            from extensions import mail
            from flask_mail import Message

            msg = Message(
                subject="Recuperá tu contraseña - Sportify",
                recipients=[email],
                body=f"""
Hola {usuario.nombre},

Recibimos una solicitud para recuperar tu contraseña en Sportify.

Hacé clic en el siguiente link para crear una nueva contraseña:
{link}

Este link expira en 1 hora.

Si no solicitaste esto, ignorá este mail.

El equipo de Sportify
                """
            )
            mail.send(msg)
        except Exception as e:
            print(f"Error al enviar mail: {e}")

    return jsonify({
        "status": "success",
        "message": "Si el email existe, te enviamos las instrucciones."
    }), 200

# -----------------------------------------------------------------
# ENDPOINT: NUEVA CONTRASEÑA
# -----------------------------------------------------------------
@auth_bp.route('/nueva-password', methods=['POST'])
def nueva_password():
    datos = request.get_json()
    token = datos.get('token')
    password = datos.get('password')

    if not token or not password:
        return jsonify({"status": "error", "message": "Token y contraseña son obligatorios"}), 400

    email = verificar_token(token)
    if not email:
        return jsonify({"status": "error", "message": "El link expiró o es inválido"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "La contraseña debe tener al menos 6 caracteres"}), 400

    if not re.search(r"[^a-zA-Z0-9]", password):
        return jsonify({"status": "error", "message": "La contraseña debe incluir al menos un carácter especial"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    try:
        usuario.password_hash = generate_password_hash(password)
        db.session.commit()
        return jsonify({"status": "success", "message": "Contraseña actualizada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al actualizar: {str(e)}"}), 500
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

        try:
            print(f"Enviando mail a: {email}")  # ← agregá esto
            from extensions import mail
            from flask_mail import Message

            msg = Message(
                subject="¡Bienvenido a Sportify!",
                recipients=[email],
                body=f"""
Hola {nombre} {apellido},

¡Tu registro en Sportify fue exitoso!

Ya podés iniciar sesión con tu email: {email}

¡Nos vemos en el centro!
El equipo de Sportify
                """
            )
            mail.send(msg)
            print("Mail enviado OK")  # ← y esto

        except Exception as mail_error:
            print(f"Error al enviar mail: {mail_error}")

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

    #Buscamos si existe en la tabla de empleados
    empleado_profile = Empleado.query.filter_by(usuario_id=user.id).first()
    
    # 3. SI ES ADMIN: Respondemos con éxito y le mandamos el objeto administrador para React
    if admin_profile:
        # Si es admin, devolvemos el perfil de administrador 
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "administrador": { "id": admin_profile.id }
            }
        }), 200

    # NUEVO: Si no es admin pero es empleado, devolvemos el perfil de empleado
    elif empleado_profile:
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "administrador": None,  
                "empleado": { "id": empleado_profile.id }  
            }
        }), 200

    # 4. SI NO ES ADMIN NI EMPLEADO (O sea, es un cliente común): 
    else:
        # Si no es admin ni empleado, es un cliente común 
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "administrador": None
            }
        }), 200
    
# -----------------------------------------------------------------
# ENDPOINT: MODIFICAR PERFIL
# -----------------------------------------------------------------
@auth_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def modificar_perfil(usuario_id):
    datos = request.get_json()

    nombre = datos.get('nombre')
    apellido = datos.get('apellido')
    email = datos.get('email')
    fecha_nacimiento_str = datos.get('fecha_nacimiento')
    password = datos.get('password')

    if not all([nombre, apellido, email, fecha_nacimiento_str]):
        return jsonify({"status": "error", "message": "Todos los campos son obligatorios"}), 400

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    email_cambiado = email != usuario.email

    # Regla 1: email único
    if email_cambiado:
        existente = Usuario.query.filter(Usuario.email == email, Usuario.id != usuario_id).first()
        if existente:
            return jsonify({"status": "error", "message": "El email ya está registrado por otro usuario"}), 400

    # Validar contraseña si se quiere cambiar
    if password:
        if len(password) < 6:
            return jsonify({"status": "error", "message": "La contraseña debe tener al menos 6 caracteres"}), 400
        if not re.search(r"[^a-zA-Z0-9]", password):
            return jsonify({"status": "error", "message": "La contraseña debe incluir al menos un carácter especial"}), 400

    try:
        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
        hoy = datetime.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad < 18:
            return jsonify({"status": "error", "message": "Debes ser mayor de edad"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Formato de fecha inválido"}), 400

    try:
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.fecha_nacimiento = fecha_nacimiento

        if password:
            usuario.password_hash = generate_password_hash(password)

        # Regla 2: si cambió el email, enviamos confirmación y NO lo actualizamos todavía
        if email_cambiado:
            token = generar_token(email)
            link = f"http://localhost:5173/confirmar-email?token={token}&usuario_id={usuario_id}"
            try:
                from extensions import mail
                from flask_mail import Message
                msg = Message(
                    subject="Confirmá tu nuevo email - Sportify",
                    recipients=[email],
                    body=f"""
Hola {nombre},

Recibimos una solicitud para cambiar tu email en Sportify.

Hacé clic en el siguiente link para confirmar tu nuevo email:
{link}

Este link expira en 1 hora. Si no solicitaste esto, ignorá este mail.

El equipo de Sportify
                    """
                )
                mail.send(msg)
            except Exception as e:
                print(f"Error al enviar mail: {e}")
        else:
            usuario.email = email

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Perfil actualizado correctamente.",
            "email_cambiado": email_cambiado
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al actualizar: {str(e)}"}), 500
# -----------------------------------------------------------------
# ENDPOINT: CONFIRMAR NUEVO EMAIL
# -----------------------------------------------------------------
@auth_bp.route('/confirmar-email', methods=['GET'])
def confirmar_email():
    token = request.args.get('token')
    usuario_id = request.args.get('usuario_id')

    if not token or not usuario_id:
        return jsonify({"status": "error", "message": "Token o usuario inválido"}), 400

    email = verificar_token(token)
    if not email:
        return jsonify({"status": "error", "message": "El link expiró o es inválido"}), 400

    usuario = Usuario.query.get(int(usuario_id))
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    # Verificar que el email no lo haya tomado otro usuario mientras tanto
    existente = Usuario.query.filter(Usuario.email == email, Usuario.id != usuario.id).first()
    if existente:
        return jsonify({"status": "error", "message": "El email ya está registrado por otro usuario"}), 400

    try:
        usuario.email = email
        db.session.commit()
        # Redirigimos al login con mensaje de éxito
        return '''
            <html>
            <body style="font-family:sans-serif;text-align:center;padding:50px">
                <h2 style="color:#1E90FF">✅ Email confirmado</h2>
                <p>Tu nuevo email fue actualizado correctamente en Sportify.</p>
                <a href="http://localhost:5173" style="color:#1E90FF">Ir al inicio</a>
            </body>
            </html>
        ''', 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al confirmar: {str(e)}"}), 500