import pytest
from datetime import date
from models import db, Actividad, Usuario, Administrador

# ==========================================
# FIXTURES LOCALES (Datos de prueba)
# ==========================================
@pytest.fixture
def admin_user(app_context):
    """Crea un usuario administrador falso para poder pasar las validaciones"""
    # Creamos un usuario base
    user = Usuario(
        nombre="Admin", apellido="Prueba", dni="12345678", 
        email="admin@test.com", password_hash="hash", fecha_nacimiento=date(1990, 1, 1)
    )
    db.session.add(user)
    db.session.commit()
    
    # Lo convertimos en administrador
    admin = Administrador(usuario_id=user.id, nivel_acceso="total")
    db.session.add(admin)
    db.session.commit()
    
    return user

@pytest.fixture
def actividad_base(app_context):
    """Crea una actividad de prueba en la base de datos"""
    act = Actividad(nombre="Crossfit Test", precio_base=15000.0, descripcion="Prueba", activa=True)
    db.session.add(act)
    db.session.commit()
    return act

# ==========================================
# TESTS PARA GET (Obtener Actividades)
# ==========================================
def test_obtener_actividades_exito(client, actividad_base):
    """Prueba que el endpoint GET devuelva la lista de actividades"""
    response = client.get('/api/actividades')
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert len(data['actividades']) > 0
    
    # En lugar de fijarnos en la posición 0, buscamos si nuestra actividad está en la lista
    nombres_actividades = [act['nombre'] for act in data['actividades']]
    assert "Crossfit Test" in nombres_actividades

# ==========================================
# TESTS PARA POST (Crear Actividad)
# ==========================================
def test_crear_actividad_exito(client, admin_user):
    """Prueba crear una actividad mandando el X-User-Id correcto"""
    # El POST requiere que el ID del usuario llegue en el header 'X-User-Id'
    headers = {'X-User-Id': str(admin_user.id)}
    payload = {
        "nombre": "Zumba",
        "precio_base": 12000.0,
        "descripcion": "Clase de baile"
    }
    
    response = client.post('/api/actividades', headers=headers, json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data['status'] == 'success'
    
    # Verificamos que realmente se guardó en la base de datos
    actividad_db = Actividad.query.filter_by(nombre="Zumba").first()
    assert actividad_db is not None

def test_crear_actividad_sin_permisos(client):
    """Prueba que un usuario no admin reciba un error 403"""
    # Mandamos un ID que no existe en la tabla Administrador
    headers = {'X-User-Id': '999'} 
    payload = {"nombre": "Yoga", "precio_base": 10000.0}
    
    response = client.post('/api/actividades', headers=headers, json=payload)
    data = response.get_json()

    # Tu código devuelve un 403 si el usuario no es administrador
    assert response.status_code == 403
    assert data['message'] == "No autorizado. No sos administrador."

# ==========================================
# TESTS PARA PUT (Modificar Actividad)
# ==========================================
def test_modificar_actividad_exito(client, actividad_base):
    """Prueba modificar una actividad existente"""
    # El PUT requiere el header 'X-User-Role' igual a 'admin'
    headers = {'X-User-Role': 'admin'}
    payload = {
        "nombre": "Crossfit Actualizado",
        "precio_base": 18000.0,
        "descripcion": "Nueva descripcion"
    }
    
    response = client.put(f'/api/actividades/{actividad_base.id}', headers=headers, json=payload)
    
    assert response.status_code == 200
    
    # Verificamos el cambio en la base
    db.session.refresh(actividad_base)
    assert actividad_base.nombre == "Crossfit Actualizado"
    assert actividad_base.precio_base == 18000.0

def test_modificar_actividad_inactiva_falla(client, actividad_base):
    """Prueba que no se pueda modificar una actividad dada de baja"""
    # Simulamos que la actividad está eliminada
    actividad_base.activa = False
    db.session.commit()
    
    headers = {'X-User-Role': 'admin'}
    payload = {"nombre": "Intento Fallido", "precio_base": 100}
    
    response = client.put(f'/api/actividades/{actividad_base.id}', headers=headers, json=payload)
    data = response.get_json()

    # Tu código devuelve 400 si se intenta modificar una actividad inactiva
    assert response.status_code == 400
    assert "eliminada" in data['message']

# ==========================================
# TESTS PARA DELETE (Eliminar Actividad)
# ==========================================
def test_eliminar_actividad_exito(client, actividad_base):
    """Prueba la baja lógica de la actividad"""
    # El DELETE también requiere el header 'X-User-Role': 'admin'
    headers = {'X-User-Role': 'admin'}
    
    response = client.delete(f'/api/actividades/{actividad_base.id}', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'success'
    
    # Verificamos que la baja lógica se aplicó
    db.session.refresh(actividad_base)
    assert actividad_base.activa is False