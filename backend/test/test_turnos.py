import pytest
from datetime import date, time, timedelta
from models import db, Usuario, Administrador, Actividad, Turno, Clase, Reserva

# ==========================================
# FIXTURES LOCALES (Datos de prueba)
# ==========================================

@pytest.fixture
def admin_user(app_context):
    """Crea un usuario administrador para pasar las validaciones de _es_admin"""
    user = Usuario(
        nombre="Admin", apellido="Turnos", dni="12345678",
        email="admin.turnos@test.com", password_hash="hash",
        fecha_nacimiento=date(1990, 1, 1)
    )
    db.session.add(user)
    db.session.commit()

    admin = Administrador(usuario_id=user.id, nivel_acceso="total")
    db.session.add(admin)
    db.session.commit()
    return user


@pytest.fixture
def actividad_base(app_context):
    """Crea una actividad activa de prueba"""
    act = Actividad(nombre="Futbol Test", precio_base=4000.0, descripcion="Prueba turnos", activa=True)
    db.session.add(act)
    db.session.commit()
    return act


@pytest.fixture
def turno_base(client, admin_user, actividad_base):
    """
    Crea un turno vía API (lunes 10:00, cupo 10), lo que genera sus clases
    a 3 meses. Devuelve el dict 'turno' de la respuesta (incluye 'id').
    """
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {
        "actividad_id": actividad_base.id,
        "dia_semana": "lunes",
        "horario_inicio": "10:00",
        "cupo_maximo": 10
    }
    resp = client.post('/api/turnos', headers=headers, json=payload)
    return resp.get_json()['turno']


@pytest.fixture
def turno_con_reserva(app_context, actividad_base):
    """
    Crea un turno (martes 15:00, cupo 8) con una clase futura que tiene una
    reserva confirmada. Lo armamos a mano para controlar exactamente el estado.
    Devuelve el Turno.
    """
    turno = Turno(
        actividad_id=actividad_base.id,
        dia_semana='martes',
        horario_inicio=time(15, 0),
        horario_fin=time(16, 0),
        cupo_maximo=8,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    # Clase futura (a 7 dias, asegurado >= hoy)
    clase = Clase(
        turno_id=turno.id,
        fecha=date.today() + timedelta(days=7),
        cupo_disponible=7,  # 1 lugar ya ocupado por la reserva de abajo
        activo=True
    )
    db.session.add(clase)
    db.session.commit()

    cliente = Usuario(
        nombre="Cliente", apellido="Test", dni="44444444",
        email="cliente.turnos@test.com", password_hash="hash",
        fecha_nacimiento=date(2000, 1, 1)
    )
    db.session.add(cliente)
    db.session.commit()

    reserva = Reserva(
        clase_id=clase.id,
        usuario_id=cliente.id,
        estado='confirmada',  # cuenta como reserva activa en _clase_tiene_reservas
        metodo_pago='tarjeta_virtual',
        monto_total=4000.00,
        monto_pagado=2000.00
    )
    db.session.add(reserva)
    db.session.commit()
    return turno


# ==========================================
# TESTS - CREAR TURNO (POST /api/turnos)
# ==========================================

def test_crear_turno_exito(client, admin_user, actividad_base):
    """Crear un turno valido: responde 201, lo guarda y genera clases futuras"""
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {
        "actividad_id": actividad_base.id,
        "dia_semana": "miercoles",
        "horario_inicio": "18:00",
        "cupo_maximo": 12
    }

    response = client.post('/api/turnos', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['status'] == 'success'
    assert data['message'] == 'Turno creado correctamente.'
    # Por defecto el alcance es 3 meses, asi que siempre genera varias clases
    assert data['clases_generadas'] > 0

    # Verificamos que quedo en la base
    turno_db = Turno.query.filter_by(actividad_id=actividad_base.id, dia_semana='miercoles').first()
    assert turno_db is not None
    assert turno_db.cupo_maximo == 12
    # El horario_fin se calcula solo (+1 hora)
    assert turno_db.horario_fin == time(19, 0)


def test_crear_turno_sin_permisos(client):
    """Un usuario que no es admin recibe 403"""
    headers = {'X-User-Id': '999'}  # id que no esta en la tabla Administrador
    payload = {
        "actividad_id": 1,
        "dia_semana": "lunes",
        "horario_inicio": "10:00",
        "cupo_maximo": 10
    }

    response = client.post('/api/turnos', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 403
    assert data['message'] == "No autorizado. Se requiere perfil administrador."


def test_crear_turno_duplicado_falla(client, admin_user, turno_base):
    """No se puede crear un segundo turno activo en la misma franja (actividad+dia+horario)"""
    headers = {'X-User-Id': str(admin_user.id)}
    # turno_base ya creo lunes 10:00 para la actividad. Repetimos exactamente igual.
    payload = {
        "actividad_id": turno_base['actividad_id'],
        "dia_semana": "lunes",
        "horario_inicio": "10:00",
        "cupo_maximo": 5
    }

    response = client.post('/api/turnos', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == "Ya existe un turno activo para esa actividad en ese día y horario."


def test_crear_turno_cupo_invalido_falla(client, admin_user, actividad_base):
    """
    Cupo negativo => 400 'El cupo debe ser un numero entero positivo'.
    OJO: usamos -5 y no 0, porque 0 es falsy y caeria en 'faltan campos'.
    """
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {
        "actividad_id": actividad_base.id,
        "dia_semana": "jueves",
        "horario_inicio": "09:00",
        "cupo_maximo": -5
    }

    response = client.post('/api/turnos', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == "El cupo debe ser un número entero positivo."


def test_crear_turno_actividad_inactiva_falla(client, admin_user, app_context):
    """No se puede crear un turno sobre una actividad dada de baja"""
    act = Actividad(nombre="Padel Baja", precio_base=5000.0, activa=False)
    db.session.add(act)
    db.session.commit()

    headers = {'X-User-Id': str(admin_user.id)}
    payload = {
        "actividad_id": act.id,
        "dia_semana": "viernes",
        "horario_inicio": "20:00",
        "cupo_maximo": 8
    }

    response = client.post('/api/turnos', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == "No se puede crear un turno sobre una actividad dada de baja."


# ==========================================
# TESTS - MODIFICAR TURNO (PUT /api/turnos/<id>)
# ==========================================

def test_modificar_cupo_sin_reservas_exito(client, admin_user, turno_base):
    """Sin reservas se puede cambiar el cupo libremente (CASO B: regenera clases)"""
    turno_id = turno_base['id']
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {"cupo_maximo": 15}

    response = client.put(f'/api/turnos/{turno_id}', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == "Turno modificado correctamente."

    # Verificamos el cambio en la base
    turno_db = db.session.get(Turno, turno_id)
    assert turno_db.cupo_maximo == 15


def test_modificar_subir_cupo_con_reservas_exito(client, admin_user, turno_con_reserva):
    """
    Con reservas SI se permite SUBIR el cupo (CASO A).
    El cupo_disponible de las clases futuras se incrementa en el mismo delta.
    """
    turno_id = turno_con_reserva.id
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {"cupo_maximo": 10}  # de 8 a 10 => delta +2

    response = client.put(f'/api/turnos/{turno_id}', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == "Turno modificado correctamente. Cupo incrementado en clases futuras."

    turno_db = db.session.get(Turno, turno_id)
    assert turno_db.cupo_maximo == 10

    # La clase futura tenia cupo_disponible 7 => debe pasar a 9 (+2)
    clase_db = Clase.query.filter_by(turno_id=turno_id).first()
    assert clase_db.cupo_disponible == 9


def test_modificar_horario_con_reservas_bloqueado(client, admin_user, turno_con_reserva):
    """Con reservas NO se puede cambiar el horario => 400"""
    turno_id = turno_con_reserva.id
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {"horario_inicio": "16:00"}  # distinto de las 15:00 originales

    response = client.put(f'/api/turnos/{turno_id}', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "No se puede cambiar el horario" in data['message']

    # El horario no debe haber cambiado
    turno_db = db.session.get(Turno, turno_id)
    assert turno_db.horario_inicio == time(15, 0)


def test_modificar_bajar_cupo_con_reservas_bloqueado(client, admin_user, turno_con_reserva):
    """Con reservas el cupo solo se puede incrementar, no reducir => 400"""
    turno_id = turno_con_reserva.id
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {"cupo_maximo": 5}  # menor que 8

    response = client.put(f'/api/turnos/{turno_id}', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "El cupo solo se puede incrementar" in data['message']

    # El cupo no debe haber cambiado
    turno_db = db.session.get(Turno, turno_id)
    assert turno_db.cupo_maximo == 8


# ==========================================
# TESTS - ELIMINAR TURNO (DELETE /api/turnos/<id>)
# ==========================================

def test_eliminar_turno_exito(client, admin_user, turno_base):
    """Baja logica del turno: responde 200 y deja activo=False"""
    turno_id = turno_base['id']
    headers = {'X-User-Id': str(admin_user.id)}

    response = client.delete(f'/api/turnos/{turno_id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == "Turno dado de baja correctamente."

    turno_db = db.session.get(Turno, turno_id)
    assert turno_db.activo is False


def test_eliminar_turno_inexistente_falla(client, admin_user):
    """Eliminar un turno que no existe => 404"""
    headers = {'X-User-Id': str(admin_user.id)}

    response = client.delete('/api/turnos/99999', headers=headers)
    data = response.get_json()

    assert response.status_code == 404
    assert data['message'] == "Turno no encontrado."


# ==========================================
# TESTS - DAR DE BAJA CLASE PUNTUAL (DELETE /api/turnos/clases/<id>)
# ==========================================

def test_dar_de_baja_clase_sin_reservas_exito(client, admin_user, turno_base):
    """
    Baja de una clase puntual sin reservas: 200 y activo=False.
    (No cubrimos el caso con reservas: queda fuera del alcance de esta entrega.)
    """
    turno_id = turno_base['id']
    clase = Clase.query.filter_by(turno_id=turno_id, activo=True).first()
    assert clase is not None  # turno_base genero clases

    headers = {'X-User-Id': str(admin_user.id)}
    response = client.delete(f'/api/turnos/clases/{clase.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == "Clase dada de baja correctamente."
    assert data['detalles']['tenia_reservas'] is False

    clase_db = db.session.get(Clase, clase.id)
    assert clase_db.activo is False


# ==========================================
# TESTS - SELECTOR DE ALCANCE (cantidad de clases generadas)
# ==========================================

def test_alcance_proxima_genera_una_clase(client, admin_user, actividad_base):
    """alcance='proxima' = ventana de 7 dias = exactamente 1 clase del dia objetivo"""
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {
        "actividad_id": actividad_base.id,
        "dia_semana": "lunes",
        "horario_inicio": "10:00",
        "cupo_maximo": 10,
        "alcance": "proxima"
    }

    response = client.post('/api/turnos', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['clases_generadas'] == 1


def test_alcance_dos_semanas_genera_dos_clases(client, admin_user, actividad_base):
    """alcance='2semanas' = ventana de 14 dias = exactamente 2 clases del dia objetivo"""
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {
        "actividad_id": actividad_base.id,
        "dia_semana": "martes",
        "horario_inicio": "11:00",
        "cupo_maximo": 10,
        "alcance": "2semanas"
    }

    response = client.post('/api/turnos', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['clases_generadas'] == 2
