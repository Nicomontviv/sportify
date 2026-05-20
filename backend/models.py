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

    # NUEVO: Relación uno a uno con Administrador para el flujo de Login administrativo
    administrador = db.relationship('Administrador', backref='usuario', uselist=False, lazy=True)

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


# NUEVO: Modelo Administrador (Especialización de Usuario)
class Administrador(db.Model):
    __tablename__ = 'administrador'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False, unique=True)
    nivel_acceso = db.Column(db.String(50), nullable=False, default='total')


# NUEVO: Modelo Actividad con la columna precio_base requerida por la HU
class Actividad(db.Model):
    __tablename__ = 'actividad'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True) # unique=True para cumplir la Regla de Negocio 1
    descripcion = db.Column(db.Text, nullable=True)
    precio_base = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    activa = db.Column(db.Boolean, nullable=False, default=True)


# MODIFICADO: Turno ahora es la PLANTILLA recurrente (sin fecha).
# Define que "todos los <dia_semana> de <horario_inicio> a <horario_fin>
# hay <actividad> con cupo máximo X". Las instancias concretas con fecha
# viven en la tabla Clase.
class Turno(db.Model):
    __tablename__ = 'turno'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividad.id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    dia_semana = db.Column(db.Enum('lunes','martes','miercoles','jueves','viernes'), nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fin = db.Column(db.Time, nullable=False)
    cupo_maximo = db.Column(db.SmallInteger, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Relación inversa con las clases generadas a partir de este turno
    clases = db.relationship('Clase', backref='turno', lazy=True)


# NUEVO: Clase = instancia concreta de un turno con fecha puntual.
# Es a lo que reservan los usuarios. Hereda actividad, día, horario y
# cupo máximo desde Turno; solo guarda lo propio de la fecha.
class Clase(db.Model):
    __tablename__ = 'clase'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    turno_id = db.Column(db.Integer, db.ForeignKey('turno.id', onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cupo_disponible = db.Column(db.SmallInteger, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relación inversa con las reservas de esta clase puntual
    reservas = db.relationship('Reserva', backref='clase', lazy=True)


# MODIFICADO: Reserva ahora apunta a Clase (instancia con fecha),
# no a Turno (plantilla).
class Reserva(db.Model):
    __tablename__ = 'reserva'

    id = db.Column(db.Integer, primary_key=True)
    clase_id = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    #fecha_reserva = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    # ENUM estricto de tu SQL
    estado = db.Column(db.Enum('confirmada', 'cancelada_usuario', 'cancelada_centro', 'pendiente_pago', 'asistio', 'ausente'), default='pendiente_pago', nullable=False)
    metodo_pago = db.Column(db.Enum('mercado_pago', 'efectivo', 'membresia'), nullable=False)

    # Columnas de montos reales
    monto_total = db.Column(db.Numeric(10, 2), nullable=False)
    monto_pagado = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    #resultado_pago = db.Column(db.String(100))