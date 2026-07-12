import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from models import db

# Importamos los Blueprints desde nuestra subcarpeta
from routes.auth import auth_bp
from routes.actividades import actividades_bp
from routes.reportes import reportes_bp
from routes.turnos import turnos_bp  # NUEVO
from routes.pagos import pagos_bp
from routes.reservas import reservas_bp
# Importar el nuevo archivo
from routes.lista_espera import lista_espera_bp
from routes.asistencia import asistencia_bp


load_dotenv()

app = Flask(__name__)
CORS(app)
# Verificamos si estamos corriendo tests
if os.environ.get('FLASK_TESTING') == 'True':
    # Base de datos temporal en RAM
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    # Tu conexión a MySQL real de siempre
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# REGISTRO DE BLUEPRINTS
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(actividades_bp, url_prefix='/api/actividades')
app.register_blueprint(turnos_bp, url_prefix='/api/turnos')  # NUEVO
app.register_blueprint(pagos_bp, url_prefix='/api/pagos')
app.register_blueprint(reservas_bp, url_prefix='/api/reservas')
app.register_blueprint(lista_espera_bp, url_prefix='/api/lista-espera')
app.register_blueprint(asistencia_bp, url_prefix='/api/asistencia')
app.register_blueprint(reportes_bp)


if __name__ == '__main__':
    app.run(debug=True, port=5000)