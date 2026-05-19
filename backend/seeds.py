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

    print("👤 [2/4] Forzando recreación limpia del Administrador...")
    with app.app_context():
        admin_email = "admin@sportify.com"
        
        # 1. Buscamos si ya existe el admin viejo con la contraseña rota
        admin_viejo = Usuario.query.filter_by(email=admin_email).first()
        if admin_viejo:
            # BLINDAJE: Borramos primero TODAS las reservas asociadas a este usuario
            Reserva.query.filter_by(usuario_id=admin_viejo.id).delete()
            
            # Borramos su rol por la restricción de clave foránea
            Administrador.query.filter_by(usuario_id=admin_viejo.id).delete()
            
            # Ahora sí, la base de datos nos va a dejar borrar el usuario
            db.session.delete(admin_viejo)
            db.session.commit()
            print("🧹 Viejo administrador (y sus reservas) eliminados para limpiar el texto plano.")

        # 2. Creamos el administrador de cero con hash real garantizado
        from werkzeug.security import generate_password_hash
        
        admin = Usuario(
            nombre="Nicolás",
            apellido="Montanari",
            dni="12345678",
            email=admin_email,
            password_hash=generate_password_hash("admin123"),
            fecha_nacimiento=date(1995, 10, 10)
        )
        db.session.add(admin)
        db.session.flush() # Obtenemos el ID dinámico antes del commit
        
        # 3. Le asignamos el perfil de Administrador (esto activa tu vista en React)
        perfil_admin = Administrador(usuario_id=admin.id, nivel_acceso="total")
        db.session.add(perfil_admin)
        db.session.commit()
        print("✔️ ¡Usuario Administrador creado de cero con contraseña encriptada!")

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

            # Escenario 1: Turno (plantilla) de Vóley los lunes 18-19hs, cupo 12.
            turno_voley = Turno(
                actividad_id=voley_act.id,
                dia_semana='lunes',
                horario_inicio=time(18, 0),
                horario_fin=time(19, 0),
                cupo_maximo=12,
                activo=True
            )
            db.session.add(turno_voley)

            # Escenario 2: Turno (plantilla) de Pádel los martes 19-20hs, cupo 4.
            turno_padel = Turno(
                actividad_id=padel_act.id,
                dia_semana='martes',
                horario_inicio=time(19, 0),
                horario_fin=time(20, 0),
                cupo_maximo=4,
                activo=True
            )
            db.session.add(turno_padel)
            db.session.flush()  # necesitamos los IDs para generar clases

            # Generamos las clases (instancias con fecha) para junio 2026 a partir
            # de cada turno. El helper crea una Clase por cada fecha del mes que
            # coincida con el dia_semana del turno.
            clases_voley = generar_clases_para_mes(turno_voley, 2026, 6)
            clases_padel = generar_clases_para_mes(turno_padel, 2026, 6)

            for c in clases_voley + clases_padel:
                db.session.add(c)
            db.session.flush()

            # Simulamos que el admin ya reservó la primera clase de Pádel del mes,
            # así dejamos un escenario con una reserva concreta para la demo.
            primera_clase_padel = clases_padel[0] if clases_padel else None
            if primera_clase_padel:
                primera_clase_padel.cupo_disponible -= 1  # consumimos un lugar
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
            print(f"✔️ Escenarios montados: 2 turnos (plantillas), "
                  f"{len(clases_voley) + len(clases_padel)} clases generadas para junio.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Nota: No se pudieron montar los turnos de prueba: {str(e)}")
if __name__ == "__main__":
    with app.app_context():
        cargar_datos_base()