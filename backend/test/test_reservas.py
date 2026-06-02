import pytest
from datetime import date, datetime, time, timedelta
from models import db, Usuario, Credito, Actividad, Turno, Clase, Reserva

# ==========================================
# FIXTURES LOCALES (Datos de prueba)
# ==========================================

@pytest.fixture
def usuario_casual(app_context):
    """Crea un usuario casual (no abonado) de prueba"""
    user = Usuario(
        nombre="Juan", apellido="Perez", dni="99999999",
        email="casual@test.com", password_hash="hash",
        fecha_nacimiento=date(1995, 3, 20), activo=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def usuario_abonado(app_context):
    """Crea un usuario abonado con crédito activo para el mes actual"""
    user = Usuario(
        nombre="Carlos", apellido="Gomez", dni="22222222",
        email="abonado@test.com", password_hash="hash",
        fecha_nacimiento=date(1990, 5, 15), activo=True
    )
    db.session.add(user)
    db.session.commit()

    ahora = datetime.now()
    credito = Credito(
        usuario_id=user.id,
        monto_descuento=20.00,
        mes=ahora.month,
        anio=ahora.year,
        pagado=True,
        descuento_activo=True,
        cancelaciones=0
    )
    db.session.add(credito)
    db.session.commit()
    return user

@pytest.fixture
def actividad_base(app_context):
    """Crea una actividad de prueba"""
    act = Actividad(nombre="Crossfit Test", precio_base=5000.0, activa=True)
    db.session.add(act)
    db.session.commit()
    return act

@pytest.fixture
def clase_con_cupo(app_context, actividad_base):
    """Clase futura (3 días) con cupo disponible"""
    turno = Turno(
        actividad_id=actividad_base.id,
        dia_semana='lunes',
        horario_inicio=time(10, 0),
        horario_fin=time(11, 0),
        cupo_maximo=10,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date.today() + timedelta(days=3),
        cupo_disponible=5,
        activo=True
    )
    db.session.add(clase)
    db.session.commit()
    return clase

@pytest.fixture
def clase_sin_cupo(app_context, actividad_base):
    """Clase futura sin cupo disponible"""
    turno = Turno(
        actividad_id=actividad_base.id,
        dia_semana='martes',
        horario_inicio=time(14, 0),
        horario_fin=time(15, 0),
        cupo_maximo=5,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date.today() + timedelta(days=3),
        cupo_disponible=0,
        activo=True
    )
    db.session.add(clase)
    db.session.commit()
    return clase

@pytest.fixture
def reserva_cancelable_mas_24h(app_context, usuario_casual, actividad_base):
    """Reserva cuya clase empieza en más de 24h → cancelable con devolución de seña"""
    turno = Turno(
        actividad_id=actividad_base.id,
        dia_semana='miercoles',
        horario_inicio=time(10, 0),
        horario_fin=time(11, 0),
        cupo_maximo=10,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date.today() + timedelta(days=3),
        cupo_disponible=5,
        activo=True
    )
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(
        clase_id=clase.id,
        usuario_id=usuario_casual.id,
        estado='confirmada',
        metodo_pago='efectivo',
        monto_total=5000.00,
        monto_pagado=2500.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_cancelable_entre_1h_y_24h(app_context, usuario_casual, actividad_base):
    """Reserva cuya clase empieza en 3h → cancelable pero sin devolución de seña"""
    inicio = datetime.now() + timedelta(hours=3)
    turno = Turno(
        actividad_id=actividad_base.id,
        dia_semana='jueves',
        horario_inicio=inicio.replace(microsecond=0, second=0).time(),
        horario_fin=(inicio + timedelta(hours=1)).replace(microsecond=0, second=0).time(),
        cupo_maximo=10,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=inicio.date(),
        cupo_disponible=5,
        activo=True
    )
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(
        clase_id=clase.id,
        usuario_id=usuario_casual.id,
        estado='confirmada',
        metodo_pago='efectivo',
        monto_total=5000.00,
        monto_pagado=2500.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_no_cancelable(app_context, usuario_casual, actividad_base):
    """Reserva cuya clase empieza en 30 minutos → fuera del límite de cancelación"""
    inicio = datetime.now() + timedelta(minutes=30)
    turno = Turno(
        actividad_id=actividad_base.id,
        dia_semana='viernes',
        horario_inicio=inicio.replace(microsecond=0, second=0).time(),
        horario_fin=(inicio + timedelta(hours=1)).replace(microsecond=0, second=0).time(),
        cupo_maximo=10,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=inicio.date(),
        cupo_disponible=5,
        activo=True
    )
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(
        clase_id=clase.id,
        usuario_id=usuario_casual.id,
        estado='confirmada',
        metodo_pago='efectivo',
        monto_total=5000.00,
        monto_pagado=2500.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_abonado_cancelable(app_context, usuario_abonado, actividad_base):
    """Reserva de abonado con clase en más de 24h → cancela y acumula cancelación en crédito"""
    turno = Turno(
        actividad_id=actividad_base.id,
        dia_semana='lunes',
        horario_inicio=time(16, 0),
        horario_fin=time(17, 0),
        cupo_maximo=10,
        activo=True
    )
    db.session.add(turno)
    db.session.commit()

    clase = Clase(
        turno_id=turno.id,
        fecha=date.today() + timedelta(days=3),
        cupo_disponible=5,
        activo=True
    )
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(
        clase_id=clase.id,
        usuario_id=usuario_abonado.id,
        estado='confirmada',
        metodo_pago='membresia',
        monto_total=4000.00,
        monto_pagado=4000.00
    )
    db.session.add(reserva)
    db.session.commit()
    return reserva


# ==========================================
# TESTS — CREAR RESERVA (POST /api/reservas)
# ==========================================

def test_crear_reserva_usuario_no_abonado(client, usuario_casual, clase_con_cupo):
    """Escenario exitoso: reserva en estado pendiente_pago con seña del 50%"""
    payload = {
        "usuario_id": usuario_casual.id,
        "clase_id": clase_con_cupo.id,
        "metodo_pago": "efectivo"
    }
    response = client.post('/api/reservas', json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['status'] == 'success'

    reserva = Reserva.query.filter_by(usuario_id=usuario_casual.id).first()
    assert reserva.estado == 'pendiente_pago'
    assert float(reserva.monto_pagado) == float(reserva.monto_total) / 2

    db.session.refresh(clase_con_cupo)
    assert clase_con_cupo.cupo_disponible == 4

def test_crear_reserva_usuario_abonado(client, usuario_abonado, clase_con_cupo):
    """Escenario exitoso: reserva de abonado queda confirmada con descuento del 20% aplicado"""
    payload = {
        "usuario_id": usuario_abonado.id,
        "clase_id": clase_con_cupo.id,
        "metodo_pago": "membresia"
    }
    response = client.post('/api/reservas', json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['status'] == 'success'

    reserva = Reserva.query.filter_by(usuario_id=usuario_abonado.id).first()
    assert reserva.estado == 'confirmada'
    assert float(reserva.monto_total) == 4000.00  # 5000 - 20%
    assert float(reserva.monto_pagado) == float(reserva.monto_total)

def test_crear_reserva_usuario_no_encontrado(client, clase_con_cupo):
    """Error: usuario inexistente → 404"""
    payload = {
        "usuario_id": 9999,
        "clase_id": clase_con_cupo.id,
        "metodo_pago": "efectivo"
    }
    response = client.post('/api/reservas', json=payload)

    assert response.status_code == 404

def test_crear_reserva_clase_no_encontrada(client, usuario_casual):
    """Error: clase inexistente → 404"""
    payload = {
        "usuario_id": usuario_casual.id,
        "clase_id": 9999,
        "metodo_pago": "efectivo"
    }
    response = client.post('/api/reservas', json=payload)

    assert response.status_code == 404

def test_crear_reserva_sin_cupo(client, usuario_casual, clase_sin_cupo):
    """RN: no se puede reservar una clase sin cupo disponible → 409"""
    payload = {
        "usuario_id": usuario_casual.id,
        "clase_id": clase_sin_cupo.id,
        "metodo_pago": "efectivo"
    }
    response = client.post('/api/reservas', json=payload)

    assert response.status_code == 409


# ==========================================
# TESTS — CANCELAR RESERVA (PUT /api/reservas/<id>)
# ==========================================

def test_cancelar_reserva_sin_header(client, reserva_cancelable_mas_24h):
    """Error: falta el header X-User-Id → 400"""
    response = client.put(f'/api/reservas/{reserva_cancelable_mas_24h.id}')

    assert response.status_code == 400

def test_cancelar_reserva_no_encontrada(client, usuario_casual):
    """Error: reserva inexistente → 404"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.put('/api/reservas/9999', headers=headers)

    assert response.status_code == 404

def test_cancelar_reserva_no_es_suya(client, usuario_abonado, reserva_cancelable_mas_24h):
    """RN: un usuario no puede cancelar la reserva de otro → 403"""
    headers = {'X-User-Id': str(usuario_abonado.id)}
    response = client.put(f'/api/reservas/{reserva_cancelable_mas_24h.id}', headers=headers)

    assert response.status_code == 403

def test_cancelar_reserva_ya_cancelada(client, usuario_casual, reserva_cancelable_mas_24h):
    """RN: no se puede cancelar una reserva ya cancelada → 409"""
    reserva_cancelable_mas_24h.estado = 'cancelada_usuario'
    db.session.commit()

    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.put(f'/api/reservas/{reserva_cancelable_mas_24h.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 409
    assert data['message'] == 'La reserva ya se encuentra cancelada'

def test_cancelar_reserva_fuera_de_limite(client, usuario_casual, reserva_no_cancelable):
    """RN: no se puede cancelar dentro de la hora previa al inicio de la clase → 409"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.put(f'/api/reservas/{reserva_no_cancelable.id}', headers=headers)

    assert response.status_code == 409

def test_cancelar_reserva_no_abonado_mas_24h(client, usuario_casual, reserva_cancelable_mas_24h):
    """RN: cancelación con más de 24h de anticipación → se devuelve la seña (monto_pagado = 0)"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.put(f'/api/reservas/{reserva_cancelable_mas_24h.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'

    db.session.refresh(reserva_cancelable_mas_24h)
    assert reserva_cancelable_mas_24h.estado == 'cancelada_usuario'
    assert float(reserva_cancelable_mas_24h.monto_pagado) == 0.00

def test_cancelar_reserva_no_abonado_entre_1h_y_24h(client, usuario_casual, reserva_cancelable_entre_1h_y_24h):
    """RN: cancelación dentro de las 24h previas → NO se devuelve la seña"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.put(f'/api/reservas/{reserva_cancelable_entre_1h_y_24h.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'

    db.session.refresh(reserva_cancelable_entre_1h_y_24h)
    assert reserva_cancelable_entre_1h_y_24h.estado == 'cancelada_usuario'
    assert float(reserva_cancelable_entre_1h_y_24h.monto_pagado) == 2500.00

def test_cancelar_reserva_abonado(client, usuario_abonado, reserva_abonado_cancelable):
    """RN: cancelación de abonado incrementa el contador de cancelaciones del mes"""
    ahora = datetime.now()
    credito = Credito.query.filter_by(
        usuario_id=usuario_abonado.id,
        mes=ahora.month,
        anio=ahora.year
    ).first()
    cancelaciones_previas = credito.cancelaciones

    headers = {'X-User-Id': str(usuario_abonado.id)}
    response = client.put(f'/api/reservas/{reserva_abonado_cancelable.id}', headers=headers)

    assert response.status_code == 200

    db.session.refresh(credito)
    assert credito.cancelaciones == cancelaciones_previas + 1

def test_cancelar_reserva_restaura_cupo(client, usuario_casual, reserva_cancelable_mas_24h):
    """RN: al cancelar una reserva se restaura el cupo de la clase"""
    clase = db.session.get(Clase, reserva_cancelable_mas_24h.clase_id)
    cupo_previo = clase.cupo_disponible

    headers = {'X-User-Id': str(usuario_casual.id)}
    client.put(f'/api/reservas/{reserva_cancelable_mas_24h.id}', headers=headers)

    db.session.refresh(clase)
    assert clase.cupo_disponible == cupo_previo + 1


# ==========================================
# TESTS — VER RESERVAS (GET /api/reservas)
# ==========================================

def test_ver_reservas_sin_parametro(client):
    """Error: falta el parámetro usuario_id → 400"""
    response = client.get('/api/reservas')

    assert response.status_code == 400

def test_ver_reservas_exitoso(client, usuario_casual, reserva_cancelable_mas_24h):
    """Escenario exitoso: retorna reservas activas y cancelables del usuario"""
    response = client.get(f'/api/reservas?usuario_id={usuario_casual.id}')
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert len(data['reservas']) == 1
    assert 'nombre_actividad' in data['reservas'][0]
    assert 'fecha' in data['reservas'][0]
    assert 'estado' in data['reservas'][0]

def test_ver_reservas_muestra_canceladas(client, usuario_casual, reserva_cancelable_mas_24h):
    """Las reservas canceladas aparecen en el listado con cancelable=False"""
    reserva_cancelable_mas_24h.estado = 'cancelada_usuario'
    db.session.commit()

    response = client.get(f'/api/reservas?usuario_id={usuario_casual.id}')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data['reservas']) == 1
    assert data['reservas'][0]['estado'] == 'cancelada_usuario'
    assert data['reservas'][0]['cancelable'] == False

def test_ver_reservas_usuario_sin_reservas(client, usuario_casual):
    """Escenario: usuario sin reservas → lista vacía"""
    response = client.get(f'/api/reservas?usuario_id={usuario_casual.id}')
    data = response.get_json()

    assert response.status_code == 200
    assert data['reservas'] == []
