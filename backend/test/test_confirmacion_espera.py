import pytest
from datetime import date, time, datetime, timedelta
from models import db, Usuario, Actividad, Turno, Clase, ListaEspera, Reserva

@pytest.fixture
def base_datos_test(app_context):
    """Prepara el ecosistema básico: Actividad, Turno, Clase y Usuario"""
    act = Actividad(nombre="Boxeo", precio_base=8000.0, activa=True)
    db.session.add(act)
    db.session.commit()
    
    turno = Turno(actividad_id=act.id, dia_semana='viernes', horario_inicio=time(18,0), horario_fin=time(19,0), cupo_maximo=10)
    db.session.add(turno)
    db.session.commit()
    
    clase = Clase(turno_id=turno.id, fecha=date.today(), cupo_disponible=0)
    user = Usuario(nombre="Ana", apellido="Test", dni="123", email="ana@test.com", password_hash="h", fecha_nacimiento=date(1995,1,1))
    
    db.session.add_all([clase, user])
    db.session.commit()
    
    return {"clase": clase, "user": user}

def test_escenario_1_confirmacion_dentro_del_plazo(client, base_datos_test):
    clase = base_datos_test["clase"]
    user = base_datos_test["user"]

    # Simulamos que le llegó la notificación hace 45 minutos
    hace_45_min = datetime.now() - timedelta(minutes=45)
    
    inscripcion = ListaEspera(clase_id=clase.id, usuario_id=user.id, posicion=1, estado='notificado', fecha_notificacion=hace_45_min)
    reserva = Reserva(clase_id=clase.id, usuario_id=user.id, estado='pendiente_pago', metodo_pago='efectivo', monto_total=8000.0, monto_pagado=0.0)
    
    db.session.add_all([inscripcion, reserva])
    db.session.commit()

    headers = {'X-User-Id': str(user.id)}
    response = client.post(f'/api/lista-espera/{inscripcion.id}/confirmar', headers=headers)
    data = response.get_json()

    # VERIFICACIÓN: El sistema le permite confirmar porque no pasaron 60 mins
    assert response.status_code == 200
    assert data['status'] == 'success'
    
    db.session.refresh(inscripcion)
    db.session.refresh(reserva)
    assert inscripcion.estado == 'confirmado'
    assert reserva.estado == 'confirmada'

def test_escenario_2_intento_fuera_de_plazo(client, base_datos_test):
    clase = base_datos_test["clase"]
    user = base_datos_test["user"]

    # Simulamos que la notificación llegó hace 65 minutos
    hace_65_min = datetime.now() - timedelta(minutes=65)
    
    inscripcion = ListaEspera(clase_id=clase.id, usuario_id=user.id, posicion=1, estado='notificado', fecha_notificacion=hace_65_min)
    reserva = Reserva(clase_id=clase.id, usuario_id=user.id, estado='pendiente_pago', metodo_pago='efectivo', monto_total=8000.0, monto_pagado=0.0)
    
    db.session.add_all([inscripcion, reserva])
    db.session.commit()

    headers = {'X-User-Id': str(user.id)}
    response = client.post(f'/api/lista-espera/{inscripcion.id}/confirmar', headers=headers)
    data = response.get_json()

    # VERIFICACIÓN: El sistema le rechaza el pago porque expiró el tiempo
    assert response.status_code == 400
    assert "tiempo ha expirado" in data['message']
    
    db.session.refresh(inscripcion)
    db.session.refresh(reserva)
    assert inscripcion.estado == 'expirado'
    assert reserva.estado == 'cancelada_centro'