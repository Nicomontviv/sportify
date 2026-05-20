import os
import pytest

# 1. ENCENDEMOS EL MODO TEST ANTES DE IMPORTAR NADA
os.environ['FLASK_TESTING'] = 'True'

# 2. Ahora sí, cuando app.py se lea, va a caer en el 'if' de SQLite
from app import app as flask_app
from models import db

@pytest.fixture
def app():
    """Configura la aplicación de Flask para los tests usando una BD en memoria"""
    flask_app.config['TESTING'] = True
    
    with flask_app.app_context():
        # Creamos las tablas de cero en la memoria RAM
        db.create_all()
        yield flask_app
        
        # Al terminar todos los tests, destruimos las tablas de RAM
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Crea el cliente de pruebas para hacer las peticiones HTTP"""
    return app.test_client()

@pytest.fixture
def app_context(app):
    """Mantiene vivo el contexto para interactuar con la BD en los tests"""
    with app.app_context():
        yield