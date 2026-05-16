from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instanciamos db para poder usarlo en este archivo
db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_alta = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relación inversa para acceder a los créditos mensuales del usuario
    creditos = db.relationship('Credito', backref='usuario', lazy=True)

    # El flag dinámico en el backend que charlamos antes
    @property
    def is_abonado_actual(self):
        ahora = datetime.now()
        # Buscamos si tiene un registro de crédito pago para el mes y año actual
        credito_actual = Credito.query.filter_by(
            usuario_id=self.id,
            mes=ahora.month,
            anio=ahora.year,
            pagado=True,
            descuento_activo=True
        ).first()
        return credito_actual is not None


class Credito(db.Model):
    __tablename__ = 'credito'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    monto_descuento = db.Column(db.Numeric(5, 2), nullable=False, default=20.00)
    mes = db.Column(db.Integer, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    pagado = db.Column(db.Boolean, nullable=False, default=False)
    fecha_pago = db.Column(db.DateTime, nullable=True)
    cancelaciones = db.Column(db.Integer, nullable=False, default=0)
    descuento_activo = db.Column(db.Boolean, nullable=False, default=True)