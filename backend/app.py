import os
from flask import Flask
from flask_cors import CORS
from extensions import mail
# ...
from dotenv import load_dotenv
from models import db

from routes.auth import auth_bp
from routes.actividades import actividades_bp
from routes.turnos import turnos_bp
from routes.pagos import pagos_bp
from routes.reservas import reservas_bp
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

if os.environ.get('FLASK_TESTING') == 'True':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
mail.init_app(app)  # ← agregá esto después de configurar el mail


db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(actividades_bp, url_prefix='/api/actividades')
app.register_blueprint(turnos_bp, url_prefix='/api/turnos')
app.register_blueprint(pagos_bp, url_prefix='/api/pagos')
app.register_blueprint(reservas_bp, url_prefix='/api/reservas')
if __name__ == '__main__':
    app.run(debug=True, port=5000)