import pytest
from datetime import date, time
from models import db, Usuario, Actividad, Turno, Clase, ListaEspera

# ==========================================
# FIXTURES LOCALES (Datos de prueba para la Lista)
# ==========================================
@pytest.fixture
def usuario_casual(app_context):
    """Crea un usuario estándar para las pruebas de reserva"""
    user = Usuario(
        nombre="Juan", apellido="Perez", dni="99887766", 
        email="juan.espera@test.com", password_hash="hash", fecha_nacimiento=date(1995, 1, 1)
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def clase_sin_cupo(app_context):
    """Crea la cadena completa: Actividad -> Turno -> Clase (LLENA)"""
    act = Actividad(nombre="Pádel Test", precio_base=15000.0, activa=True)
    db.session.add(act)
    db.session.commit()
    
    turno = Turno(actividad_id=act.id, dia_semana='miercoles', horario_inicio=time(19, 0), horario_fin=time(20, 0), cupo_maximo=4)
    db.session.add(turno)
    db.session.commit()

    # ACÁ ESTÁ LA CLAVE: cupo_disponible = 0
    clase = Clase(turno_id=turno.id, fecha=date.today(), cupo_disponible=0)
    db.session.add(clase)
    db.session.commit()
    return clase

@pytest.fixture
def clase_con_cupo(app_context):
    """Crea una clase que todavía tiene lugares libres"""
    act = Actividad(nombre="Tenis Test", precio_base=12000.0, activa=True)
    db.session.add(act)
    db.session.commit()
    
    turno = Turno(actividad_id=act.id, dia_semana='jueves', horario_inicio=time(10, 0), horario_fin=time(11, 0), cupo_maximo=4)
    db.session.add(turno)
    db.session.commit()

    clase = Clase(turno_id=turno.id, fecha=date.today(), cupo_disponible=2)
    db.session.add(clase)
    db.session.commit()
    return clase

# ==========================================
# TESTS DE LOS CRITERIOS DE ACEPTACIÓN
# ==========================================

def test_unirse_lista_espera_exito(client, usuario_casual, clase_sin_cupo):
    """Escenario 1: Inscripción exitosa (Positivo)"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {'clase_id': clase_sin_cupo.id}

    response = client.post('/api/lista-espera', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['status'] == 'success'
    assert "correctamente" in data['message']

    # Verificamos que se haya guardado en la base de datos con posición 1
    inscripcion = ListaEspera.query.filter_by(usuario_id=usuario_casual.id, clase_id=clase_sin_cupo.id).first()
    assert inscripcion is not None
    assert inscripcion.posicion == 1
    assert inscripcion.estado == 'en_espera'

def test_unirse_lista_espera_duplicado(client, usuario_casual, clase_sin_cupo):
    """Escenario 2: Usuario ya inscripto en espera"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {'clase_id': clase_sin_cupo.id}

    # 1. Hacemos la primera inscripción (Debe funcionar)
    client.post('/api/lista-espera', headers=headers, json=payload)

    # 2. Intentamos inscribirnos exactamente de nuevo a la misma clase
    response = client.post('/api/lista-espera', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['status'] == 'error'
    assert "Ya te encuentras en espera" in data['message']

def test_unirse_lista_rechazado_por_cupo_libre(client, usuario_casual, clase_con_cupo):
    """Regla de Negocio: No permitir lista de espera si hay lugares disponibles"""
    headers = {'X-User-Id': str(usuario_casual.id)}
    payload = {'clase_id': clase_con_cupo.id}

    response = client.post('/api/lista-espera', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert data['status'] == 'error'
    assert "aún tiene cupos disponibles" in data['message']