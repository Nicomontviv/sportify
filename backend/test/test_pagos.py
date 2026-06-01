import pytest
from datetime import date, datetime, time
from models import db, Usuario, Empleado, Administrador, Actividad, Turno, Clase, Reserva, Deposito

# ==========================================
# FIXTURES LOCALES (Datos de prueba)
# ==========================================

@pytest.fixture
def usuario_casual(app_context):
    """Juan Perez - usuario casual con reservas para HU1 - DNI 99999999"""
    user = Usuario(
        nombre="Juan", apellido="Perez", dni="99999999",
        email="casual@test.com", password_hash="hash",
        fecha_nacimiento=date(1995, 3, 20), activo=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def usuario_casual_sin_reservas(app_context):
    """Gonzalo Lopez - usuario casual sin reservas - DNI 22555111"""
    user = Usuario(
        nombre="Gonzalo", apellido="Lopez", dni="22555111",
        email="gonzalo@test.com", password_hash="hash",
        fecha_nacimiento=date(1990, 1, 1), activo=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def usuario_casual_hu2(app_context):
    """Luis Gonzalez - usuario casual con reservas para HU2 - DNI 88888888"""
    user = Usuario(
        nombre="Luis", apellido="Gonzalez", dni="88888888",
        email="luis@test.com", password_hash="hash",
        fecha_nacimiento=date(1993, 6, 10), activo=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def usuario_empleado(app_context):
    """Mario Gomez - empleado de prueba - DNI 55555555"""
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
    """Nicolas Montanari - administrador de prueba - DNI 12345678"""
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
def reserva_futbol_viernes(app_context, usuario_casual):
    """Reserva de Fútbol viernes 5/6/2026 18:00hs para Juan Perez - escenarios 1 y 9 HU1"""
    actividad = Actividad(nombre="Futbol", precio_base=20000.0, activa=True)
    db.session.add(actividad)
    db.session.commit()

    turno = Turno(
        actividad_id=actividad.id,
        dia_semana='viernes',
        horario_inicio=time(18, 0),
        horario_fin=time(19, 0),
        cupo_maximo=12,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date(2026, 6, 5),
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
        monto_total=20000.00,
        monto_pagado=0.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_futbol_viernes_con_senia(app_context, usuario_casual):
    """Reserva de Fútbol viernes 5/6/2026 18:00hs con seña ya pagada - escenario 9 HU1"""
    actividad = Actividad(nombre="Futbol Senia", precio_base=20000.0, activa=True)
    db.session.add(actividad)
    db.session.commit()

    turno = Turno(
        actividad_id=actividad.id,
        dia_semana='viernes',
        horario_inicio=time(18, 0),
        horario_fin=time(19, 0),
        cupo_maximo=12,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date(2026, 6, 5),
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
        monto_total=20000.00,
        monto_pagado=10000.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_voley_martes(app_context, usuario_casual):
    """Reserva de Vóley martes 2/6/2026 17:00hs para Juan Perez - escenario 2 HU1"""
    actividad = Actividad(nombre="Voley", precio_base=18000.0, activa=True)
    db.session.add(actividad)
    db.session.commit()

    turno = Turno(
        actividad_id=actividad.id,
        dia_semana='martes',
        horario_inicio=time(17, 0),
        horario_fin=time(18, 0),
        cupo_maximo=12,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date(2026, 6, 2),
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
        monto_total=18000.00,
        monto_pagado=0.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_futbol_lunes(app_context, usuario_casual):
    """Reserva de Fútbol lunes 1/6/2026 10:00hs para Juan Perez - escenarios 4 al 12 HU1"""
    actividad = Actividad(nombre="Futbol Lunes", precio_base=20000.0, activa=True)
    db.session.add(actividad)
    db.session.commit()

    turno = Turno(
        actividad_id=actividad.id,
        dia_semana='lunes',
        horario_inicio=time(10, 0),
        horario_fin=time(11, 0),
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
        monto_total=20000.00,
        monto_pagado=0.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reservas_padel_basquet(app_context, usuario_casual):
    """Reservas de Pádel miércoles 3/6/2026 y Básquet jueves 4/6/2026 para Juan Perez - escenario 3 HU1"""
    act_padel = Actividad(nombre="Padel", precio_base=16000.0, activa=True)
    act_basquet = Actividad(nombre="Basquet", precio_base=18000.0, activa=True)
    db.session.add_all([act_padel, act_basquet])
    db.session.commit()

    turno_padel = Turno(actividad_id=act_padel.id, dia_semana='miercoles',
                        horario_inicio=time(19, 0), horario_fin=time(20, 0),
                        cupo_maximo=4, activo=True)
    turno_basquet = Turno(actividad_id=act_basquet.id, dia_semana='jueves',
                          horario_inicio=time(14, 0), horario_fin=time(15, 0),
                          cupo_maximo=12, activo=True)
    db.session.add_all([turno_padel, turno_basquet])
    db.session.commit()

    clase_padel = Clase(turno_id=turno_padel.id, fecha=date(2026, 6, 3),
                        cupo_disponible=3, activo=True)
    clase_basquet = Clase(turno_id=turno_basquet.id, fecha=date(2026, 6, 4),
                          cupo_disponible=11, activo=True)
    db.session.add_all([clase_padel, clase_basquet])
    db.session.commit()

    reserva_padel = Reserva(clase_id=clase_padel.id, usuario_id=usuario_casual.id,
                            estado='pendiente_pago', metodo_pago='tarjeta_virtual',
                            monto_total=16000.00, monto_pagado=0.00)
    reserva_basquet = Reserva(clase_id=clase_basquet.id, usuario_id=usuario_casual.id,
                              estado='pendiente_pago', metodo_pago='tarjeta_virtual',
                              monto_total=18000.00, monto_pagado=0.00)
    db.session.add_all([reserva_padel, reserva_basquet])
    db.session.commit()
    return reserva_padel, reserva_basquet

@pytest.fixture
def reserva_futbol_viernes_hu2(app_context, usuario_casual_hu2):
    """Reserva de Fútbol viernes 5/6/2026 18:00hs para Luis Gonzalez - escenarios 1 y 4 HU2"""
    actividad = Actividad(nombre="Futbol HU2", precio_base=20000.0, activa=True)
    db.session.add(actividad)
    db.session.commit()

    turno = Turno(actividad_id=actividad.id, dia_semana='viernes',
                  horario_inicio=time(18, 0), horario_fin=time(19, 0),
                  cupo_maximo=12, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=date(2026, 6, 5),
                  cupo_disponible=11, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_casual_hu2.id,
                      estado='pendiente_pago', metodo_pago='efectivo',
                      monto_total=20000.00, monto_pagado=0.00)
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_futbol_viernes_hu2_con_senia(app_context, usuario_casual_hu2):
    """Reserva de Fútbol viernes 5/6/2026 18:00hs con seña pagada para Luis Gonzalez - escenario 4 HU2"""
    actividad = Actividad(nombre="Futbol HU2 Senia", precio_base=20000.0, activa=True)
    db.session.add(actividad)
    db.session.commit()

    turno = Turno(actividad_id=actividad.id, dia_semana='viernes',
                  horario_inicio=time(18, 0), horario_fin=time(19, 0),
                  cupo_maximo=12, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=date(2026, 6, 5),
                  cupo_disponible=11, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_casual_hu2.id,
                      estado='pendiente_pago', metodo_pago='efectivo',
                      monto_total=20000.00, monto_pagado=10000.00)
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reservas_padel_basquet_hu2(app_context, usuario_casual_hu2):
    """Reservas de Pádel miércoles 3/6/2026 y Básquet jueves 4/6/2026 para Luis Gonzalez - escenario 3 HU2"""
    act_padel = Actividad(nombre="Padel HU2", precio_base=16000.0, activa=True)
    act_basquet = Actividad(nombre="Basquet HU2", precio_base=18000.0, activa=True)
    db.session.add_all([act_padel, act_basquet])
    db.session.commit()

    turno_padel = Turno(actividad_id=act_padel.id, dia_semana='miercoles',
                        horario_inicio=time(19, 0), horario_fin=time(20, 0),
                        cupo_maximo=4, activo=True)
    turno_basquet = Turno(actividad_id=act_basquet.id, dia_semana='jueves',
                          horario_inicio=time(14, 0), horario_fin=time(15, 0),
                          cupo_maximo=12, activo=True)
    db.session.add_all([turno_padel, turno_basquet])
    db.session.commit()

    clase_padel = Clase(turno_id=turno_padel.id, fecha=date(2026, 6, 3),
                        cupo_disponible=3, activo=True)
    clase_basquet = Clase(turno_id=turno_basquet.id, fecha=date(2026, 6, 4),
                          cupo_disponible=11, activo=True)
    db.session.add_all([clase_padel, clase_basquet])
    db.session.commit()

    reserva_padel = Reserva(clase_id=clase_padel.id, usuario_id=usuario_casual_hu2.id,
                            estado='pendiente_pago', metodo_pago='efectivo',
                            monto_total=16000.00, monto_pagado=0.00)
    reserva_basquet = Reserva(clase_id=clase_basquet.id, usuario_id=usuario_casual_hu2.id,
                              estado='pendiente_pago', metodo_pago='efectivo',
                              monto_total=18000.00, monto_pagado=0.00)
    db.session.add_all([reserva_padel, reserva_basquet])
    db.session.commit()
    return reserva_padel, reserva_basquet


# ==========================================
# DATOS DE TARJETA VÁLIDOS
# 1111111111111111 = pago exitoso
# 2222222222222222 = fondos insuficientes
# 3333333333333333 = tarjeta bloqueada o inhabilitada
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

def test_pago_virtual_senia_exitoso(client, usuario_casual, reserva_futbol_viernes):
    """Escenario 1: Pago exitoso de seña (50%) - Fútbol viernes 5/6/2026 18:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_viernes.id, "tipo_pago": "senia"}],
        **TARJETA_VALIDA
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago de seña confirmado exitosamente'

    deposito = Deposito.query.filter_by(reserva_id=reserva_futbol_viernes.id).first()
    assert deposito is not None
    assert float(deposito.monto) == 10000.00
    assert deposito.tipo == 'senia'

def test_pago_virtual_total_exitoso(client, usuario_casual, reserva_voley_martes):
    """Escenario 2: Pago exitoso del total (100%) - Vóley martes 2/6/2026 17:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_voley_martes.id, "tipo_pago": "total"}],
        **TARJETA_VALIDA
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago total confirmado exitosamente'

    db.session.refresh(reserva_voley_martes)
    assert reserva_voley_martes.estado == 'confirmada'
    assert float(reserva_voley_martes.monto_pagado) == 18000.00

def test_pago_virtual_varias_clases(client, usuario_casual, reservas_padel_basquet):
    """Escenario 3: Pago exitoso de varias clases - Pádel miércoles 3/6/2026 + Básquet jueves 4/6/2026"""
    reserva_padel, reserva_basquet = reservas_padel_basquet
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [
            {"reserva_id": reserva_padel.id, "tipo_pago": "senia"},
            {"reserva_id": reserva_basquet.id, "tipo_pago": "total"}
        ],
        **TARJETA_VALIDA
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago confirmado exitosamente'
    assert data['total_cobrado'] == 26000.00

def test_pago_virtual_tarjeta_numero_invalido(client, usuario_casual, reserva_futbol_lunes):
    """Escenario 4: Pago fallido por número de tarjeta inválido - Fútbol lunes 1/6/2026 10:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_lunes.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1234",
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El número de tarjeta debe tener exactamente 16 dígitos numéricos'

def test_pago_virtual_mes_vencimiento_invalido(client, usuario_casual, reserva_futbol_lunes):
    """Escenario 5: Pago fallido por mes de vencimiento inválido - Fútbol lunes 1/6/2026 10:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_lunes.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "Juan Perez",
        "vencimiento": "13/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El mes de vencimiento debe estar entre 01 y 12'

def test_pago_virtual_tarjeta_vencida(client, usuario_casual, reserva_futbol_lunes):
    """Escenario 6: Pago fallido por año de vencimiento anterior al actual - Fútbol lunes 1/6/2026 10:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_lunes.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "Juan Perez",
        "vencimiento": "12/25",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'La tarjeta está vencida'

def test_pago_virtual_cvv_invalido(client, usuario_casual, reserva_futbol_lunes):
    """Escenario 7: Pago fallido por CVV inválido - Fútbol lunes 1/6/2026 10:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_lunes.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "12"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El código de seguridad debe tener exactamente 3 dígitos'

def test_pago_virtual_titular_vacio(client, usuario_casual, reserva_futbol_lunes):
    """Escenario 8: Pago fallido por titular vacío - Fútbol lunes 1/6/2026 10:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_lunes.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "1111111111111111",
        "titular": "",
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'El nombre del titular es obligatorio'

def test_pago_virtual_saldo_faltante(client, usuario_casual, reserva_futbol_viernes_con_senia):
    """Escenario 9: Pago exitoso del saldo faltante - Fútbol viernes 5/6/2026 con seña ya pagada"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_viernes_con_senia.id, "tipo_pago": "total"}],
        **TARJETA_VALIDA
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago del saldo faltante confirmado exitosamente'

def test_pago_virtual_sin_reservas(client, usuario_casual_sin_reservas):
    """Escenario 10: No hay reservas pendientes de pago - Gonzalo Lopez DNI 22555111"""
    headers = {'X-User-Id': str(usuario_casual_sin_reservas.id)}

    response = client.get('/api/pagos/reservas-pendientes', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['reservas'] == []

def test_pago_virtual_fondos_insuficientes(client, usuario_casual, reserva_futbol_lunes):
    """Escenario 11: Pago denegado por fondos insuficientes - Fútbol lunes 1/6/2026 10:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_lunes.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "2222222222222222",
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'Pago denegado: fondos insuficientes'

def test_pago_virtual_tarjeta_bloqueada(client, usuario_casual, reserva_futbol_lunes):
    """Escenario 12: Pago denegado por tarjeta bloqueada o inhabilitada - Fútbol lunes 1/6/2026 10:00hs"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_lunes.id, "tipo_pago": "senia"}],
        "numero_tarjeta": "3333333333333333",
        "titular": "Juan Perez",
        "vencimiento": "12/27",
        "cvv": "123"
    }

    response = client.post('/api/pagos/virtual', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['message'] == 'Pago denegado: su tarjeta se encuentra bloqueada o inhabilitada'


# ==========================================
# TESTS HU2 — PAGO PRESENCIAL DEL USUARIO CASUAL
# ==========================================

def test_pago_presencial_senia_exitoso(client, usuario_empleado, reserva_futbol_viernes_hu2):
    """Escenario 1: Cobro exitoso de seña (50%) - Fútbol viernes 5/6/2026 18:00hs - Luis Gonzalez"""
    headers = {'X-User-Id': str(usuario_empleado.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_viernes_hu2.id, "tipo_pago": "senia"}]
    }

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Seña guardada exitosamente'

    deposito = Deposito.query.filter_by(reserva_id=reserva_futbol_viernes_hu2.id).first()
    assert deposito is not None
    assert deposito.tipo == 'senia'
    assert float(deposito.monto) == 10000.00

def test_pago_presencial_total_exitoso(client, usuario_empleado, usuario_casual_hu2):
    """Escenario 2: Cobro exitoso del total (100%) - Vóley martes 2/6/2026 17:00hs - Luis Gonzalez"""
    act = Actividad(nombre="Voley HU2", precio_base=18000.0, activa=True)
    db.session.add(act)
    db.session.commit()

    turno = Turno(actividad_id=act.id, dia_semana='martes',
                  horario_inicio=time(17, 0), horario_fin=time(18, 0),
                  cupo_maximo=12, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=date(2026, 6, 2),
                  cupo_disponible=11, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_casual_hu2.id,
                      estado='pendiente_pago', metodo_pago='efectivo',
                      monto_total=18000.00, monto_pagado=0.00)
    db.session.add(reserva)
    db.session.commit()

    headers = {'X-User-Id': str(usuario_empleado.id)}
    payload = {"pagos": [{"reserva_id": reserva.id, "tipo_pago": "total"}]}

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago total guardado exitosamente'

    db.session.refresh(reserva)
    assert reserva.estado == 'confirmada'
    assert float(reserva.monto_pagado) == 18000.00

def test_pago_presencial_varias_clases(client, usuario_empleado, reservas_padel_basquet_hu2):
    """Escenario 3: Cobro exitoso de varias clases - Pádel miércoles + Básquet jueves - Luis Gonzalez"""
    reserva_padel, reserva_basquet = reservas_padel_basquet_hu2
    headers = {'X-User-Id': str(usuario_empleado.id)}
    payload = {
        "pagos": [
            {"reserva_id": reserva_padel.id, "tipo_pago": "senia"},
            {"reserva_id": reserva_basquet.id, "tipo_pago": "total"}
        ]
    }

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago guardado exitosamente'
    assert data['total_cobrado'] == 26000.00

def test_pago_presencial_saldo_faltante(client, usuario_empleado, reserva_futbol_viernes_hu2_con_senia):
    """Escenario 4: Cobro exitoso del saldo faltante - Fútbol viernes con seña pagada - Luis Gonzalez"""
    headers = {'X-User-Id': str(usuario_empleado.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_viernes_hu2_con_senia.id, "tipo_pago": "total"}]
    }

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['message'] == 'Pago del saldo faltante guardado exitosamente'

def test_pago_presencial_no_autorizado(client, usuario_casual, reserva_futbol_viernes_hu2):
    """RN2.1: Un usuario casual no puede registrar pagos presenciales"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {
        "pagos": [{"reserva_id": reserva_futbol_viernes_hu2.id, "tipo_pago": "senia"}]
    }

    response = client.post('/api/pagos/presencial', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 403

def test_buscar_usuario_por_dni_exitoso(client, usuario_empleado, usuario_casual_hu2):
    """Búsqueda exitosa de usuario casual por DNI - Luis Gonzalez DNI 88888888"""
    headers = {'X-User-Id': str(usuario_empleado.id)}

    response = client.get(f'/api/pagos/usuario-por-dni/{usuario_casual_hu2.dni}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['usuario']['dni'] == usuario_casual_hu2.dni

def test_buscar_usuario_admin_rechazado(client, usuario_empleado, usuario_admin):
    """RN2.7: No se puede buscar un administrador por DNI - DNI 12345678"""
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

def test_consultar_mis_pagos_exitoso(client, usuario_casual, reserva_futbol_viernes):
    """Escenario 1: Listado de pagos exitoso - Juan Perez DNI 99999999 - Junio 2026"""
    deposito = Deposito(
        reserva_id=reserva_futbol_viernes.id,
        empleado_id=None,
        monto=10000.00,
        fecha=datetime(2026, 6, 5, 18, 0),
        tipo='senia'
    )
    db.session.add(deposito)
    db.session.commit()

    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.get('/api/pagos/mis-pagos?mes=6&anio=2026', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert len(data['pagos']) > 0

def test_consultar_mis_pagos_vacio(client, usuario_casual_sin_reservas):
    """Escenario 2: Listado de pagos vacío - Gonzalo Lopez DNI 22555111 - Junio 2026"""
    headers = {'X-User-Id': str(usuario_casual_sin_reservas.id)}
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
