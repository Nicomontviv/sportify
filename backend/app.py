import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text
from models import db, Usuario  # <-- Importamos db y el modelo Usuario desde models.py

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la app con la configuración de la base de datos
db.init_app(app)

@app.route('/api/test-db', methods=['GET'])
def test_db_connection():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "status": "success",
            "message": "¡Conexión exitosa entre Flask y MySQL!"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al conectar con la base de datos: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)