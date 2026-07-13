import pytest
from datetime import date, datetime, time, timedelta
from models import db, Usuario, Credito, Actividad, Turno, Clase, Reserva

# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def usuario_casual(app_context):
    user = Usuario(
        nombre="Juan", apellido="Perez", dni="11111111",
        email="casual_cancelacion@test.com", password_hash="hash",
        fecha_nacimiento=date(1995, 3, 20), activo=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def usuario_abonado(app_context):
    user = Usuario(
        nombre="Carlos", apellido="Gomez", dni="22222222",
        email="abonado_cancelacion@test.com", password_hash="hash",
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
        cancelaciones=0,
        clases_a_favor=0
    )
    db.session.add(credito)
    db.session.commit()
    return user

@pytest.fixture
def actividad_base(app_context):
    act = Actividad(nombre="Cancelacion Test", precio_base=10000.0, activa=True)
    db.session.add(act)
    db.session.commit()
    return act

@pytest.fixture
def reserva_casual_mas24h(app_context, usuario_casual, actividad_base):
    """Reserva casual con clase en +24hs → devuelve seña"""
    turno = Turno(actividad_id=actividad_base.id, dia_semana='lunes',
                  horario_inicio=time(10, 0), horario_fin=time(11, 0),
                  cupo_maximo=10, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=date.today() + timedelta(days=3),
                  cupo_disponible=5, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_casual.id,
                      estado='confirmada', metodo_pago='efectivo',
                      monto_total=10000.00, monto_pagado=5000.00)
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_casual_menos24h(app_context, usuario_casual, actividad_base):
    """Reserva casual con clase en 3hs → NO devuelve seña"""
    inicio = datetime.now() + timedelta(hours=3)
    turno = Turno(actividad_id=actividad_base.id, dia_semana='martes',
                  horario_inicio=inicio.replace(second=0, microsecond=0).time(),
                  horario_fin=(inicio + timedelta(hours=1)).replace(second=0, microsecond=0).time(),
                  cupo_maximo=10, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=inicio.date(),
                  cupo_disponible=5, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_casual.id,
                      estado='confirmada', metodo_pago='efectivo',
                      monto_total=10000.00, monto_pagado=5000.00)
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_abonado_mas48h(app_context, usuario_abonado, actividad_base):
    """Reserva abonado con clase en +48hs → genera clase a favor"""
    turno = Turno(actividad_id=actividad_base.id, dia_semana='miercoles',
                  horario_inicio=time(10, 0), horario_fin=time(11, 0),
                  cupo_maximo=10, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=date.today() + timedelta(days=5),
                  cupo_disponible=5, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_abonado.id,
                      estado='confirmada', metodo_pago='membresia',
                      monto_total=8000.00, monto_pagado=8000.00)
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_abonado_menos48h(app_context, usuario_abonado, actividad_base):
    """Reserva abonado con clase en 3hs → acumula cancelación sin clase a favor"""
    inicio = datetime.now() + timedelta(hours=3)
    turno = Turno(actividad_id=actividad_base.id, dia_semana='jueves',
                  horario_inicio=inicio.replace(second=0, microsecond=0).time(),
                  horario_fin=(inicio + timedelta(hours=1)).replace(second=0, microsecond=0).time(),
                  cupo_maximo=10, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=inicio.date(),
                  cupo_disponible=5, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_abonado.id,
                      estado='confirmada', metodo_pago='membresia',
                      monto_total=8000.00, monto_pagado=8000.00)
    db.session.add(reserva)
    db.session.commit()
    return reserva

@pytest.fixture
def reserva_abonado_tercera_cancelacion(app_context, usuario_abonado, actividad_base):
    """Abonado con 2 cancelaciones previas — la próxima dispara penalización"""
    ahora = datetime.now()
    credito = Credito.query.filter_by(
        usuario_id=usuario_abonado.id, mes=ahora.month, anio=ahora.year
    ).first()
    credito.cancelaciones = 2
    db.session.commit()

    turno = Turno(actividad_id=actividad_base.id, dia_semana='viernes',
                  horario_inicio=time(16, 0), horario_fin=time(17, 0),
                  cupo_maximo=10, activo=True)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=date.today() + timedelta(days=5),
                  cupo_disponible=5, activo=True)
    db.session.add(clase)
    db.session.commit()

    reserva = Reserva(clase_id=clase.id, usuario_id=usuario_abonado.id,
                      estado='confirmada', metodo_pago='membresia',
                      monto_total=8000.00, monto_pagado=8000.00)
    db.session.add(reserva)
    db.session.commit()
    return reserva


# ==========================================
# TESTS — CANCELACIÓN USUARIO CASUAL
# ==========================================

def test_casual_cancelacion_mas24h_devuelve_senia(client, usuario_casual, reserva_casual_mas24h):
    """Cancelación casual con más de 24hs → devuelve seña"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.put(f'/api/reservas/{reserva_casual_mas24h.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['senia_devuelta'] == True
    db.session.refresh(reserva_casual_mas24h)
    assert float(reserva_casual_mas24h.monto_pagado) == 0.00

def test_casual_cancelacion_menos24h_no_devuelve_senia(client, usuario_casual, reserva_casual_menos24h):
    """Cancelación casual con menos de 24hs → NO devuelve seña"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    response = client.put(f'/api/reservas/{reserva_casual_menos24h.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['senia_devuelta'] == False
    db.session.refresh(reserva_casual_menos24h)
    assert float(reserva_casual_menos24h.monto_pagado) == 5000.00


# ==========================================
# TESTS — CANCELACIÓN USUARIO ABONADO
# ==========================================

def test_abonado_cancelacion_mas48h_genera_clase_a_favor(client, usuario_abonado, reserva_abonado_mas48h):
    """Cancelación abonado con más de 48hs → genera clase a favor"""
    ahora = datetime.now()
    credito = Credito.query.filter_by(
        usuario_id=usuario_abonado.id, mes=ahora.month, anio=ahora.year
    ).first()
    clases_previas = credito.clases_a_favor

    headers = {'X-User-Id': str(usuario_abonado.id)}
    response = client.put(f'/api/reservas/{reserva_abonado_mas48h.id}', headers=headers)

    assert response.status_code == 200
    db.session.refresh(credito)
    assert credito.cancelaciones == 1
    assert credito.clases_a_favor == clases_previas + 1

def test_abonado_cancelacion_menos48h_no_genera_clase_a_favor(client, usuario_abonado, reserva_abonado_menos48h):
    """Cancelación abonado con menos de 48hs → acumula cancelación sin clase a favor"""
    ahora = datetime.now()
    credito = Credito.query.filter_by(
        usuario_id=usuario_abonado.id, mes=ahora.month, anio=ahora.year
    ).first()
    clases_previas = credito.clases_a_favor

    headers = {'X-User-Id': str(usuario_abonado.id)}
    response = client.put(f'/api/reservas/{reserva_abonado_menos48h.id}', headers=headers)

    assert response.status_code == 200
    db.session.refresh(credito)
    assert credito.cancelaciones == 1
    assert credito.clases_a_favor == clases_previas

def test_abonado_tercera_cancelacion_pierde_descuento(client, usuario_abonado, reserva_abonado_tercera_cancelacion):
    """3ra cancelación → descuento_activo = False y perdio_descuento = True"""
    headers = {'X-User-Id': str(usuario_abonado.id)}
    response = client.put(f'/api/reservas/{reserva_abonado_tercera_cancelacion.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['perdio_descuento'] == True

    ahora = datetime.now()
    credito = Credito.query.filter_by(
        usuario_id=usuario_abonado.id, mes=ahora.month, anio=ahora.year
    ).first()
    db.session.refresh(credito)
    assert credito.descuento_activo == False
    assert credito.cancelaciones == 3