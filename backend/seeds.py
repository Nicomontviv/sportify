import os
from datetime import date, datetime, time
from app import app, db
from models import Usuario, Administrador, Actividad, Turno, Reserva

def cargar_datos_base():
    print("🧼 [1/4] Limpiando residuos de turnos anteriores...")
    with app.app_context():
        try:
            db.session.query(Reserva).delete()
            db.session.query(Turno).delete()
            db.session.commit()
            print("✔️ Tablas de turnos limpias.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Alerta al limpiar (puede no haber datos todavía): {str(e)}")

    print("👤 [2/4] Verificando usuario Administrador...")
    with app.app_context():
        admin_email = "admin@sportify.com"
        admin = Usuario.query.filter_by(email=admin_email).first()

        if not admin:
            admin = Usuario(
                nombre="Nicolás",
                apellido="Montanari",
                dni="12345678",
                email=admin_email,
                password_hash="admin123",
                fecha_nacimiento=date(1995, 10, 10)
            )
            db.session.add(admin)
            db.session.flush()
            perfil_admin = Administrador(usuario_id=admin.id, nivel_acceso="total")
            db.session.add(perfil_admin)
            db.session.commit()
            print("✔️ Usuario Administrador creado.")
        else:
            print("info: El administrador ya existía.")

    print("🏋️ [3/4] Forzando activación de disciplinas base...")
    with app.app_context():
        # NOTA: precio_base no existe en la tabla actividad del SQL.
        # Solo se usan: nombre, descripcion, activa.
        actividades_iniciales = [
            {"nombre": "Fútbol",  "descripcion": "Canchas de césped sintético para fútbol 5 y 11."},
            {"nombre": "Básquet", "descripcion": "Cancha cubierta de piso flotante profesional."},
            {"nombre": "Vóley",   "descripcion": "Turnos para vóley mixto e institucional."},
            {"nombre": "Pádel",   "descripcion": "Canchas de blindex de última generación."}
        ]

        for act_data in actividades_iniciales:
            act = Actividad.query.filter_by(nombre=act_data["nombre"]).first()
            if not act:
                nueva_act = Actividad(
                    nombre=act_data["nombre"],
                    descripcion=act_data["descripcion"],
                    activa=True
                )
                db.session.add(nueva_act)
            else:
                act.activa = True
                act.descripcion = act_data["descripcion"]

        db.session.commit()
        print("✔️ ¡ÉXITO! Todas las actividades quedaron guardadas en estado ACTIVO.")

    print("📅 [4/4] Montando escenarios relacionales para la Demo...")
    with app.app_context():
        try:
            voley_act  = Actividad.query.filter_by(nombre="Vóley").first()
            padel_act  = Actividad.query.filter_by(nombre="Pádel").first()
            admin_user = Usuario.query.filter_by(email="admin@sportify.com").first()

            # Escenario 1: Vóley libre (12 cupos disponibles)
            turno_voley = Turno(
                actividad_id=voley_act.id,
                fecha=date(2026, 6, 1),
                horario_inicio=time(18, 0),
                horario_fin=time(19, 0),
                activo=True,
                cupo_maximo=12,
                cupo_disponible=12
            )
            db.session.add(turno_voley)

            # Escenario 2: Pádel con 1 lugar ya ocupado (4 max, 3 disponibles)
            turno_padel = Turno(
                actividad_id=padel_act.id,
                fecha=date(2026, 6, 2),
                horario_inicio=time(19, 0),
                horario_fin=time(20, 0),
                activo=True,
                cupo_maximo=4,
                cupo_disponible=3
            )
            db.session.add(turno_padel)
            db.session.flush()

            # Reserva del admin para el turno de Pádel
            # Columnas según el SQL: turno_id, usuario_id, estado, metodo_pago, monto_total, monto_pagado
            reserva_padel = Reserva(
                turno_id=turno_padel.id,
                usuario_id=admin_user.id,
                estado='confirmada',        # ENUM válido: confirmada | cancelada_usuario | cancelada_centro | pendiente_pago | asistio | ausente
                metodo_pago='mercado_pago', # ENUM válido: mercado_pago | efectivo | membresia
                monto_total=16000.00,
                monto_pagado=5000.00        # seña parcial
            )
            db.session.add(reserva_padel)
            db.session.commit()
            print("✔️ Escenarios de turnos acoplados sin errores.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Nota: No se pudieron montar los turnos de prueba por una desincronización de columnas: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        cargar_datos_base()