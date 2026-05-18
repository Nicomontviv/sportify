import os
from datetime import date, datetime, time
from app import app, db
from models import Usuario, Administrador, Actividad, Turno, Reserva, Clase
from helpers.turnos_helper import generar_clases_para_mes

def cargar_datos_base():
    print("🧼 [1/4] Limpiando residuos de turnos anteriores...")
    with app.app_context():
        try:
            db.session.query(Reserva).delete()
            db.session.query(Clase).delete()  # NUEVO: limpiar clases antes que turnos por FK
            db.session.query(Turno).delete()
            db.session.commit()
            print("✔️ Tablas de turnos, clases y reservas limpias.")
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

            # 1. Crear Turno Plantilla para Vóley (Todos los lunes de junio)
            turno_voley = Turno(
                actividad_id=voley_act.id,
                dia_semana='lunes',
                horario_inicio=time(18, 0),
                horario_fin=time(19, 0),
                cupo_maximo=12,
                activo=True
            )
            db.session.add(turno_voley)

            # 2. Crear Turno Plantilla para Pádel (Todos los miércoles de junio)
            turno_padel = Turno(
                actividad_id=padel_act.id,
                dia_semana='miercoles',
                horario_inicio=time(19, 0),
                horario_fin=time(20, 0),
                cupo_maximo=4,
                activo=True
            )
            db.session.add(turno_padel)
            
            # Flush para que la DB nos devuelva los IDs de los turnos generados
            db.session.flush()

            # 3. Generar las clases concretas para Junio 2026 usando nuestro Helper
            clases_voley = generar_clases_para_mes(turno_voley, 2026, 6)
            clases_padel = generar_clases_para_mes(turno_padel, 2026, 6)

            for clase in clases_voley + clases_padel:
                db.session.add(clase)
            
            db.session.flush() # Flush para tener los IDs de las clases

            # 4. Reservar una clase específica (la primera del mes de pádel)
            # Buscamos la clase con fecha más temprana generada para pádel
            primera_clase_padel = Clase.query.filter_by(turno_id=turno_padel.id).order_by(Clase.fecha.asc()).first()
            
            if primera_clase_padel:
                # Descontamos el cupo de esa clase en particular
                primera_clase_padel.cupo_disponible -= 1
                
                # Creamos la reserva atada a la CLASE (como manda el nuevo SQL)
                reserva_padel = Reserva(
                    clase_id=primera_clase_padel.id,
                    usuario_id=admin_user.id,
                    estado='confirmada',
                    metodo_pago='mercado_pago',
                    monto_total=16000.00,
                    monto_pagado=5000.00
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