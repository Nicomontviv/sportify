import pytest
from datetime import date, time, datetime
from models import db, Usuario, Actividad, Turno, Clase, ListaEspera, Reserva, Credito
from helpers.espera_helper import procesar_lista_espera_al_cancelar

# ==========================================
# FIXTURES (Fábrica de datos para los tests)
# ==========================================
@pytest.fixture
def clase_base(app_context):
    act = Actividad(nombre="Natación", precio_base=10000.0, activa=True)
    db.session.add(act)
    db.session.commit()
    turno = Turno(actividad_id=act.id, dia_semana='lunes', horario_inicio=time(10,0), horario_fin=time(11,0), cupo_maximo=5)
    db.session.add(turno)
    db.session.commit()
    # Arranca con cupo 0 para simular que está llena
    clase = Clase(turno_id=turno.id, fecha=date.today(), cupo_disponible=0)
    db.session.add(clase)
    db.session.commit()
    return clase

def crear_usuario_test(nombre, es_abonado=False):
    user = Usuario(nombre=nombre, apellido="Test", dni=f"111{nombre}", email=f"{nombre}@test.com", password_hash="h", fecha_nacimiento=date(1990,1,1))
    db.session.add(user)
    db.session.commit()
    
    if es_abonado:
        # Le inyectamos un crédito pago del mes actual para que "is_abonado_actual" dé True
        ahora = datetime.now()
        credito = Credito(usuario_id=user.id, mes=ahora.month, anio=ahora.year, pagado=True, descuento_activo=True)
        db.session.add(credito)
        db.session.commit()
    return user

# ==========================================
# TESTS (Criterios de Aceptación)
# ==========================================

def test_escenario_1_abonado_cancela_con_abonados_esperando(app_context, clase_base):
    cancelador = crear_usuario_test("CanceladorAbonado", es_abonado=True)
    espera_no_abonado = crear_usuario_test("Casual1", es_abonado=False)
    espera_abonado = crear_usuario_test("Abonado1", es_abonado=True)

    # Anotamos a ambos en espera (El no abonado llegó primero)
    db.session.add(ListaEspera(clase_id=clase_base.id, usuario_id=espera_no_abonado.id, posicion=1))
    db.session.add(ListaEspera(clase_id=clase_base.id, usuario_id=espera_abonado.id, posicion=2))
    db.session.commit()

    # Ejecutamos la regla de negocio
    procesar_lista_espera_al_cancelar(clase_base.id, cancelador.id)

    # VERIFICACIÓN: El sistema debió saltar al Casual1 y darle la reserva al Abonado1
    reserva_nueva = Reserva.query.filter_by(clase_id=clase_base.id).first()
    inscripcion_abonado = ListaEspera.query.filter_by(usuario_id=espera_abonado.id).first()
    
    assert reserva_nueva.usuario_id == espera_abonado.id
    assert inscripcion_abonado.estado == 'notificado'
    assert clase_base.cupo_disponible == 0 # El cupo pasó directo

def test_escenario_2_abonado_cancela_sin_abonados_esperando(app_context, clase_base):
    cancelador = crear_usuario_test("CanceladorAbonado2", es_abonado=True)
    espera_no_abonado = crear_usuario_test("Casual2", es_abonado=False)

    db.session.add(ListaEspera(clase_id=clase_base.id, usuario_id=espera_no_abonado.id, posicion=1))
    db.session.commit()

    procesar_lista_espera_al_cancelar(clase_base.id, cancelador.id)

    # VERIFICACIÓN: Al no haber abonados, se la da al Casual
    reserva_nueva = Reserva.query.filter_by(clase_id=clase_base.id).first()
    assert reserva_nueva.usuario_id == espera_no_abonado.id

def test_escenario_3_no_abonado_cancela_lista_general(app_context, clase_base):
    cancelador = crear_usuario_test("CanceladorCasual", es_abonado=False)
    espera_casual = crear_usuario_test("Casual3", es_abonado=False)
    espera_abonado = crear_usuario_test("Abonado2", es_abonado=True)

    # Anotamos al casual primero
    db.session.add(ListaEspera(clase_id=clase_base.id, usuario_id=espera_casual.id, posicion=1))
    db.session.add(ListaEspera(clase_id=clase_base.id, usuario_id=espera_abonado.id, posicion=2))
    db.session.commit()

    procesar_lista_espera_al_cancelar(clase_base.id, cancelador.id)

    # VERIFICACIÓN: Como canceló un casual, se respeta el orden estricto (gana el casual)
    reserva_nueva = Reserva.query.filter_by(clase_id=clase_base.id).first()
    assert reserva_nueva.usuario_id == espera_casual.id

def test_escenario_4_cancelacion_sin_interesados(app_context, clase_base):
    cancelador = crear_usuario_test("Solo", es_abonado=False)
    
    # Aseguramos que la lista esté vacía
    ListaEspera.query.delete()
    db.session.commit()

    procesar_lista_espera_al_cancelar(clase_base.id, cancelador.id)

    # VERIFICACIÓN: Nadie se anotó, el cupo vuelve a la clase
    assert clase_base.cupo_disponible == 1
    assert Reserva.query.count() == 0