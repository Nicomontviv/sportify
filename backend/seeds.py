import os
from datetime import date, datetime
from app import app, db
from models import Usuario, Administrador, Actividad, Credito

def cargar_datos_base():
    print("🌱 Iniciando la carga de datos base (Seeds) para Sportify...")

    # 1. CREAR USUARIO ADMINISTRADOR DE PRUEBA
    admin_email = "admin@sportify.com"
    admin_existente = Usuario.query.filter_by(email=admin_email).first()

    if not admin_existente:
        nuevo_admin = Usuario(
            nombre="Nicolás",
            apellido="Montanari",
            dni="12345678",
            email=admin_email,
            password_hash="admin123", # Para la Demo 1 validamos en texto plano directo
            fecha_nacimiento=date(1995, 10, 10)
        )
        db.session.add(nuevo_admin)
        db.session.flush() # Flush para obtener el ID antes del commit

        perfil_admin = Administrador(
            usuario_id=nuevo_admin.id,
            nivel_acceso="total"
        )
        db.session.add(perfil_admin)
        print("✔️ Usuario Administrador de prueba creado con éxito.")
    else:
        print("ℹ️ El usuario administrador ya existía en el sistema.")

    # 2. CREAR ACTIVIDADES BASE EXIGIDAS POR EL NEGOCIO
    # Dejamos 'Fútbol' cargada de antemano para poder forzar el Escenario 2 de duplicados
    actividades_iniciales = [
        {"nombre": "Fútbol", "precio_base": 15000.00, "descripcion": "Canchas de césped sintético para fútbol 5 y 11."},
        {"nombre": "Básquet", "precio_base": 14000.00, "descripcion": "Cancha cubierta de piso flotante profesional."},
        {"nombre": "Vóley", "precio_base": 12000.00, "descripcion": "Turnos para vóley mixto e institucional."},
        {"nombre": "Pádel", "precio_base": 16000.00, "descripcion": "Canchas de blindex de última generación."}
    ]

    for act in actividades_iniciales:
        act_existente = Actividad.query.filter_by(nombre=act["nombre"]).first()
        if not act_existente:
            nueva_act = Actividad(
                nombre=act["nombre"],
                precio_base=act["precio_base"],
                descripcion=act["descripcion"],
                activa=True
            )
            db.session.add(nueva_act)
            print(f"✔️ Actividad '{act['nombre']}' insertada correctamente.")
        else:
            print(f"ℹ️ La actividad '{act['nombre']}' ya se encontraba registrada.")

    # 3. GUARDAR TODO EN LA BASE DE DATOS
    try:
        db.session.commit()
        print("🎉 ¡Proceso de seeding completado de forma exitosa!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error crítico durante el commit de los datos: {str(e)}")

if __name__ == "__main__":
    # Usamos el contexto de la app de Flask para poder interactuar con SQLAlchemy
    with app.app_context():
        cargar_datos_base()