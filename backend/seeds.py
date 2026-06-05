import os
from datetime import date, datetime, time, timedelta
from app import app, db
from models import Usuario, Administrador, Actividad, Turno, Reserva, Clase, Empleado, Deposito
from helpers.turnos_helper import generar_clases_para_mes
# Seeds para la demo - Junio 2026
def cargar_datos_base():
    print("🧼 [1/4] Limpiando residuos de turnos anteriores...")
    with app.app_context():
        try:
            db.session.query(Deposito).delete()
            db.session.query(Reserva).delete()
            db.session.query(Clase).delete()
            db.session.query(Turno).delete()
            db.session.commit()
            print("✔️ Tablas de turnos, clases, reservas y depósitos limpias.")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Alerta al limpiar (puede no haber datos todavía): {str(e)}")

    print("👤 [2/4] Forzando recreación limpia del Administrador...")
    with app.app_context():
        admin_email = "admin@sportify.com"

        admin_viejo = Usuario.query.filter_by(email=admin_email).first()
        if admin_viejo:
            Reserva.query.filter_by(usuario_id=admin_viejo.id).delete()
            Administrador.query.filter_by(usuario_id=admin_viejo.id).delete()
            db.session.delete(admin_viejo)
            db.session.commit()
            print("🧹 Viejo administrador eliminado.")

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
        db.session.flush()

        perfil_admin = Administrador(usuario_id=admin.id, nivel_acceso="total")
        db.session.add(perfil_admin)
        db.session.commit()
        print("✔️ Usuario Administrador creado: admin@sportify.com / admin123")

    print("👷 [2.5/4] Creando usuario Empleado de prueba...")
    with app.app_context():
        from werkzeug.security import generate_password_hash

        empleado_email = "empleado@sportify.com"

        empleado_viejo = Usuario.query.filter_by(email=empleado_email).first()
        if empleado_viejo:
            Empleado.query.filter_by(usuario_id=empleado_viejo.id).delete()
            db.session.delete(empleado_viejo)
            db.session.commit()
            print("🧹 Viejo empleado eliminado.")

        empleado_usuario = Usuario(
            nombre="Mario",
            apellido="Gomez",
            dni="55555555",
            email=empleado_email,
            password_hash=generate_password_hash("empleado123!"),
            fecha_nacimiento=date(1990, 5, 15)
        )
        db.session.add(empleado_usuario)
        db.session.flush()

        perfil_empleado = Empleado(usuario_id=empleado_usuario.id, legajo="EMP001", cargo="Recepcionista")
        db.session.add(perfil_empleado)
        db.session.commit()
        print("✔️ Usuario Empleado creado: empleado@sportify.com / empleado123!")

    # Juan Perez — usuario casual para HU1
    print("🙋 [2.7/4] Creando usuario Casual Juan Perez (HU pagovirtual)...")
    with app.app_context():
        from werkzeug.security import generate_password_hash

        casual_email = "casual@sportify.com"

        casual_viejo = Usuario.query.filter_by(email=casual_email).first()
        if casual_viejo:
            Reserva.query.filter_by(usuario_id=casual_viejo.id).delete()
            db.session.delete(casual_viejo)
            db.session.commit()
            print("🧹 Viejo usuario Juan Perez eliminado.")

        casual_usuario = Usuario(
            nombre="Juan",
            apellido="Perez",
            dni="99999999",
            email=casual_email,
            password_hash=generate_password_hash("casual123!"),
            fecha_nacimiento=date(1995, 3, 20)
        )
        db.session.add(casual_usuario)
        db.session.commit()
        print("✔️ Usuario Casual creado: casual@sportify.com / casual123!")

    # Luis Gonzalez — usuario casual para HU pagopresencial
    print("🙋 [2.8/4] Creando usuario Casual Luis Gonzalez (HU pagopresencial)...")
    with app.app_context():
        from werkzeug.security import generate_password_hash

        luis_email = "luis@sportify.com"

        luis_viejo = Usuario.query.filter_by(email=luis_email).first()
        if luis_viejo:
            Reserva.query.filter_by(usuario_id=luis_viejo.id).delete()
            db.session.delete(luis_viejo)
            db.session.commit()
            print("🧹 Viejo usuario Luis Gonzalez eliminado.")

        luis_usuario = Usuario(
            nombre="Luis",
            apellido="Gonzalez",
            dni="88888888",
            email=luis_email,
            password_hash=generate_password_hash("luis123!"),
            fecha_nacimiento=date(1993, 6, 10)
        )
        db.session.add(luis_usuario)
        db.session.commit()
        print("✔️ Usuario Casual creado: luis@sportify.com / luis123!")

    # Gonzalo Lopez — usuario casual sin reservas
    print("🙋 [2.9/4] Creando usuario Casual Gonzalo Lopez (sin reservas)...")
    with app.app_context():
        from werkzeug.security import generate_password_hash

        gonzalo_email = "gonzalo@sportify.com"

        gonzalo_viejo = Usuario.query.filter_by(email=gonzalo_email).first()
        if not gonzalo_viejo:
            gonzalo_viejo = Usuario.query.filter_by(dni="22555111").first()
        if gonzalo_viejo:
            Reserva.query.filter_by(usuario_id=gonzalo_viejo.id).delete()
            db.session.delete(gonzalo_viejo)
            db.session.commit()
            print("🧹 Viejo usuario Gonzalo Lopez eliminado.")

        gonzalo_usuario = Usuario(
            nombre="Gonzalo",
            apellido="Lopez",
            dni="22555111",
            email=gonzalo_email,
            password_hash=generate_password_hash("gonzalo123!"),
            fecha_nacimiento=date(1988, 11, 5)
        )
        db.session.add(gonzalo_usuario)
        db.session.commit()
        print("✔️ Usuario Casual creado: gonzalo@sportify.com / gonzalo123! (sin reservas)")

    print("🏋️ [3/4] Forzando activación de disciplinas base...")
    with app.app_context():
        actividades_iniciales = [
            {"nombre": "Fútbol",  "descripcion": "Canchas de césped sintético para fútbol 5 y 11.", "precio": 20000.0},
            {"nombre": "Básquet", "descripcion": "Cancha cubierta de piso flotante profesional.",    "precio": 18000.0},
            {"nombre": "Vóley",   "descripcion": "Turnos para vóley mixto e institucional.",         "precio": 18000.0},
            {"nombre": "Pádel",   "descripcion": "Canchas de blindex de última generación.",         "precio": 16000.0}
        ]

        for act_data in actividades_iniciales:
            act = Actividad.query.filter(
                db.func.lower(Actividad.nombre) == act_data["nombre"].lower()
            ).first()
            if not act:
                nueva_act = Actividad(
                    nombre=act_data["nombre"],
                    descripcion=act_data["descripcion"],
                    precio_base=act_data["precio"],
                    activa=True
                )
                db.session.add(nueva_act)
            else:
                act.nombre = act_data["nombre"]
                act.activa = True
                act.descripcion = act_data["descripcion"]
                act.precio_base = act_data["precio"]

        db.session.commit()
        print("✔️ ¡ÉXITO! Todas las actividades quedaron guardadas en estado ACTIVO.")

    print("📅 [4/4] Montando escenarios relacionales para la Demo...")
    with app.app_context():
        try:
            futbol_act  = Actividad.query.filter_by(nombre="Fútbol").first()
            voley_act   = Actividad.query.filter_by(nombre="Vóley").first()
            padel_act   = Actividad.query.filter_by(nombre="Pádel").first()
            basquet_act = Actividad.query.filter_by(nombre="Básquet").first()

            casual_user  = Usuario.query.filter_by(email="casual@sportify.com").first()   # Juan Perez
            luis_user    = Usuario.query.filter_by(email="luis@sportify.com").first()     # Luis Gonzalez

            turno_futbol_viernes = Turno(
                actividad_id=futbol_act.id,
                dia_semana='viernes',
                horario_inicio=time(18, 0),
                horario_fin=time(19, 0),
                cupo_maximo=12,
                activo=True
            )
            db.session.add(turno_futbol_viernes)

            turno_voley_martes = Turno(
                actividad_id=voley_act.id,
                dia_semana='martes',
                horario_inicio=time(17, 0),
                horario_fin=time(18, 0),
                cupo_maximo=12,
                activo=True
            )
            db.session.add(turno_voley_martes)

            turno_padel_miercoles = Turno(
                actividad_id=padel_act.id,
                dia_semana='miercoles',
                horario_inicio=time(19, 0),
                horario_fin=time(20, 0),
                cupo_maximo=4,
                activo=True
            )
            db.session.add(turno_padel_miercoles)

            turno_basquet_jueves = Turno(
                actividad_id=basquet_act.id,
                dia_semana='jueves',
                horario_inicio=time(14, 0),
                horario_fin=time(15, 0),
                cupo_maximo=12,
                activo=True
            )
            db.session.add(turno_basquet_jueves)

            turno_futbol_lunes = Turno(
                actividad_id=futbol_act.id,
                dia_semana='lunes',
                horario_inicio=time(10, 0),
                horario_fin=time(11, 0),
                cupo_maximo=12,
                activo=True
            )
            db.session.add(turno_futbol_lunes)

            db.session.flush()

            clases_futbol_viernes  = generar_clases_para_mes(turno_futbol_viernes, 2026, 6)
            clases_voley_martes    = generar_clases_para_mes(turno_voley_martes, 2026, 6)
            clases_padel_miercoles = generar_clases_para_mes(turno_padel_miercoles, 2026, 6)
            clases_basquet_jueves  = generar_clases_para_mes(turno_basquet_jueves, 2026, 6)
            clases_futbol_lunes    = generar_clases_para_mes(turno_futbol_lunes, 2026, 6)

            for c in (clases_futbol_viernes + clases_voley_martes + clases_padel_miercoles +
                      clases_basquet_jueves + clases_futbol_lunes):
                db.session.add(c)
            db.session.flush()

            if clases_futbol_viernes and casual_user:
                clases_futbol_viernes[1].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_futbol_viernes[1].id,
                    usuario_id=casual_user.id,
                    estado='pendiente_pago',
                    metodo_pago='tarjeta_virtual',
                    monto_total=20000.00,
                    monto_pagado=10000.00
                ))

            if clases_voley_martes and casual_user:
                clases_voley_martes[1].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_voley_martes[1].id,
                    usuario_id=casual_user.id,
                    estado='pendiente_pago',
                    metodo_pago='tarjeta_virtual',
                    monto_total=18000.00,
                    monto_pagado=9000.00
                ))

            if clases_padel_miercoles and casual_user:
                clases_padel_miercoles[0].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_padel_miercoles[0].id,
                    usuario_id=casual_user.id,
                    estado='pendiente_pago',
                    metodo_pago='tarjeta_virtual',
                    monto_total=16000.00,
                    monto_pagado=8000.00
                ))

            if clases_basquet_jueves and casual_user:
                clases_basquet_jueves[0].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_basquet_jueves[0].id,
                    usuario_id=casual_user.id,
                    estado='pendiente_pago',
                    metodo_pago='tarjeta_virtual',
                    monto_total=18000.00,
                    monto_pagado=9000.00
                ))

            if clases_futbol_lunes and casual_user:
                clases_futbol_lunes[0].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_futbol_lunes[0].id,
                    usuario_id=casual_user.id,
                    estado='pendiente_pago',
                    metodo_pago='tarjeta_virtual',
                    monto_total=20000.00,
                    monto_pagado=10000.00
                ))

            # Escenario: reserva activa pero NO cancelable (clase comienza en 30 min)
            # cancelable = now < inicio_clase - 1h = now < (now+30min-1h) = False
            DIAS_ES = {0: 'lunes', 1: 'martes', 2: 'miercoles', 3: 'jueves', 4: 'viernes', 5: 'sabado', 6: 'domingo'}
            ahora_seed = datetime.now()
            inicio_nc = (ahora_seed + timedelta(minutes=30)).replace(second=0, microsecond=0)
            fin_nc    = (ahora_seed + timedelta(minutes=90)).replace(second=0, microsecond=0)

            turno_basquet_nc = Turno(
                actividad_id=basquet_act.id,
                dia_semana=DIAS_ES[ahora_seed.weekday()],
                horario_inicio=inicio_nc.time(),
                horario_fin=fin_nc.time(),
                cupo_maximo=12,
                activo=True
            )
            db.session.add(turno_basquet_nc)
            db.session.flush()

            clase_basquet_nc = Clase(
                turno_id=turno_basquet_nc.id,
                fecha=date.today(),
                cupo_disponible=11,
                activo=True
            )
            db.session.add(clase_basquet_nc)
            db.session.flush()

            if casual_user:
                db.session.add(Reserva(
                    clase_id=clase_basquet_nc.id,
                    usuario_id=casual_user.id,
                    estado='pendiente_pago',
                    metodo_pago='tarjeta_virtual',
                    monto_total=18000.00,
                    monto_pagado=9000.00
                ))

            if clases_futbol_viernes and luis_user:
                clases_futbol_viernes[1].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_futbol_viernes[1].id,
                    usuario_id=luis_user.id,
                    estado='pendiente_pago',
                    metodo_pago='efectivo',
                    monto_total=20000.00,
                    monto_pagado=10000.00
                ))

            if clases_voley_martes and luis_user:
                clases_voley_martes[1].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_voley_martes[1].id,
                    usuario_id=luis_user.id,
                    estado='pendiente_pago',
                    metodo_pago='efectivo',
                    monto_total=18000.00,
                    monto_pagado=9000.00
                ))

            if clases_padel_miercoles and luis_user:
                clases_padel_miercoles[1].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_padel_miercoles[1].id,
                    usuario_id=luis_user.id,
                    estado='pendiente_pago',
                    metodo_pago='efectivo',
                    monto_total=16000.00,
                    monto_pagado=8000.00
                ))

            if clases_basquet_jueves and luis_user:
                clases_basquet_jueves[1].cupo_disponible -= 1
                db.session.add(Reserva(
                    clase_id=clases_basquet_jueves[1].id,
                    usuario_id=luis_user.id,
                    estado='pendiente_pago',
                    metodo_pago='efectivo',
                    monto_total=18000.00,
                    monto_pagado=9000.00
                ))

            db.session.commit()
            print("✔️ Escenarios cargados para HU pago virtual (Juan Perez) y HU pago presencial (Luis Gonzalez).")
            print("✔️ Gonzalo Lopez creado sin reservas (escenario 10 HU pago virtual y escenario 5 HU pago presencial).")
            print("")
            print("👤 Usuarios de prueba:")
            print("   Admin:    admin@sportify.com     / admin123       (DNI 12345678)")
            print("   Empleado: empleado@sportify.com  / empleado123!   (DNI 55555555)")
            print("   HUpagovirtual:      casual@sportify.com    / casual123!     (Juan Perez    DNI 99999999)")
            print("   HUpagopresencial:      luis@sportify.com      / luis123!       (Luis Gonzalez DNI 88888888)")
            print("   Sin reserva:  gonzalo@sportify.com   / gonzalo123!    (Gonzalo Lopez DNI 22555111)")

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Nota: No se pudieron cargar los turnos de prueba: {str(e)}")

if __name__ == "__main__":
    with app.app_context():
        cargar_datos_base()