import pytest
from datetime import date, datetime
from models import db, Usuario, Empleado, Administrador, Actividad, Turno, Clase, Reserva, Deposito

# ==========================================
# FIXTURES LOCALES (Datos de prueba)
# ==========================================

@pytest.fixture
def usuario_casual(app_context):
    """Crea un usuario casual de prueba"""
    user = Usuario(
        nombre="Juan", apellido="Perez", dni="99999999",
        email="casual@test.com", password_hash="hash",
        fecha_nacimiento=date(1995, 3, 20), activo=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def usuario_empleado(app_context):
    """Crea un usuario empleado de prueba"""
    user = Usuario(
        nombre="Mario", apellido="Gomez", dni="55555555",
        email="empleado@test.com", password_hash="hash",
        fecha_nacimiento=date(1990, 5, 15), activo=True
    )
    db.session.add(user)
    db.session.commit()

    empleado = Empleado(usuario_id=user.id, legajo="EMP001", cargo="Recepcionista")
    db.session.add(empleado)
    db.session.commit()
    return user

@pytest.fixture
def usuario_admin(app_context):
    """Crea un usuario administrador de prueba"""
    user = Usuario(
        nombre="Nicolas", apellido="Montanari", dni="12345678",
        email="admin@test.com", password_hash="hash",
        fecha_nacimiento=date(1995, 10, 10), activo=True
    )
    db.session.add(user)
    db.session.commit()

    admin = Administrador(usuario_id=user.id, nivel_acceso="total")
    db.session.add(admin)
    db.session.commit()
    return user

@pytest.fixture
def reserva_pendiente(app_context, usuario_casual):
    """Crea una reserva pendiente de pago para el usuario casual"""
    actividad = Actividad(nombre="Voley Test", precio_base=12000.0, activa=True)
    db.session.add(actividad)
    db.session.commit()

    from datetime import time
    turno = Turno(
        actividad_id=actividad.id,
        dia_semana='lunes',
        horario_inicio=time(18, 0),
        horario_fin=time(19, 0),
        cupo_maximo=12,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date(2026, 6, 1),
        cupo_disponible=11,
        activo=True
    )
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(
        clase_id=clase.id,
        usuario_id=usuario_casual.id,
        estado='pendiente_pago',
        metodo_pago='tarjeta_virtual',
        monto_total=12000.00,
        monto_pagado=0.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva


# ==========================================
# DATOS DE TARJETA VÁLIDOS
# 1111111111111111 = pago exitoso
# 2222222222222222 = fondos insuficientes
# 3333333333333333 = tarjeta con problemas
# ==========================================
TARJETA_VALIDA = {
    "numero_tarjeta": "1111111111111111",
    "titular": "Juan Perez",
    "vencimiento": "12/27",
    "cvv": "123"
}


# ==========================================
# TESTS HU1 — PAGO VIRTUAL DEL USUARIO CASUAL
# ==========================================

def test_pago_virtual_senia_exitoso(client, usuario_casual, reserva_pendiente):
    """Escenario 1: Pago exitoso de seña (50%) de una clase"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        **TARJETA_VALIDA
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago de seña confirmado exitosamente'

    # Verificamos que el depósito se registró correctamente
    deposito = Deposito.query.filter_by(reserva_id=reserva_pendiente.id).first()
    assert deposito is not None
    assert float(deposito.monto) == 6000.00
    assert deposito.tipo == 'senia'

def test_pago_virtual_total_exitoso(client, usuario_casual, reserva_pendiente):
    """Escenario 2: Pago exitoso del total (100%) de una clase"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "total"}],
        **TARJETA_VALIDA
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago total confirmado exitosamente'

    # Verificamos que la reserva quedó confirmada
    db.session.refresh(reserva_pendiente)
    assert reserva_pendiente.estado == 'confirmada'
    assert float(reserva_pendiente.monto_pagado) == 12000.00

def test_pago_virtual_tarjeta_numero_invalido(client, usuario_casual, reserva_pendiente):
    """Escenario 4: Pago fallido por número de tarjeta inválido"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1234",  # Solo 4 dígitos
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El número de tarjeta debe tener exactamente 16 dígitos numéricos'

def test_pago_virtual_mes_vencimiento_invalido(client, usuario_casual, reserva_pendiente):
    """Escenario 5: Pago fallido por mes de vencimiento inválido"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "Juan Perez",
        "vencimiento": "13/27",  # Mes 13 inválido
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El mes de vencimiento debe estar entre 01 y 12'

def test_pago_virtual_tarjeta_vencida(client, usuario_casual, reserva_pendiente):
    """Escenario 6: Pago fallido por año de vencimiento anterior al actual"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "Juan Perez",
        "vencimiento": "12/25",  # Año 2025 vencido
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'La tarjeta está vencida'

def test_pago_virtual_cvv_invalido(client, usuario_casual, reserva_pendiente):
    """Escenario 7: Pago fallido por CVV inválido"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "12"  # Solo 2 dígitos
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El código de seguridad debe tener exactamente 3 dígitos'

def test_pago_virtual_titular_vacio(client, usuario_casual, reserva_pendiente):
    """Escenario 8: Pago fallido por titular vacío"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "",  # Titular vacío
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El nombre del titular es obligatorio'

def test_pago_virtual_sin_reservas(client, usuario_casual):
    """Escenario 10: No hay reservas pendientes de pago"""
    headers = {'X-User-Id': str(usuario_casual.id)}

    response = client.get('/api/pagos/reservas-pendientes', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['reservas'] == []

def test_pago_virtual_fondos_insuficientes(client, usuario_casual, reserva_pendiente):
    """Escenario 11: Pago rechazado por fondos insuficientes"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "2222222222222222",
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'Pago rechazado: fondos insuficientes'

def test_pago_virtual_tarjeta_con_problemas(client, usuario_casual, reserva_pendiente):
    """Escenario 12: Pago rechazado por tarjeta con problemas"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "3333333333333333",
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'Pago rechazado: tarjeta con problemas'


# ==========================================
# TESTS HU2 — PAGO PRESENCIAL DEL USUARIO CASUAL
# ==========================================

def test_pago_presencial_senia_exitoso(client, usuario_empleado, usuario_casual, reserva_pendiente):
    """Escenario 1: Registro exitoso de seña (50%) de una clase"""
    headers = {'X-User-Id': str(usuario_empleado.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}]
    }

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Seña registrada exitosamente'

    # Verificamos que el depósito se registró con el empleado
    deposito = Deposito.query.filter_by(reserva_id=reserva_pendiente.id).first()
    assert deposito is not None
    assert deposito.tipo == 'senia'
    assert float(deposito.monto) == 6000.00

def test_pago_presencial_total_exitoso(client, usuario_empleado, usuario_casual, reserva_pendiente):
    """Escenario 2: Registro exitoso del total (100%) de una clase"""
    headers = {'X-User-Id': str(usuario_empleado.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "total"}]
    }

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago total registrado exitosamente'

    db.session.refresh(reserva_pendiente)
    assert reserva_pendiente.estado == 'confirmada'
    assert float(reserva_pendiente.monto_pagado) == 12000.00

def test_pago_presencial_no_autorizado(client, usuario_casual, reserva_pendiente):
    """RN2.1: Un usuario casual no puede registrar pagos presenciales"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_pendiente.id, "tipo_pago": "senia"}]
    }

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 403

def test_buscar_usuario_por_dni_exitoso(client, usuario_empleado, usuario_casual):
    """Búsqueda exitosa de usuario casual por DNI"""
    headers = {'X-User-Id': str(usuario_empleado.id)}

    response = client.get(f'/api/pagos/usuario-por-dni/{usuario_casual.dni}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['usuario']['dni'] == usuario_casual.dni

def test_buscar_usuario_admin_rechazado(client, usuario_empleado, usuario_admin):
    """RN2.7: No se puede buscar un administrador por DNI"""
    headers = {'X-User-Id': str(usuario_empleado.id)}

    response = client.get(f'/api/pagos/usuario-por-dni/{usuario_admin.dni}', headers=headers)
    data = response.get_json()

    assert response.status_code == 404
    assert data['message'] == 'No se encontró ningún usuario con ese DNI.'

def test_buscar_usuario_no_existe(client, usuario_empleado):
    """Escenario 8: DNI que no existe en el sistema"""
    headers = {'X-User-Id': str(usuario_empleado.id)}

    response = client.get('/api/pagos/usuario-por-dni/00000000', headers=headers)
    data = response.get_json()

    assert response.status_code == 404


# ==========================================
# TESTS HU3 — CONSULTAR MIS PAGOS
# ==========================================

def test_consultar_mis_pagos_exitoso(client, usuario_casual, reserva_pendiente):
    """Escenario 1: Listado de pagos exitoso"""
    # Primero registramos un depósito
    deposito = Deposito(
        reserva_id=reserva_pendiente.id,
        empleado_id=None,
        monto=6000.00,
        fecha=datetime(2026, 5, 22, 10, 0),
        tipo='senia'
    )
    db.session.add(deposito)
    db.session.commit()

    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.get('/api/pagos/mis-pagos?mes=5&anio=2026', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert len(data['pagos']) > 0

def test_consultar_mis_pagos_vacio(client, usuario_casual):
    """Escenario 2: Listado de pagos vacío"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.get('/api/pagos/mis-pagos?mes=6&anio=2026', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['pagos'] == []
    assert data['message'] == 'No posee pagos en el mes seleccionado'

def test_consultar_mis_pagos_sin_parametros(client, usuario_casual):
    """Error si no se envían mes y año"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.get('/api/pagos/mis-pagos', headers=headers)
    data = response.get_json()

    assert response.status_code == 400
