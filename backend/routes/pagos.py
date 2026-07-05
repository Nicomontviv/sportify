from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Reserva, Deposito, Empleado, Usuario, Administrador, Clase, Turno, Actividad, Credito, Certificado
import re

pagos_bp = Blueprint('pagos', __name__)

# ============================================================
# Helpers internos
# ============================================================

def _es_empleado(user_id):
    """Valida que el user_id corresponda a un empleado."""
    if not user_id:
        return False
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False
    return Empleado.query.filter_by(usuario_id=user_id).first() is not None

def _get_empleado(user_id):
    """Retorna el objeto Empleado asociado al user_id."""
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    return Empleado.query.filter_by(usuario_id=user_id).first()

def _deposito_a_dict(deposito):
    """Convierte un depósito a diccionario con info de la reserva."""
    reserva = deposito.reserva
    clase = reserva.clase if reserva else None
    turno = clase.turno if clase else None
    actividad = turno.actividad if turno else None
    return {
        "deposito_id": deposito.id,
        "reserva_id": deposito.reserva_id,
        "monto": float(deposito.monto),
        "fecha": deposito.fecha.strftime('%Y-%m-%d %H:%M'),
        "tipo": deposito.tipo,
        "actividad": actividad.nombre if actividad else None,
        "fecha_clase": clase.fecha.strftime('%Y-%m-%d') if clase else None,
        "horario": turno.horario_inicio.strftime('%H:%M') if turno else None,
        "metodo_pago": reserva.metodo_pago if reserva else None
    }

def _validar_tarjeta(numero, titular, vencimiento, cvv):
    """
    Valida los datos de la tarjeta según las reglas de negocio (RN1.3):
    - Número: exactamente 16 dígitos numéricos
    - Titular: no puede estar vacío
    - Vencimiento: formato MM/AA, mes entre 01 y 12, fecha >= fecha actual
    - CVV: exactamente 3 dígitos numéricos
    Números especiales de simulación:
    - 1111111111111111: pago exitoso
    - 2222222222222222: fondos insuficientes
    - 3333333333333333: tarjeta bloqueada o inhabilitada
    Retorna None si todo es válido, o un mensaje de error específico si algo falla.
    """
    # Validar número de tarjeta: exactamente 16 dígitos numéricos
    if not numero or not re.fullmatch(r'\d{16}', str(numero)):
        return "El número de tarjeta debe tener exactamente 16 dígitos numéricos"

    # Validar titular: no puede estar vacío
    if not titular or str(titular).strip() == '':
        return "El nombre del titular es obligatorio"

    # Validar vencimiento: formato MM/AA
    if not vencimiento or not re.fullmatch(r'\d{2}/\d{2}', str(vencimiento)):
        return "La fecha de vencimiento debe tener el formato MM/AA"

    mes, anio = vencimiento.split('/')
    mes = int(mes)
    anio = int(anio) + 2000  # Convertimos AA a AAAA (ej: 27 -> 2027)

    # Validar mes entre 01 y 12 (Escenario 5)
    if mes < 1 or mes > 12:
        return "El mes de vencimiento debe estar entre 01 y 12"

    # Validar que la tarjeta no esté vencida considerando mes y año actual (Escenario 6)
    ahora = datetime.now()
    if anio < ahora.year or (anio == ahora.year and mes < ahora.month):
        return "La tarjeta está vencida"

    # Validar CVV: exactamente 3 dígitos numéricos (Escenario 7)
    if not cvv or not re.fullmatch(r'\d{3}', str(cvv)):
        return "El código de seguridad debe tener exactamente 3 dígitos"

    # Simulación de resultados según número de tarjeta (Escenarios 11 y 12)
    if str(numero) == '2222222222222222':
        return "Pago denegado: fondos insuficientes"
    if str(numero) == '3333333333333333':
        return "Pago denegado: su tarjeta se encuentra bloqueada o inhabilitada"

    return None  # Todo válido


# ============================================================
# ENDPOINT AUXILIAR — BUSCAR USUARIO POR DNI (para el empleado)
# El empleado busca un usuario por DNI para registrar su pago
# Solo devuelve usuarios casuales 
# ============================================================
@pagos_bp.route('/usuario-por-dni/<string:dni>', methods=['GET'])
def usuario_por_dni(dni):
    user_id = request.headers.get('X-User-Id')

    # Validar que sea empleado
    if not _es_empleado(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil empleado."}), 403

    try:
        # Buscar el usuario por DNI
        usuario = Usuario.query.filter_by(dni=dni, activo=True).first()
        if not usuario:
            return jsonify({"status": "error", "message": "No se encontró ningún usuario con ese DNI."}), 404

        #  Verificar que no sea admin ni empleado (solo usuarios casuales)
        es_admin = Administrador.query.filter_by(usuario_id=usuario.id).first()
        es_empleado_usuario = Empleado.query.filter_by(usuario_id=usuario.id).first()
        if es_admin or es_empleado_usuario:
            return jsonify({"status": "error", "message": "No se encontró ningún usuario con ese DNI."}), 404

        return jsonify({
            "status": "success",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "dni": usuario.dni,
                "email": usuario.email
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500


# ============================================================
# HU 1 — PAGO VIRTUAL DEL USUARIO CASUAL
# El usuario elige si paga seña (50%) o total (100%) de una o varias reservas
# El pago se procesa mediante un formulario de tarjeta simulado 
# ============================================================
@pagos_bp.route('/virtual', methods=['POST'])
def pago_virtual():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"status": "error", "message": "No autorizado."}), 401

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "ID de usuario inválido."}), 400

    data = request.get_json() or {}
    pagos = data.get('pagos')  # Lista de { reserva_id, tipo_pago: 'senia' | 'total' }

    # Datos de la tarjeta (RN1.2)
    numero_tarjeta = data.get('numero_tarjeta')
    titular = data.get('titular')
    vencimiento = data.get('vencimiento')
    cvv = data.get('cvv')

    if not pagos or not isinstance(pagos, list) or len(pagos) == 0:
        return jsonify({"status": "error", "message": "Debe enviar al menos un pago."}), 400

    # Validar datos de la tarjeta (RN1.3 - Escenarios 4 al 12)
    error_tarjeta = _validar_tarjeta(numero_tarjeta, titular, vencimiento, cvv)
    if error_tarjeta:
        return jsonify({"status": "error", "message": error_tarjeta}), 400

    resultados = []
    total_cobrado = 0

    try:
        for item in pagos:
            reserva_id = item.get('reserva_id')
            tipo_pago = item.get('tipo_pago')  # 'senia' o 'total'

            if not reserva_id or tipo_pago not in ('senia', 'total'):
                return jsonify({
                    "status": "error",
                    "message": f"Datos inválidos para el pago de la reserva {reserva_id}. tipo_pago debe ser 'senia' o 'total'."
                }), 400

            # Verificar que la reserva existe y pertenece al usuario (RN1.4)
            reserva = Reserva.query.filter_by(id=reserva_id, usuario_id=user_id).first()
            if not reserva:
                return jsonify({
                    "status": "error",
                    "message": f"La reserva {reserva_id} no existe o no pertenece al usuario."
                }), 404

            # Verificar que la reserva tiene saldo pendiente
            monto_pendiente = float(reserva.monto_total) - float(reserva.monto_pagado)
            if monto_pendiente <= 0:
                return jsonify({
                    "status": "error",
                    "message": f"La reserva {reserva_id} ya está pagada en su totalidad."
                }), 400

            # Calcular monto a cobrar según tipo de pago (RN1.6)
            tenia_senia_previa = float(reserva.monto_pagado) > 0
            if tipo_pago == 'senia':
                monto_a_cobrar = round(float(reserva.monto_total) * 0.5, 2)
                tipo_deposito = 'senia'
            else:  # total
                monto_a_cobrar = monto_pendiente
                tipo_deposito = 'pago_total'

            # Registrar el depósito
            nuevo_deposito = Deposito(
                reserva_id=reserva.id,
                empleado_id=None,  # Es pago online, no hay empleado
                monto=monto_a_cobrar,
                fecha=datetime.now(),
                tipo=tipo_deposito
            )
            db.session.add(nuevo_deposito)

            # Actualizar monto pagado en la reserva
            reserva.monto_pagado = float(reserva.monto_pagado) + monto_a_cobrar

            # Actualizar estado de la reserva (RN1.7)
            if float(reserva.monto_pagado) >= float(reserva.monto_total):
                reserva.estado = 'confirmada'
            else:
                reserva.estado = 'pendiente_pago'

            reserva.metodo_pago = 'tarjeta_virtual'  # Pasarela simulada interna (RN1.1)
            total_cobrado += monto_a_cobrar

            resultados.append({
                "reserva_id": reserva.id,
                "tipo_pago": tipo_pago,
                "monto_cobrado": monto_a_cobrar,
                "monto_total": float(reserva.monto_total),
                "monto_pagado": float(reserva.monto_pagado),
                "monto_pendiente": float(reserva.monto_total) - float(reserva.monto_pagado),
                "estado": reserva.estado
            })

        db.session.commit()

        # Mensajes según escenarios de la HU
        mensaje = "Pago de seña confirmado exitosamente" if len(pagos) == 1 and pagos[0]['tipo_pago'] == 'senia' \
            else "Pago del saldo faltante confirmado exitosamente" if len(pagos) == 1 and tenia_senia_previa \
            else "Pago total confirmado exitosamente" if len(pagos) == 1 \
            else "Pago confirmado exitosamente"

        return jsonify({
            "status": "success",
            "message": mensaje,
            "total_cobrado": total_cobrado,
            "pagos": resultados
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500


# ============================================================
# HU 2 — PAGO PRESENCIAL DEL USUARIO CASUAL (registrado por empleado)
# El empleado registra si cobró seña (50%) o total (100%) en efectivo
# ============================================================
@pagos_bp.route('/presencial', methods=['POST'])
def pago_presencial():
    user_id = request.headers.get('X-User-Id')

    # Validar que sea empleado
    if not _es_empleado(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil empleado."}), 403

    empleado = _get_empleado(user_id)

    data = request.get_json() or {}
    pagos = data.get('pagos')  # Lista de { reserva_id, tipo_pago: 'senia' | 'total' }

    if not pagos or not isinstance(pagos, list) or len(pagos) == 0:
        return jsonify({"status": "error", "message": "Debe enviar al menos un pago."}), 400

    resultados = []
    total_cobrado = 0

    try:
        for item in pagos:
            reserva_id = item.get('reserva_id')
            tipo_pago = item.get('tipo_pago')  # 'senia' o 'total'

            if not reserva_id or tipo_pago not in ('senia', 'total'):
                return jsonify({
                    "status": "error",
                    "message": f"Datos inválidos para el pago de la reserva {reserva_id}. tipo_pago debe ser 'senia' o 'total'."
                }), 400

            # Verificar que la reserva existe
            reserva = Reserva.query.filter_by(id=reserva_id).first()
            if not reserva:
                return jsonify({
                    "status": "error",
                    "message": f"La reserva {reserva_id} no existe."
                }), 404

            # Verificar que la reserva tiene saldo pendiente
            monto_pendiente = float(reserva.monto_total) - float(reserva.monto_pagado)
            if monto_pendiente <= 0:
                return jsonify({
                    "status": "error",
                    "message": f"La reserva {reserva_id} ya está pagada en su totalidad."
                }), 400

            # Calcular monto a cobrar según tipo de pago
            if tipo_pago == 'senia':
                monto_a_cobrar = round(float(reserva.monto_total) * 0.5, 2)
                tipo_deposito = 'senia'
            else:  # total
                monto_a_cobrar = monto_pendiente
                tipo_deposito = 'pago_total' if float(reserva.monto_pagado) == 0 else 'pago_parcial'

            # Registrar el depósito con el empleado
            nuevo_deposito = Deposito(
                reserva_id=reserva.id,
                empleado_id=empleado.id,
                monto=monto_a_cobrar,
                fecha=datetime.now(),
                tipo=tipo_deposito
            )
            db.session.add(nuevo_deposito)

            # Actualizar monto pagado en la reserva
            reserva.monto_pagado = float(reserva.monto_pagado) + monto_a_cobrar

            # Actualizar estado de la reserva
            if float(reserva.monto_pagado) >= float(reserva.monto_total):
                reserva.estado = 'confirmada'
            else:
                reserva.estado = 'pendiente_pago'

            reserva.metodo_pago = 'efectivo'
            total_cobrado += monto_a_cobrar

            resultados.append({
                "reserva_id": reserva.id,
                "tipo_pago": tipo_pago,
                "monto_cobrado": monto_a_cobrar,
                "monto_total": float(reserva.monto_total),
                "monto_pagado": float(reserva.monto_pagado),
                "monto_pendiente": float(reserva.monto_total) - float(reserva.monto_pagado),
                "estado": reserva.estado
            })

        db.session.commit()

        mensaje = "Seña guardada exitosamente" if len(pagos) == 1 and pagos[0]['tipo_pago'] == 'senia' \
            else "Pago total guardado exitosamente" if len(pagos) == 1 and tipo_deposito == 'pago_total' \
            else "Pago del saldo faltante guardado exitosamente" if len(pagos) == 1 and tipo_deposito == 'pago_parcial' \
            else "Pago guardado exitosamente"

        return jsonify({
            "status": "success",
            "message": mensaje,
            "total_cobrado": total_cobrado,
            "pagos": resultados
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500


# ============================================================
# HU 3 — CONSULTAR MIS PAGOS
# El usuario consulta su historial de pagos filtrado por mes
# ============================================================
@pagos_bp.route('/mis-pagos', methods=['GET'])
def mis_pagos():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"status": "error", "message": "No autorizado."}), 401

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "ID de usuario inválido."}), 400

    # Parámetros de filtro por mes y año
    mes = request.args.get('mes')
    anio = request.args.get('anio')

    if not mes or not anio:
        return jsonify({"status": "error", "message": "Debe enviar los parámetros 'mes' y 'anio'."}), 400

    try:
        mes = int(mes)
        anio = int(anio)
        if mes < 1 or mes > 12:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Mes y año deben ser números válidos. Mes entre 1 y 12."}), 400
    actividad_id = request.args.get('actividad_id')

    try:
        # Buscar todas las reservas del usuario
        query = Reserva.query.filter_by(usuario_id=user_id)
        if actividad_id:
            query = query.join(Clase).join(Turno).filter(Turno.actividad_id == int(actividad_id))     
        reservas = query.all()
        reservas_ids = [r.id for r in reservas]

        if not reservas_ids:
            return jsonify({
                "status": "success",
                "message": "No posee pagos en el mes seleccionado",
                "pagos": []
            }), 200

        # Buscar depósitos de esas reservas en el mes y año indicados
        depositos = Deposito.query.filter(
            Deposito.reserva_id.in_(reservas_ids),
            db.extract('month', Deposito.fecha) == mes,
            db.extract('year', Deposito.fecha) == anio
        ).order_by(Deposito.fecha.desc()).all()

        if not depositos:
            return jsonify({
                "status": "success",
                "message": "No posee pagos en el mes seleccionado",
                "pagos": []
            }), 200

        return jsonify({
            "status": "success",
            "message": f"Pagos del mes {mes}/{anio}",
            "pagos": [_deposito_a_dict(d) for d in depositos]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500


# ============================================================
# RESERVAR Y PAGAR EN UN SOLO PASO (desde calendario de actividades)
# El usuario selecciona clases del calendario, elige seña o total,
# ingresa datos de tarjeta y se crea la reserva + depósito juntos.
# ============================================================
@pagos_bp.route('/reservar-y-pagar', methods=['POST'])
def reservar_y_pagar():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"status": "error", "message": "No autorizado."}), 401

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "ID de usuario inválido."}), 400

    data = request.get_json() or {}
    clases = data.get('clases')  # Lista de { clase_id, tipo_pago: 'senia' | 'total' }
    numero_tarjeta = data.get('numero_tarjeta')
    titular = data.get('titular')
    vencimiento = data.get('vencimiento')
    cvv = data.get('cvv')

    if not clases or not isinstance(clases, list) or len(clases) == 0:
        return jsonify({"status": "error", "message": "Debe enviar al menos una clase."}), 400

    error_tarjeta = _validar_tarjeta(numero_tarjeta, titular, vencimiento, cvv)
    if error_tarjeta:
        return jsonify({"status": "error", "message": error_tarjeta}), 400

    usuario = db.session.get(Usuario, user_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404
    
    # REGLA DE NEGOCIO: El usuario debe tener un certificado de aptitud física vigente
    certificado = Certificado.query.filter_by(usuario_id=user_id, estado='vigente').first()
    if not certificado:
        return jsonify({"status": "error", "message": "No podés reservar sin un certificado de aptitud física vigente."}), 400

    resultados = []
    total_cobrado = 0

    try:
        for item in clases:
            clase_id = item.get('clase_id')
            tipo_pago = item.get('tipo_pago')

            if not clase_id or tipo_pago not in ('senia', 'total'):
                return jsonify({
                    "status": "error",
                    "message": f"Datos inválidos para la clase {clase_id}. tipo_pago debe ser 'senia' o 'total'."
                }), 400

            clase = db.session.get(Clase, clase_id)
            if not clase or not clase.activo:
                return jsonify({"status": "error", "message": f"La clase {clase_id} no existe o no está disponible."}), 404

            if clase.cupo_disponible <= 0:
                return jsonify({"status": "error", "message": "La clase no posee cupos disponibles."}), 409

            turno = db.session.get(Turno, clase.turno_id)
            actividad = db.session.get(Actividad, turno.actividad_id)
            monto_total = float(actividad.precio_base)

            if usuario.is_abonado_actual:
                ahora = datetime.now()
                credito = Credito.query.filter_by(
                    usuario_id=user_id, anio=ahora.year, mes=ahora.month
                ).first()
                if credito:
                    monto_total = round(monto_total - monto_total * float(credito.monto_descuento) / 100, 2)
                monto_a_cobrar = monto_total
                monto_pagado_inicial = monto_total
                tipo_deposito = 'pago_total'
                estado = 'confirmada'
            elif tipo_pago == 'senia':
                monto_a_cobrar = round(monto_total * 0.5, 2)
                monto_pagado_inicial = monto_a_cobrar
                tipo_deposito = 'senia'
                estado = 'pendiente_pago'
            else:
                monto_a_cobrar = monto_total
                monto_pagado_inicial = monto_total
                tipo_deposito = 'pago_total'
                estado = 'confirmada'

            nueva_reserva = Reserva(
                clase_id=clase_id,
                usuario_id=user_id,
                metodo_pago='tarjeta_virtual',
                monto_total=monto_total,
                monto_pagado=monto_pagado_inicial,
                estado=estado
            )
            db.session.add(nueva_reserva)
            db.session.flush()

            nuevo_deposito = Deposito(
                reserva_id=nueva_reserva.id,
                empleado_id=None,
                monto=monto_a_cobrar,
                fecha=datetime.now(),
                tipo=tipo_deposito
            )
            db.session.add(nuevo_deposito)

            clase.cupo_disponible -= 1
            total_cobrado += monto_a_cobrar

            resultados.append({
                "reserva_id": nueva_reserva.id,
                "clase_id": clase_id,
                "tipo_pago": tipo_pago,
                "monto_cobrado": monto_a_cobrar,
                "monto_total": monto_total,
                "estado": estado
            })

        db.session.commit()

        # REGLA DE NEGOCIO: verificar si el usuario se convierte en abonado
        ahora = datetime.now()
        for item in clases:
            clase_id = item.get('clase_id')
            clase = db.session.get(Clase, clase_id)
            turno = db.session.get(Turno, clase.turno_id)
            
            reservas_mismo_turno = Reserva.query.join(Clase).filter(
                Reserva.usuario_id == user_id,
                Clase.turno_id == turno.id,
                db.extract('month', Clase.fecha) == ahora.month,
                db.extract('year', Clase.fecha) == ahora.year,
                Reserva.estado.in_(['confirmada', 'pendiente_pago'])
            ).count()

            if reservas_mismo_turno >= 3:
                credito_existente = Credito.query.filter_by(
                    usuario_id=user_id, mes=ahora.month, anio=ahora.year
                ).first()
                if not credito_existente:
                    nuevo_credito = Credito(
                        usuario_id=user_id,
                        mes=ahora.month,
                        anio=ahora.year,
                        pagado=True,
                        descuento_activo=True
                    )
                    db.session.add(nuevo_credito)
                    
                    # Aplicar descuento retroactivo a las reservas del mismo turno
                    reservas_a_actualizar = Reserva.query.join(Clase).filter(
                        Reserva.usuario_id == user_id,
                        Clase.turno_id == turno.id,
                        db.extract('month', Clase.fecha) == ahora.month,
                        db.extract('year', Clase.fecha) == ahora.year,
                        Reserva.estado.in_(['confirmada', 'pendiente_pago'])
                    ).all()
                    
                    for r in reservas_a_actualizar:
                        monto_con_descuento = round(float(r.monto_total) * 0.80, 2)
                        r.monto_total = monto_con_descuento
                        r.monto_pagado = monto_con_descuento
                        r.estado = 'confirmada'
                    
                    db.session.commit()

        if len(clases) == 1 and clases[0]['tipo_pago'] == 'senia':
            mensaje = "Reserva confirmada. Seña pagada exitosamente."
        elif len(clases) == 1:
            mensaje = "Reserva confirmada. Pago total realizado exitosamente."
        else:
            mensaje = "Reservas confirmadas. Pago realizado exitosamente."

        return jsonify({
            "status": "success",
            "message": mensaje,
            "total_cobrado": total_cobrado,
            "reservas": resultados
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500


# ============================================================
# RESERVAR Y COBRAR PRESENCIALMENTE EN UN SOLO PASO (empleado)
# El empleado busca al usuario, selecciona clases del calendario,
# elige seña o total, y se crea la reserva + depósito presencial.
# ============================================================
@pagos_bp.route('/reservar-presencial', methods=['POST'])
def reservar_presencial():
    user_id = request.headers.get('X-User-Id')

    if not _es_empleado(user_id):
        return jsonify({"status": "error", "message": "No autorizado. Se requiere perfil empleado."}), 403

    empleado = _get_empleado(user_id)

    data = request.get_json() or {}
    usuario_id = data.get('usuario_id')
    clases = data.get('clases')  # Lista de { clase_id, tipo_pago: 'senia' | 'total' }

    if not usuario_id:
        return jsonify({"status": "error", "message": "Debe enviar el usuario_id."}), 400

    if not clases or not isinstance(clases, list) or len(clases) == 0:
        return jsonify({"status": "error", "message": "Debe enviar al menos una clase."}), 400

    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        return jsonify({"status": "error", "message": "Usuario no encontrado."}), 404
    
    # REGLA DE NEGOCIO: El usuario debe tener un certificado de aptitud física vigente
    certificado = Certificado.query.filter_by(usuario_id=usuario_id, estado='vigente').first()
    if not certificado:
        return jsonify({"status": "error", "message": "El usuario no tiene un certificado de aptitud física vigente."}), 400

    resultados = []
    total_cobrado = 0

    try:
        for item in clases:
            clase_id = item.get('clase_id')
            tipo_pago = item.get('tipo_pago')

            if not clase_id or tipo_pago not in ('senia', 'total'):
                return jsonify({
                    "status": "error",
                    "message": f"Datos inválidos para la clase {clase_id}. tipo_pago debe ser 'senia' o 'total'."
                }), 400

            clase = db.session.get(Clase, clase_id)
            if not clase or not clase.activo:
                return jsonify({"status": "error", "message": f"La clase {clase_id} no existe o no está disponible."}), 404

            if clase.cupo_disponible <= 0:
                return jsonify({"status": "error", "message": "La clase no posee cupos disponibles."}), 409

            turno = db.session.get(Turno, clase.turno_id)
            actividad = db.session.get(Actividad, turno.actividad_id)
            monto_total = float(actividad.precio_base)

            if usuario.is_abonado_actual:
                ahora = datetime.now()
                credito = Credito.query.filter_by(
                    usuario_id=usuario_id, anio=ahora.year, mes=ahora.month
                ).first()
                if credito:
                    monto_total = round(monto_total - monto_total * float(credito.monto_descuento) / 100, 2)
                monto_a_cobrar = monto_total
                monto_pagado_inicial = monto_total
                tipo_deposito = 'pago_total'
                estado = 'confirmada'
            elif tipo_pago == 'senia':
                monto_a_cobrar = round(monto_total * 0.5, 2)
                monto_pagado_inicial = monto_a_cobrar
                tipo_deposito = 'senia'
                estado = 'pendiente_pago'
            else:
                monto_a_cobrar = monto_total
                monto_pagado_inicial = monto_total
                tipo_deposito = 'pago_total'
                estado = 'confirmada'

            nueva_reserva = Reserva(
                clase_id=clase_id,
                usuario_id=usuario_id,
                metodo_pago='efectivo',
                monto_total=monto_total,
                monto_pagado=monto_pagado_inicial,
                estado=estado
            )
            db.session.add(nueva_reserva)
            db.session.flush()

            nuevo_deposito = Deposito(
                reserva_id=nueva_reserva.id,
                empleado_id=empleado.id,
                monto=monto_a_cobrar,
                fecha=datetime.now(),
                tipo=tipo_deposito
            )
            db.session.add(nuevo_deposito)

            clase.cupo_disponible -= 1
            total_cobrado += monto_a_cobrar

            resultados.append({
                "reserva_id": nueva_reserva.id,
                "clase_id": clase_id,
                "tipo_pago": tipo_pago,
                "monto_cobrado": monto_a_cobrar,
                "monto_total": monto_total,
                "estado": estado
            })

        db.session.commit()

        if len(clases) == 1 and clases[0]['tipo_pago'] == 'senia':
            mensaje = "Reserva creada. Seña registrada exitosamente."
        elif len(clases) == 1:
            mensaje = "Reserva creada. Pago total registrado exitosamente."
        else:
            mensaje = "Reservas creadas. Cobro registrado exitosamente."

        return jsonify({
            "status": "success",
            "message": mensaje,
            "total_cobrado": total_cobrado,
            "reservas": resultados
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error en el servidor: {str(e)}"}), 500
