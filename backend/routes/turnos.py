from flask import Blueprint, request, jsonify
from datetime import date, datetime, timedelta, time
from sqlalchemy import and_

from models import db, Turno, Clase, Reserva, Administrador, Actividad
from helpers.turnos_helper import generar_clases_para_rango

turnos_bp = Blueprint('turnos', __name__)

# ============================================================
# Constantes
# ============================================================
VENTANA_GENERACION_DIAS = 90  # 3 meses hacia adelante
DIAS_VALIDOS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']

# ============================================================
# REGENERAR CLASES (rellena clases faltantes para todos los turnos activos)
# Se llama automáticamente al entrar a Gestión de Turnos.
# ============================================================
@turnos_bp.route('/regenerar-clases', methods=['POST'])
def regenerar_clases():
    user_id = request.headers.get('X-User-Id')
    if not _es_admin(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil administrador."}), 403

    try:
        turnos_activos = Turno.query.filter_by(activo=True).all()

        total_clases_creadas = 0
        detalle_por_turno = []

        for turno in turnos_activos:
            clases_nuevas = _generar_clases_futuras(turno)
            if len(clases_nuevas) > 0:
                detalle_por_turno.append({
                    "turno_id": turno.id,
                    "actividad": turno.actividad.nombre if turno.actividad else None,
                    "dia": turno.dia_semana,
                    "horario": turno.horario_inicio.strftime('%H:%M'),
                    "clases_agregadas": len(clases_nuevas)
                })
                total_clases_creadas += len(clases_nuevas)

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Regeneración completada. Se agregaron {total_clases_creadas} clases.",
            "total_clases_creadas": total_clases_creadas,
            "detalle": detalle_por_turno
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
# Helpers internos
# ============================================================
def _es_admin(user_id):
    """Valida que el user_id corresponda a un administrador."""
    if not user_id:
        return False
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False
    return Administrador.query.filter_by(usuario_id=user_id).first() is not None


def _parsear_hora(hora_str):
    """Convierte '18:00' o '18:00:00' a un objeto time."""
    try:
        partes = hora_str.split(':')
        return time(int(partes[0]), int(partes[1]))
    except (ValueError, IndexError, AttributeError):
        return None


def _calcular_horario_fin(horario_inicio):
    """Las clases duran 1h fija. Calcula horario_fin a partir del inicio."""
    # Usamos datetime para que sume bien aunque cruce medianoche (no debería)
    dt = datetime.combine(date.today(), horario_inicio) + timedelta(hours=1)
    return dt.time()


def _turno_a_dict(turno):
    return {
        "id": turno.id,
        "actividad_id": turno.actividad_id,
        "actividad_nombre": turno.actividad.nombre if turno.actividad else None,
        "dia_semana": turno.dia_semana,
        "horario_inicio": turno.horario_inicio.strftime('%H:%M'),
        "horario_fin": turno.horario_fin.strftime('%H:%M'),
        "cupo_maximo": turno.cupo_maximo,
        "activo": turno.activo
    }


def _clase_a_dict(clase):
    return {
        "id": clase.id,
        "turno_id": clase.turno_id,
        "fecha": clase.fecha.strftime('%Y-%m-%d'),
        "cupo_disponible": clase.cupo_disponible,
        "cupo_maximo": clase.turno.cupo_maximo if clase.turno else None,
        "actividad_nombre": clase.turno.actividad.nombre if clase.turno and clase.turno.actividad else None,
        "horario_inicio": clase.turno.horario_inicio.strftime('%H:%M') if clase.turno else None,
        "horario_fin": clase.turno.horario_fin.strftime('%H:%M') if clase.turno else None,
        "activo": clase.activo,
        "tiene_reservas": _clase_tiene_reservas(clase.id)
    }


def _clase_tiene_reservas(clase_id):
    """Devuelve True si la clase tiene al menos una reserva no cancelada."""
    reserva = Reserva.query.filter(
        Reserva.clase_id == clase_id,
        Reserva.estado.in_(['confirmada', 'pendiente_pago', 'asistio'])
    ).first()
    # La relación Actividad ↔ Turno la necesitamos para _turno_a_dict.
    # Si no existe en models.py, el backref se crea automáticamente abajo.
    return reserva is not None


# Relación inversa para poder hacer turno.actividad
# (si ya existe en models.py, esto no rompe nada porque se hace al import)
if not hasattr(Turno, 'actividad'):
    Turno.actividad = db.relationship('Actividad', backref='turnos', lazy=True)


# ============================================================
# LISTAR TURNOS
# ============================================================
@turnos_bp.route('', methods=['GET'])
def listar_turnos():
    try:
        # Por defecto solo los activos. Si pasan ?incluir_inactivos=true, todos.
        incluir_inactivos = request.args.get('incluir_inactivos', 'false').lower() == 'true'
        query = Turno.query
        if not incluir_inactivos:
            query = query.filter_by(activo=True)

        turnos = query.all()
        return jsonify({
            "status": "success",
            "turnos": [_turno_a_dict(t) for t in turnos]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# CREAR TURNO (+ generar clases a 3 meses)
# ============================================================
@turnos_bp.route('', methods=['POST'])
def crear_turno():
    user_id = request.headers.get('X-User-Id')
    if not _es_admin(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil administrador."}), 403

    data = request.get_json() or {}
    actividad_id = data.get('actividad_id')
    dia_semana = data.get('dia_semana')
    horario_inicio_str = data.get('horario_inicio')
    cupo_maximo = data.get('cupo_maximo')

    # Validaciones
    if not all([actividad_id, dia_semana, horario_inicio_str, cupo_maximo]):
        return jsonify({"status": "error", "message": "Faltan campos obligatorios (actividad_id, dia_semana, horario_inicio, cupo_maximo)."}), 400

    if dia_semana not in DIAS_VALIDOS:
        return jsonify({"status": "error", "message": f"Día inválido. Debe ser uno de: {', '.join(DIAS_VALIDOS)}."}), 400

    horario_inicio = _parsear_hora(horario_inicio_str)
    if not horario_inicio:
        return jsonify({"status": "error", "message": "Formato de horario_inicio inválido. Usar HH:MM."}), 400

    actividad = Actividad.query.get(actividad_id)
    if not actividad:
        return jsonify({"status": "error", "message": "La actividad indicada no existe."}), 404

    if not actividad.activa:
        return jsonify({"status": "error", "message": "No se puede crear un turno sobre una actividad dada de baja."}), 400

    try:
        cupo_maximo = int(cupo_maximo)
        if cupo_maximo <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "El cupo debe ser un número entero positivo."}), 400

    horario_fin = _calcular_horario_fin(horario_inicio)

    # ¿Ya existe un turno (activo o inactivo) en esa franja para esa actividad?
    turno_existente = Turno.query.filter_by(
        actividad_id=actividad_id,
        dia_semana=dia_semana,
        horario_inicio=horario_inicio
    ).first()

    try:
        if turno_existente:
            if turno_existente.activo:
                return jsonify({
                    "status": "error",
                    "message": "Ya existe un turno activo para esa actividad en ese día y horario."
                }), 400
            # Reactivamos el turno inactivo (Solución B)
            turno_existente.activo = True
            turno_existente.cupo_maximo = cupo_maximo
            turno_existente.horario_fin = horario_fin
            turno = turno_existente
            mensaje = "Turno reactivado correctamente."
        else:
            turno = Turno(
                actividad_id=actividad_id,
                dia_semana=dia_semana,
                horario_inicio=horario_inicio,
                horario_fin=horario_fin,
                cupo_maximo=cupo_maximo,
                activo=True
            )
            db.session.add(turno)
            mensaje = "Turno creado correctamente."

        db.session.flush()  # necesitamos turno.id para generar clases

        # Generamos clases a 3 meses vista
        clases_generadas = _generar_clases_futuras(turno)

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": mensaje,
            "turno": _turno_a_dict(turno),
            "clases_generadas": len(clases_generadas)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# MODIFICAR TURNO
# Reglas:
# - El día NUNCA se puede modificar (regla acordada con el equipo).
# - Si el turno tiene reservas en clases futuras: solo se puede SUBIR el cupo.
#   No se puede cambiar el horario ni bajar el cupo.
# - Si el turno NO tiene reservas: se puede cambiar horario y cupo libremente.
# ============================================================
@turnos_bp.route('/<int:turno_id>', methods=['PUT'])
def modificar_turno(turno_id):
    user_id = request.headers.get('X-User-Id')
    if not _es_admin(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil administrador."}), 403

    turno = Turno.query.get(turno_id)
    if not turno:
        return jsonify({"status": "error", "message": "Turno no encontrado."}), 404

    if not turno.activo:
        return jsonify({"status": "error", "message": "No se puede modificar un turno dado de baja."}), 400

    data = request.get_json() or {}

    # REGLA: el día NUNCA se puede modificar
    if 'dia_semana' in data and data['dia_semana'] != turno.dia_semana:
        return jsonify({
            "status": "error",
            "message": "No se puede cambiar el día del turno. Para cambiar el día, dá de baja este turno y creá uno nuevo."
        }), 400

    nuevo_horario_inicio_str = data.get('horario_inicio', turno.horario_inicio.strftime('%H:%M'))
    nuevo_cupo = data.get('cupo_maximo', turno.cupo_maximo)

    nuevo_horario_inicio = _parsear_hora(nuevo_horario_inicio_str)
    if not nuevo_horario_inicio:
        return jsonify({"status": "error", "message": "Formato de horario_inicio inválido. Usar HH:MM."}), 400

    try:
        nuevo_cupo = int(nuevo_cupo)
        if nuevo_cupo <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "El cupo debe ser un número entero positivo."}), 400

    # Detectamos si el turno tiene reservas en clases futuras
    hoy = date.today()
    clases_futuras = Clase.query.filter(
        Clase.turno_id == turno.id,
        Clase.fecha >= hoy,
        Clase.activo == True
    ).all()

    tiene_reservas = any(_clase_tiene_reservas(c.id) for c in clases_futuras)

    cambio_horario = nuevo_horario_inicio != turno.horario_inicio
    cambio_cupo = nuevo_cupo != turno.cupo_maximo

    # REGLA: si tiene reservas, restricciones extra
    if tiene_reservas:
        if cambio_horario:
            return jsonify({
                "status": "error",
                "message": "Este turno tiene clases con reservas. No se puede cambiar el horario. Para cambiarlo, dá de baja el turno (se reembolsarán las reservas) y creá uno nuevo."
            }), 400
        if nuevo_cupo < turno.cupo_maximo:
            return jsonify({
                "status": "error",
                "message": f"Este turno tiene reservas. El cupo solo se puede incrementar, no reducir. Cupo actual: {turno.cupo_maximo}."
            }), 400

    # Validar que la nueva franja no choque con otro turno activo
    if cambio_horario:
        conflicto = Turno.query.filter(
            Turno.actividad_id == turno.actividad_id,
            Turno.dia_semana == turno.dia_semana,
            Turno.horario_inicio == nuevo_horario_inicio,
            Turno.id != turno.id,
            Turno.activo == True
        ).first()
        if conflicto:
            return jsonify({
                "status": "error",
                "message": "Ya existe otro turno activo de la misma actividad en ese horario."
            }), 400

    try:
        cupo_viejo = turno.cupo_maximo

        turno.horario_inicio = nuevo_horario_inicio
        turno.horario_fin = _calcular_horario_fin(nuevo_horario_inicio)
        turno.cupo_maximo = nuevo_cupo

        # CASO A: tiene reservas → solo subimos cupo, actualizamos cupo_disponible de clases futuras
        if tiene_reservas:
            if cambio_cupo:
                delta = nuevo_cupo - cupo_viejo  # siempre > 0 acá
                for clase in clases_futuras:
                    clase.cupo_disponible += delta

            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "Turno modificado correctamente. Cupo incrementado en clases futuras.",
                "turno": _turno_a_dict(turno),
                "detalles": {
                    "clases_futuras_actualizadas": len(clases_futuras)
                }
            }), 200

        # CASO B: no tiene reservas → damos de baja clases viejas y regeneramos
        if cambio_horario or cambio_cupo:
            for clase in clases_futuras:
                clase.activo = False

            db.session.flush()
            clases_nuevas = _generar_clases_futuras(turno)

            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "Turno modificado correctamente.",
                "turno": _turno_a_dict(turno),
                "detalles": {
                    "clases_regeneradas": len(clases_nuevas),
                    "clases_dadas_de_baja": len(clases_futuras)
                }
            }), 200
        else:
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "Turno modificado (sin cambios que afecten clases).",
                "turno": _turno_a_dict(turno)
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# ELIMINAR TURNO (soft delete + cascada de clases sin reservas)
# ============================================================
@turnos_bp.route('/<int:turno_id>', methods=['DELETE'])
def eliminar_turno(turno_id):
    user_id = request.headers.get('X-User-Id')
    if not _es_admin(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil administrador."}), 403

    turno = Turno.query.get(turno_id)
    if not turno:
        return jsonify({"status": "error", "message": "Turno no encontrado."}), 404

    if not turno.activo:
        return jsonify({"status": "error", "message": "El turno ya está dado de baja."}), 400

    try:
        turno.activo = False

        # Soft delete de clases futuras sin reservas
        hoy = date.today()
        clases_futuras = Clase.query.filter(
            Clase.turno_id == turno.id,
            Clase.fecha >= hoy,
            Clase.activo == True
        ).all()

        clases_dadas_de_baja = 0
        clases_con_reservas = 0

        for clase in clases_futuras:
            if _clase_tiene_reservas(clase.id):
                clases_con_reservas += 1
            else:
                clase.activo = False
                clases_dadas_de_baja += 1

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Turno dado de baja correctamente.",
            "detalles": {
                "clases_futuras_dadas_de_baja": clases_dadas_de_baja,
                "clases_futuras_con_reservas_preservadas": clases_con_reservas
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# LISTAR CLASES POR RANGO (para el calendario del front)
# ============================================================
@turnos_bp.route('/clases', methods=['GET'])
def listar_clases():
    try:
        desde_str = request.args.get('desde')
        hasta_str = request.args.get('hasta')

        if not desde_str or not hasta_str:
            return jsonify({"status": "error", "message": "Faltan parámetros 'desde' y 'hasta' (formato YYYY-MM-DD)."}), 400

        try:
            desde = datetime.strptime(desde_str, '%Y-%m-%d').date()
            hasta = datetime.strptime(hasta_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"status": "error", "message": "Formato de fecha inválido. Usar YYYY-MM-DD."}), 400

        clases = Clase.query.filter(
            Clase.fecha >= desde,
            Clase.fecha <= hasta,
            Clase.activo == True
        ).order_by(Clase.fecha).all()

        return jsonify({
            "status": "success",
            "clases": [_clase_a_dict(c) for c in clases]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# DAR DE BAJA CLASE PUNTUAL
# ============================================================
@turnos_bp.route('/clases/<int:clase_id>', methods=['DELETE'])
def eliminar_clase(clase_id):
    user_id = request.headers.get('X-User-Id')
    if not _es_admin(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil administrador."}), 403

    clase = Clase.query.get(clase_id)
    if not clase:
        return jsonify({"status": "error", "message": "Clase no encontrada."}), 404

    if not clase.activo:
        return jsonify({"status": "error", "message": "La clase ya está dada de baja."}), 400

    tiene_reservas = _clase_tiene_reservas(clase.id)

    try:
        clase.activo = False
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Clase dada de baja correctamente.",
            "detalles": {
                "tenia_reservas": tiene_reservas
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# HELPER INTERNO: generar clases futuras a 3 meses
# ============================================================
# ============================================================
# HELPER INTERNO: generar clases futuras a 3 meses
# ============================================================
def _generar_clases_futuras(turno):
    """
    Genera clases para el turno desde mañana hasta 3 meses adelante.
    - Si NO existe una clase para esa fecha + turno: la crea.
    - Si existe una clase ACTIVA: no hace nada.
    - Si existe una clase INACTIVA: la reactiva y le actualiza el cupo
      al cupo_maximo actual del turno (útil para el flujo de modificar turno).
    """
    hoy = date.today()
    fecha_desde = hoy + timedelta(days=1)
    fecha_hasta = hoy + timedelta(days=VENTANA_GENERACION_DIAS)

    clases_candidatas = generar_clases_para_rango(turno, fecha_desde, fecha_hasta)
    clases_efectivamente_creadas = []

    for nueva_clase in clases_candidatas:
        # Buscamos cualquier clase existente para ese turno + fecha (activa o inactiva)
        existente = Clase.query.filter_by(
            turno_id=turno.id,
            fecha=nueva_clase.fecha
        ).first()

        if existente is None:
            # No existe nada → la creamos
            db.session.add(nueva_clase)
            clases_efectivamente_creadas.append(nueva_clase)
        elif not existente.activo:
            # Existe pero está inactiva → la reactivamos y actualizamos cupo
            existente.activo = True
            existente.cupo_disponible = turno.cupo_maximo
            clases_efectivamente_creadas.append(existente)
        # Si existe y está activa, no hacemos nada (ya está como debería)

    return clases_efectivamente_creadas