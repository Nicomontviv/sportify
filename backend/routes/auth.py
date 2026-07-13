import re  # Para validar el carácter especial exigido por el SRS
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from models import db, Usuario, Administrador, Empleado, Credito
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
# Creamos el Blueprint para Autenticación
auth_bp = Blueprint('auth', __name__)

# Clave secreta para firmar los tokens de recuperación y confirmación
CLAVE_SECRETA_TOKEN = "sportify-recuperacion-2026"
serializer = URLSafeTimedSerializer(CLAVE_SECRETA_TOKEN)

def generar_token_recuperacion(email):
    """Genera un token único y lo guarda en la BD"""
    token = serializer.dumps(email, salt="recuperacion-contrasena")
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        usuario.token_recuperacion = token
        usuario.token_recuperacion_usado = False
        db.session.commit()
    return token

def verificar_token_recuperacion(token, max_age=3600):
    """Verifica el token y devuelve el email si es válido"""
    try:
        email = serializer.loads(token, salt="recuperacion-contrasena", max_age=max_age)
        return email
    except SignatureExpired:
        return None
    except BadSignature:
        return None


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

    # 2. Comprobamos que la cuenta no esté dada de baja
    if not user.activo:
        return jsonify({"status": "error", "message": "Esta cuenta está dada de baja"}), 403

    # 3. Buscamos si existe en la tabla de administradores
    admin_profile = Administrador.query.filter_by(usuario_id=user.id).first()

    # Buscamos si existe en la tabla de empleados
    empleado_profile = Empleado.query.filter_by(usuario_id=user.id).first()

    # 4. SI ES ADMIN: Respondemos con éxito y le mandamos el objeto administrador para React
    if admin_profile:
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "administrador": { "id": admin_profile.id }
            }
        }), 200

    # Si no es admin pero es empleado, devolvemos el perfil de empleado
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

    # SI NO ES ADMIN NI EMPLEADO (es un cliente común):
    else:
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "nombre": user.nombre,
                "administrador": None
            }
        }), 200

# -----------------------------------------------------------------
# ENDPOINT:  Obtener Usuario
# -----------------------------------------------------------------   

@auth_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_perfil(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    ahora = datetime.now()
    credito = Credito.query.filter_by(
        usuario_id=usuario.id,
        mes=ahora.month,
        anio=ahora.year
    ).first()

    return jsonify({
        "status": "success",
        "user": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "email": usuario.email,
            "dni": usuario.dni,
            "fecha_nacimiento": str(usuario.fecha_nacimiento),
            "credito": {
                "cancelaciones": credito.cancelaciones,
                "clases_a_favor": credito.clases_a_favor,
                "descuento_activo": credito.descuento_activo
            } if credito else None
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

        if email_cambiado:
            token = generar_token_recuperacion(email)
            link = f"http://localhost:5173/confirmar-email?token={token}&usuario_id={usuario_id}"
            print(f"[SIMULACIÓN MAIL] Link de confirmación de email para {email}: {link}")
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

    email = verificar_token_recuperacion(token)
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



# -----------------------------------------------------------------
# 3. ENDPOINT: DAR DE BAJA USUARIO (baja lógica por DNI)
# -----------------------------------------------------------------
@auth_bp.route('/baja-usuario', methods=['PUT'])
def baja_usuario():
    datos = request.get_json()
    dni = datos.get('dni')

    if not dni:
        return jsonify({"status": "error", "message": "El DNI es obligatorio"}), 400

    usuario = Usuario.query.filter_by(dni=dni).first()
    if not usuario:
        return jsonify({"status": "error", "message": "No existe un usuario con ese DNI"}), 404

    if not usuario.activo:
        return jsonify({"status": "error", "message": "El usuario ya está dado de baja"}), 400

    try:
    
        usuario.activo = False
        usuario.fecha_baja = datetime.now(timezone.utc)  # ⬅️ esta línea tiene que estar
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Usuario {usuario.nombre} {usuario.apellido} dado de baja correctamente"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al dar de baja: {str(e)}"}), 500

# -----------------------------------------------------------------
# 4. ENDPOINT: AUTO-BAJA (el usuario se da de baja a sí mismo)
# -----------------------------------------------------------------
@auth_bp.route('/baja-cuenta/<int:usuario_id>', methods=['PUT'])
def baja_cuenta(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    if not usuario.activo:
        return jsonify({"status": "error", "message": "La cuenta ya está dada de baja"}), 400

    try:
        usuario.activo = False  # Baja LÓGICA
        db.session.commit()
        return jsonify({"status": "success", "message": "Tu cuenta fue dada de baja correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al dar de baja: {str(e)}"}), 500


# -----------------------------------------------------------------
# ENDPOINT: REACTIVAR USUARIO (HU #62)
# -----------------------------------------------------------------
@auth_bp.route('/reactivar-usuario', methods=['PUT'])
def reactivar_usuario():
    datos = request.get_json()
    dni = datos.get('dni', '').strip()

    if not dni:
        return jsonify({"status": "error", "message": "Ingresá un DNI para buscar."}), 400

    if not re.match(r'^\d{8}$', dni):
        return jsonify({"status": "error", "message": "El DNI debe tener exactamente 8 dígitos numéricos."}), 400

    usuario = Usuario.query.filter_by(dni=dni).first()
    if not usuario:
        return jsonify({"status": "error", "message": "No existe un usuario con ese DNI."}), 404

    admin_profile = Administrador.query.filter_by(usuario_id=usuario.id).first()
    empleado_profile = Empleado.query.filter_by(usuario_id=usuario.id).first()
    if admin_profile or empleado_profile:
        return jsonify({"status": "error", "message": "No existe un usuario con ese DNI."}), 404

    if usuario.activo:
        return jsonify({"status": "error", "message": "El usuario ya está activo."}), 400

    try:
        usuario.activo = True
        db.session.commit()
        return jsonify({"status": "success", "message": "Usuario reactivado exitosamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al reactivar: {str(e)}"}), 500


# -----------------------------------------------------------------
# ENDPOINT: BUSCAR USUARIO PARA CERTIFICADO (HU #33)
# -----------------------------------------------------------------
@auth_bp.route('/empleado/buscar-usuario-certificado', methods=['POST'])
def buscar_usuario_certificado():
    from models import Certificado
    datos = request.get_json()
    dni = datos.get('dni', '').strip()

    if not dni:
        return jsonify({"status": "error", "message": "Ingresá un DNI para buscar."}), 400

    if not re.match(r'^\d{8}$', str(dni)):
        return jsonify({"status": "error", "message": "El DNI debe tener exactamente 8 dígitos numéricos."}), 400

    usuario = Usuario.query.filter_by(dni=str(dni)).first()
    if not usuario:
        return jsonify({"status": "error", "message": "El DNI ingresado no pertenece a un usuario del sistema."}), 404

    admin_profile = Administrador.query.filter_by(usuario_id=usuario.id).first()
    empleado_profile = Empleado.query.filter_by(usuario_id=usuario.id).first()
    if admin_profile or empleado_profile:
        return jsonify({"status": "error", "message": "El DNI ingresado no pertenece a un usuario del sistema."}), 404

    certificado_vigente = Certificado.query.filter_by(usuario_id=usuario.id, estado='vigente').first()
    if certificado_vigente:
        return jsonify({"status": "error", "message": "El usuario ya cuenta con un certificado vigente."}), 400

    return jsonify({
        "status": "encontrado",
        "usuario": {"nombre": usuario.nombre, "apellido": usuario.apellido}
    }), 200


# -----------------------------------------------------------------
# ENDPOINT: REGISTRAR CERTIFICADO (HU #33)
# -----------------------------------------------------------------
@auth_bp.route('/empleado/registrar-certificado', methods=['POST'])
def registrar_certificado():
    from models import Certificado
    datos = request.get_json()

    dni = datos.get('dni', '').strip()
    fecha_emision_str = datos.get('fecha_emision')
    fecha_vencimiento_str = datos.get('fecha_vencimiento')

    if not fecha_emision_str or not fecha_vencimiento_str:
        return jsonify({"status": "error", "message": "Las fechas son obligatorias."}), 400

    usuario = Usuario.query.filter_by(dni=str(dni)).first()
    if not usuario:
        return jsonify({"status": "error", "message": "El DNI ingresado no pertenece a un usuario del sistema."}), 404

    hoy = datetime.today().date()

    try:
        fecha_emision = datetime.strptime(fecha_emision_str, '%Y-%m-%d').date()
        fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"status": "error", "message": "Formato de fecha inválido."}), 400

    if fecha_vencimiento < fecha_emision:
        return jsonify({"status": "error", "message": "La fecha de vencimiento no puede ser anterior a la fecha de emisión."}), 400

    if fecha_vencimiento < hoy:
        return jsonify({"status": "error", "message": "El certificado está vencido, no se puede realizar la carga."}), 400

    try:
        nuevo_certificado = Certificado(
            usuario_id=usuario.id,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            estado='vigente'
        )
        db.session.add(nuevo_certificado)
        db.session.commit()
        return jsonify({"status": "success", "message": "Certificado registrado correctamente."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al registrar certificado: {str(e)}"}), 500


# -----------------------------------------------------------------
# ENDPOINT: SOLICITAR RECUPERACIÓN DE CONTRASEÑA (HU #32)
# -----------------------------------------------------------------
@auth_bp.route('/recuperar-contrasena', methods=['POST'])
def recuperar_contrasena():
    datos = request.get_json()
    email = datos.get('email', '').strip()

    if not email:
        return jsonify({"status": "error", "message": "El correo electrónico es obligatorio."}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"status": "error", "message": "El correo electrónico ingresado no corresponde a un usuario registrado."}), 404

    token = generar_token_recuperacion(email)
    link = f"http://localhost:5173/reset-password?token={token}"

    print(f"[SIMULACIÓN MAIL] Link de recuperación para {email}: {link}")

    return jsonify({
        "status": "success",
        "message": "Usá el link a continuación para restablecer tu contraseña:",
        "link_demo": link
    }), 200


# -----------------------------------------------------------------
# ENDPOINT: VERIFICAR TOKEN DE RECUPERACIÓN (HU #32)
# -----------------------------------------------------------------
@auth_bp.route('/verificar-token-recuperacion', methods=['POST'])
def verificar_token_recuperacion_endpoint():
    datos = request.get_json()
    token = datos.get('token', '').strip()

    if not token:
        return jsonify({"status": "error", "message": "El enlace de recuperación ha expirado."}), 400

    email = verificar_token_recuperacion(token)
    if not email:
        return jsonify({"status": "error", "message": "El enlace de recuperación ha expirado."}), 400

    usuario = Usuario.query.filter_by(email=email, token_recuperacion=token).first()
    if not usuario:
        return jsonify({"status": "error", "message": "El enlace de recuperación ha expirado."}), 400
    if usuario.token_recuperacion_usado:
        return jsonify({"status": "error", "message": "El enlace de recuperación ya fue utilizado."}), 400

    return jsonify({"status": "success"}), 200


# -----------------------------------------------------------------
# ENDPOINT: RESTABLECER CONTRASEÑA (HU #32)
# -----------------------------------------------------------------
@auth_bp.route('/restablecer-contrasena', methods=['POST'])
def restablecer_contrasena():
    datos = request.get_json()
    token = datos.get('token', '').strip()
    nueva_password = datos.get('nueva_password', '').strip()

    if not token:
        return jsonify({"status": "error", "message": "Token inválido."}), 400

    email = verificar_token_recuperacion(token)
    if not email:
        return jsonify({"status": "error", "message": "El enlace de recuperación ha expirado."}), 400

    usuario = Usuario.query.filter_by(email=email, token_recuperacion=token).first()
    if not usuario:
        return jsonify({"status": "error", "message": "El enlace de recuperación ha expirado."}), 400
    if usuario.token_recuperacion_usado:
        return jsonify({"status": "error", "message": "El enlace de recuperación ya fue utilizado."}), 400

    if len(nueva_password) < 6:
        return jsonify({"status": "error", "message": "La contraseña debe tener al menos 6 caracteres."}), 400

    if not re.search(r"[^a-zA-Z0-9]", nueva_password):
        return jsonify({"status": "error", "message": "La contraseña debe incluir al menos un carácter especial."}), 400

    try:
        usuario.password_hash = generate_password_hash(nueva_password)
        usuario.token_recuperacion_usado = True
        db.session.commit()
        return jsonify({"status": "success", "message": "Contraseña restablecida exitosamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al restablecer: {str(e)}"}), 500


# -----------------------------------------------------------------
# ENDPOINT: GENERAR CONFIRMACIÓN DE EMAIL (HU #36)
# -----------------------------------------------------------------
@auth_bp.route('/generar-confirmacion-email', methods=['POST'])
def generar_confirmacion_email():
    datos = request.get_json()
    email = datos.get('email', '').strip()

    if not email:
        return jsonify({"status": "error", "message": "Email inválido."}), 400

    token = serializer.dumps(email, salt="confirmacion-email")
    link = f"http://localhost:5173/confirmar-email-registro?token={token}"

    print(f"[SIMULACIÓN MAIL] Link de confirmación para {email}: {link}")

    return jsonify({
        "status": "success",
        "link_demo": link
    }), 200


# -----------------------------------------------------------------
# ENDPOINT: CONFIRMAR EMAIL DE REGISTRO (HU #36)
# -----------------------------------------------------------------
@auth_bp.route('/confirmar-email-registro', methods=['POST'])
def confirmar_email_registro():
    datos = request.get_json()
    token = datos.get('token', '').strip()

    if not token:
        return jsonify({"status": "error", "message": "El enlace de confirmación ha expirado."}), 400

    try:
        email = serializer.loads(token, salt="confirmacion-email", max_age=3600)
    except SignatureExpired:
        return jsonify({"status": "error", "message": "El enlace de confirmación ha expirado."}), 400
    except BadSignature:
        return jsonify({"status": "error", "message": "El enlace de confirmación ha expirado."}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404

    if usuario.email_confirmado:
        return jsonify({"status": "error", "message": "La cuenta ya se encuentra confirmada."}), 400

    try:
        usuario.email_confirmado = True
        db.session.commit()
        return jsonify({"status": "success", "message": "Cuenta confirmada correctamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al confirmar: {str(e)}"}), 500