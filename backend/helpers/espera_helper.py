from datetime import datetime # Asegurate de importar datetime arriba de todo
from models import db, Usuario, Clase, ListaEspera, Reserva, Actividad, Turno, Notificacion

def procesar_lista_espera_al_cancelar(clase_id, usuario_que_cancela_id):
    """
    Evalúa la lista de espera de una clase cuando alguien cancela su lugar 
    y reasigna el cupo según las reglas de negocio.
    """
    usuario_cancelador = db.session.get(Usuario, usuario_que_cancela_id)
    clase = db.session.get(Clase, clase_id)

    # Obtenemos toda la lista de espera activa para esta clase, por orden de llegada
    esperando = ListaEspera.query.filter_by(
        clase_id=clase_id, 
        estado='en_espera'
    ).order_by(ListaEspera.posicion).all()

    # ESCENARIO 4: Cancelación sin interesados en espera
    if not esperando:
        clase.cupo_disponible += 1
        db.session.commit()
        return

    usuario_asignado = None
    inscripcion_asignada = None

    if usuario_cancelador.is_abonado_actual:
        # REGLA 1 (Escenarios 1 y 2): Cancela un Abonado
        # Buscamos primero si hay algún otro Abonado en la lista
        for inscripcion in esperando:
            user_espera = db.session.get(Usuario, inscripcion.usuario_id)
            if user_espera.is_abonado_actual:
                usuario_asignado = user_espera
                inscripcion_asignada = inscripcion
                break
        
        # Si la lista de abonados estaba vacía, salta a la lista de No Abonados (el primero general)
        if not usuario_asignado and esperando:
            inscripcion_asignada = esperando[0]
            usuario_asignado = db.session.get(Usuario, inscripcion_asignada.usuario_id)
    else:
        # REGLA 2 (Escenario 3): Cancela un No Abonado
        # Se le asigna directamente al primero de la lista general, sea quien sea.
        inscripcion_asignada = esperando[0]
        usuario_asignado = db.session.get(Usuario, inscripcion_asignada.usuario_id)

    # Si encontramos a alguien para darle el cupo:
    if usuario_asignado and inscripcion_asignada:
        # 1. Buscamos el precio de la actividad para crearle la reserva
        turno = db.session.get(Turno, clase.turno_id)
        actividad = db.session.get(Actividad, turno.actividad_id)

        # 2. Le creamos la reserva en estado pendiente
        nueva_reserva = Reserva(
            clase_id=clase_id,
            usuario_id=usuario_asignado.id,
            estado='pendiente_pago',
            metodo_pago='efectivo', # Se actualiza luego cuando pague
            monto_total=actividad.precio_base,
            monto_pagado=0.00
        )
        db.session.add(nueva_reserva)

     
          # 3. Lo sacamos de la lista de espera y registramos la hora exacta (Cronómetro ON)
        inscripcion_asignada.estado = 'notificado'
        inscripcion_asignada.fecha_notificacion = datetime.now() # <-- ¡NUEVA LÍNEA!

        # 4. Le avisamos al usuario que tiene 1 hora para confirmar
        db.session.add(Notificacion(
            usuario_id=usuario_asignado.id,
            mensaje="¡Se liberó un cupo! Tenés 1 hora para confirmar tu lugar."
        ))

        # NOTA: NO incrementamos el cupo_disponible...
        db.session.commit()
        # NOTA: NO incrementamos el cupo_disponible de la clase porque el lugar 
        # pasó directamente de las manos del que canceló al nuevo usuario.
        db.session.commit()