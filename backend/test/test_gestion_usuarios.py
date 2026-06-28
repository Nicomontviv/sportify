import pytest
from werkzeug.security import generate_password_hash
from models import db, Usuario, Administrador, Empleado, Certificado
from datetime import date

# ============================================================
# HELPERS
# ============================================================

def crear_usuario_casual(dni="99999999", email="casual@test.com", activo=True):
    usuario = Usuario(
        nombre="Juan",
        apellido="Perez",
        dni=dni,
        email=email,
        password_hash=generate_password_hash("casual123!"),
        fecha_nacimiento=date(1995, 3, 20),
        activo=activo
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario

def crear_admin(dni="12345678", email="admin@test.com"):
    usuario = Usuario(
        nombre="Admin",
        apellido="Test",
        dni=dni,
        email=email,
        password_hash=generate_password_hash("admin123!"),
        fecha_nacimiento=date(1990, 1, 1),
        activo=True
    )
    db.session.add(usuario)
    db.session.flush()
    db.session.add(Administrador(usuario_id=usuario.id, nivel_acceso="total"))
    db.session.commit()
    return usuario

def crear_empleado(dni="55555555", email="empleado@test.com"):
    usuario = Usuario(
        nombre="Empleado",
        apellido="Test",
        dni=dni,
        email=email,
        password_hash=generate_password_hash("empleado123!"),
        fecha_nacimiento=date(1990, 1, 1),
        activo=True
    )
    db.session.add(usuario)
    db.session.flush()
    db.session.add(Empleado(usuario_id=usuario.id, legajo="EMP001", cargo="Recepcionista"))
    db.session.commit()
    return usuario


# ============================================================
# HU #62 - REACTIVAR USUARIO
# ============================================================

class TestReactivarUsuario:

    def test_dni_vacio(self, client, app_context):
        response = client.put('/api/reactivar-usuario', json={"dni": ""})
        assert response.status_code == 400
        assert "Ingresá un DNI para buscar" in response.get_json()["message"]

    def test_dni_invalido(self, client, app_context):
        response = client.put('/api/reactivar-usuario', json={"dni": "1234"})
        assert response.status_code == 400
        assert "8 dígitos" in response.get_json()["message"]

    def test_dni_inexistente(self, client, app_context):
        response = client.put('/api/reactivar-usuario', json={"dni": "11111111"})
        assert response.status_code == 404

    def test_dni_admin(self, client, app_context):
        crear_admin(dni="12345678")
        response = client.put('/api/reactivar-usuario', json={"dni": "12345678"})
        assert response.status_code == 404

    def test_dni_empleado(self, client, app_context):
        crear_empleado(dni="55555555")
        response = client.put('/api/reactivar-usuario', json={"dni": "55555555"})
        assert response.status_code == 404

    def test_usuario_ya_activo(self, client, app_context):
        crear_usuario_casual(dni="99999999", activo=True)
        response = client.put('/api/reactivar-usuario', json={"dni": "99999999"})
        assert response.status_code == 400
        assert "ya está activo" in response.get_json()["message"]

    def test_reactivar_exitoso(self, client, app_context):
        crear_usuario_casual(dni="99999999", activo=False)
        response = client.put('/api/reactivar-usuario', json={"dni": "99999999"})
        assert response.status_code == 200
        assert "reactivado" in response.get_json()["message"]

# ============================================================
# HU #33 - REGISTRAR CERTIFICADO DE APTITUD FÍSICA
# ============================================================

class TestRegistrarCertificado:

    def test_dni_vacio(self, client, app_context):
        response = client.post('/api/empleado/buscar-usuario-certificado', json={"dni": ""})
        assert response.status_code == 400
        assert "Ingresá un DNI para buscar" in response.get_json()["message"]

    def test_dni_invalido(self, client, app_context):
        response = client.post('/api/empleado/buscar-usuario-certificado', json={"dni": "1234"})
        assert response.status_code == 400
        assert "8 dígitos" in response.get_json()["message"]

    def test_dni_inexistente(self, client, app_context):
        response = client.post('/api/empleado/buscar-usuario-certificado', json={"dni": "11111111"})
        assert response.status_code == 404

    def test_dni_admin(self, client, app_context):
        crear_admin(dni="12345678")
        response = client.post('/api/empleado/buscar-usuario-certificado', json={"dni": "12345678"})
        assert response.status_code == 404

    def test_dni_empleado(self, client, app_context):
        crear_empleado(dni="55555555")
        response = client.post('/api/empleado/buscar-usuario-certificado', json={"dni": "55555555"})
        assert response.status_code == 404

    def test_usuario_con_certificado_vigente(self, client, app_context):
        usuario = crear_usuario_casual(dni="99999999")
        certificado = Certificado(
            usuario_id=usuario.id,
            fecha_emision=date(2026, 1, 1),
            fecha_vencimiento=date(2027, 1, 1),
            estado='vigente'
        )
        db.session.add(certificado)
        db.session.commit()
        response = client.post('/api/empleado/buscar-usuario-certificado', json={"dni": "99999999"})
        assert response.status_code == 400
        assert "ya cuenta con un certificado vigente" in response.get_json()["message"]

    def test_buscar_usuario_exitoso(self, client, app_context):
        crear_usuario_casual(dni="99999999")
        response = client.post('/api/empleado/buscar-usuario-certificado', json={"dni": "99999999"})
        assert response.status_code == 200
        assert response.get_json()["status"] == "encontrado"

    def test_registrar_certificado_exitoso(self, client, app_context):
        crear_usuario_casual(dni="99999999")
        response = client.post('/api/empleado/registrar-certificado', json={
            "dni": "99999999",
            "fecha_emision": "2026-01-01",
            "fecha_vencimiento": "2027-01-01"
        })
        assert response.status_code == 201
        assert "registrado correctamente" in response.get_json()["message"]

    def test_fecha_vencimiento_anterior_emision(self, client, app_context):
        crear_usuario_casual(dni="99999999")
        response = client.post('/api/empleado/registrar-certificado', json={
            "dni": "99999999",
            "fecha_emision": "2026-06-01",
            "fecha_vencimiento": "2026-01-01"
        })
        assert response.status_code == 400
        assert "anterior" in response.get_json()["message"]

    def test_certificado_vencido(self, client, app_context):
        crear_usuario_casual(dni="99999999")
        response = client.post('/api/empleado/registrar-certificado', json={
            "dni": "99999999",
            "fecha_emision": "2020-01-01",
            "fecha_vencimiento": "2021-01-01"
        })
        assert response.status_code == 400
        assert "vencido" in response.get_json()["message"]


# ============================================================
# HU #32 - RECUPERACIÓN DE CONTRASEÑA
# ============================================================

class TestRecuperarContrasena:

    def test_email_vacio(self, client, app_context):
        response = client.post('/api/recuperar-contrasena', json={"email": ""})
        assert response.status_code == 400
        assert "obligatorio" in response.get_json()["message"]

    def test_email_inexistente(self, client, app_context):
        response = client.post('/api/recuperar-contrasena', json={"email": "noexiste@test.com"})
        assert response.status_code == 404

    def test_recuperar_exitoso(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        response = client.post('/api/recuperar-contrasena', json={"email": "casual@test.com"})
        assert response.status_code == 200
        assert "link_demo" in response.get_json()

    def test_restablecer_contrasena_exitoso(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        res = client.post('/api/recuperar-contrasena', json={"email": "casual@test.com"})
        token = res.get_json()["link_demo"].split("token=")[1]
        response = client.post('/api/restablecer-contrasena', json={
            "token": token,
            "nueva_password": "nueva123!"
        })
        assert response.status_code == 200
        assert "exitosamente" in response.get_json()["message"]

    def test_restablecer_contrasena_corta(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        res = client.post('/api/recuperar-contrasena', json={"email": "casual@test.com"})
        token = res.get_json()["link_demo"].split("token=")[1]
        response = client.post('/api/restablecer-contrasena', json={
            "token": token,
            "nueva_password": "abc"
        })
        assert response.status_code == 400
        assert "6 caracteres" in response.get_json()["message"]

    def test_restablecer_contrasena_sin_caracter_especial(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        res = client.post('/api/recuperar-contrasena', json={"email": "casual@test.com"})
        token = res.get_json()["link_demo"].split("token=")[1]
        response = client.post('/api/restablecer-contrasena', json={
            "token": token,
            "nueva_password": "sincaracter"
        })
        assert response.status_code == 400
        assert "especial" in response.get_json()["message"]

    def test_link_ya_utilizado(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        res = client.post('/api/recuperar-contrasena', json={"email": "casual@test.com"})
        token = res.get_json()["link_demo"].split("token=")[1]
        client.post('/api/restablecer-contrasena', json={"token": token, "nueva_password": "nueva123!"})
        response = client.post('/api/restablecer-contrasena', json={"token": token, "nueva_password": "otra123!"})
        assert response.status_code == 400
        assert "utilizado" in response.get_json()["message"]


# ============================================================
# HU #36 - CONFIRMACIÓN DE EMAIL
# ============================================================

class TestConfirmarEmail:

    def test_confirmar_email_exitoso(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        res = client.post('/api/generar-confirmacion-email', json={"email": "casual@test.com"})
        token = res.get_json()["link_demo"].split("token=")[1]
        response = client.post('/api/confirmar-email-registro', json={"token": token})
        assert response.status_code == 200
        assert "confirmada correctamente" in response.get_json()["message"]

    def test_cuenta_ya_confirmada(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        res = client.post('/api/generar-confirmacion-email', json={"email": "casual@test.com"})
        token = res.get_json()["link_demo"].split("token=")[1]
        client.post('/api/confirmar-email-registro', json={"token": token})
        response = client.post('/api/confirmar-email-registro', json={"token": token})
        assert response.status_code == 400
        assert "ya se encuentra confirmada" in response.get_json()["message"]

    def test_token_vacio(self, client, app_context):
        response = client.post('/api/confirmar-email-registro', json={"token": ""})
        assert response.status_code == 400
        assert "expirado" in response.get_json()["message"]

    def test_token_invalido(self, client, app_context):
        response = client.post('/api/confirmar-email-registro', json={"token": "tokeninvalido"})
        assert response.status_code == 400
        assert "expirado" in response.get_json()["message"]

    def test_generar_confirmacion_email_vacio(self, client, app_context):
        response = client.post('/api/generar-confirmacion-email', json={"email": ""})
        assert response.status_code == 400


# ============================================================
# HU #29 - CARGA DE USUARIO POR PARTE DEL EMPLEADO
# ============================================================

class TestRegistrarUsuario:

    def test_campos_obligatorios(self, client, app_context):
        response = client.post('/api/registro', json={
            "nombre": "",
            "apellido": "",
            "dni": "",
            "email": "",
            "password": "",
            "fecha_nacimiento": ""
        })
        assert response.status_code == 400
        assert "obligatorios" in response.get_json()["message"]

    def test_dni_duplicado(self, client, app_context):
        crear_usuario_casual(dni="99999999")
        response = client.post('/api/registro', json={
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "dni": "99999999",
            "email": "carlos@test.com",
            "password": "carlos123!",
            "fecha_nacimiento": "1990-10-10"
        })
        assert response.status_code == 400
        assert "DNI" in response.get_json()["message"]

    def test_email_duplicado(self, client, app_context):
        crear_usuario_casual(email="casual@test.com")
        response = client.post('/api/registro', json={
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "dni": "33344455",
            "email": "casual@test.com",
            "password": "carlos123!",
            "fecha_nacimiento": "1990-10-10"
        })
        assert response.status_code == 400
        assert "Email" in response.get_json()["message"]

    def test_menor_de_edad(self, client, app_context):
        response = client.post('/api/registro', json={
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "dni": "33344455",
            "email": "carlos@test.com",
            "password": "carlos123!",
            "fecha_nacimiento": "2015-10-10"
        })
        assert response.status_code == 400
        assert "mayor de edad" in response.get_json()["message"]

    def test_contrasena_corta(self, client, app_context):
        response = client.post('/api/registro', json={
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "dni": "33344455",
            "email": "carlos@test.com",
            "password": "abc",
            "fecha_nacimiento": "1990-10-10"
        })
        assert response.status_code == 400
        assert "6 caracteres" in response.get_json()["message"]

    def test_contrasena_sin_caracter_especial(self, client, app_context):
        response = client.post('/api/registro', json={
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "dni": "33344455",
            "email": "carlos@test.com",
            "password": "sincaracter",
            "fecha_nacimiento": "1990-10-10"
        })
        assert response.status_code == 400
        assert "especial" in response.get_json()["message"]

    def test_registro_exitoso(self, client, app_context):
        response = client.post('/api/registro', json={
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "dni": "33344455",
            "email": "carlos@test.com",
            "password": "carlos123!",
            "fecha_nacimiento": "1990-10-10"
        })
        assert response.status_code == 201
        assert "éxito" in response.get_json()["message"]