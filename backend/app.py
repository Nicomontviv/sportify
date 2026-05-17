import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from models import db

# Importamos los Blueprints desde nuestra subcarpeta
from routes.auth import auth_bp
from routes.actividades import actividades_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# REGISTRO DE BLUEPRINTS (Aquí definimos los prefijos de las URLs)
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(actividades_bp, url_prefix='/api/actividades')

if __name__ == '__main__':
    app.run(debug=True, port=5000)