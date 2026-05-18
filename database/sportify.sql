-- ============================================================
--  Sportify — Modelo Físico de Base de Datos 
--  Motor: MySQL 8.x
--  Proyecto: La Plata Tech — Grupo 59
--  Fecha: 2026-05-16
-- ============================================================

CREATE DATABASE IF NOT EXISTS sportify
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sportify;

-- ------------------------------------------------------------
-- 1. ACTIVIDAD
-- ------------------------------------------------------------
CREATE TABLE actividad (
  id          INT            NOT NULL AUTO_INCREMENT,
  nombre      VARCHAR(100)   NOT NULL,
  descripcion TEXT,
  activa      TINYINT(1)     NOT NULL DEFAULT 1,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. USUARIO (Estructura limpia sin ENUM de tipo)
-- ------------------------------------------------------------
CREATE TABLE usuario (
  id                INT           NOT NULL AUTO_INCREMENT,
  nombre            VARCHAR(100)  NOT NULL,
  apellido          VARCHAR(100)  NOT NULL,
  dni               VARCHAR(20)   NOT NULL UNIQUE,
  email             VARCHAR(150)  NOT NULL UNIQUE,
  password_hash     VARCHAR(255)  NOT NULL,
  fecha_nacimiento DATE          NOT NULL,
  activo            TINYINT(1)    NOT NULL DEFAULT 1,
  fecha_alta        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. CERTIFICADO  (aptitud física)
-- ------------------------------------------------------------
CREATE TABLE certificado (
  id                INT          NOT NULL AUTO_INCREMENT,
  usuario_id        INT          NOT NULL,
  numero            VARCHAR(100),
  fecha_emision     DATE,
  fecha_vencimiento DATE         NOT NULL,
  estado            ENUM('vigente','vencido','pendiente') NOT NULL DEFAULT 'pendiente',
  PRIMARY KEY (id),
  CONSTRAINT fk_cert_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuario (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. CREDITO  (membresía / descuento mensual del abonado)
-- ------------------------------------------------------------
CREATE TABLE credito (
  id               INT           NOT NULL AUTO_INCREMENT,
  usuario_id       INT           NOT NULL,
  monto_descuento  DECIMAL(5,2)  NOT NULL DEFAULT 20.00,  -- % de descuento 
  mes              TINYINT       NOT NULL,                  -- 1..12
  anio             SMALLINT      NOT NULL,
  pagado           TINYINT(1)    NOT NULL DEFAULT 0,
  fecha_pago       DATETIME,
  cancelaciones    TINYINT       NOT NULL DEFAULT 0,        -- acumuladas en el mes
  descuento_activo TINYINT(1)    NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY uq_credito_usuario_mes_anio (usuario_id, mes, anio),
  CONSTRAINT fk_credito_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuario (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5. EMPLEADO  (especialización de usuario)
-- ------------------------------------------------------------
CREATE TABLE empleado (
  id         INT          NOT NULL AUTO_INCREMENT,
  usuario_id INT          NOT NULL UNIQUE,
  legajo     VARCHAR(50),
  cargo      VARCHAR(100),
  PRIMARY KEY (id),
  CONSTRAINT fk_empleado_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuario (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 6. ADMINISTRADOR  (especialización de usuario)
-- ------------------------------------------------------------
CREATE TABLE administrador (
  id             INT          NOT NULL AUTO_INCREMENT,
  usuario_id     INT          NOT NULL UNIQUE,
  nivel_acceso   VARCHAR(50)  NOT NULL DEFAULT 'total',
  PRIMARY KEY (id),
  CONSTRAINT fk_admin_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuario (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 7. TURNO
-- ------------------------------------------------------------
CREATE TABLE turno (
  id               INT        NOT NULL AUTO_INCREMENT,
  actividad_id     INT        NOT NULL,
  fecha            DATE       NOT NULL,
  horario_inicio   TIME       NOT NULL,
  horario_fin      TIME       NOT NULL,
  cupo_maximo      TINYINT    NOT NULL,
  cupo_disponible  TINYINT    NOT NULL,
  activo           TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  CONSTRAINT fk_turno_actividad FOREIGN KEY (actividad_id)
    REFERENCES actividad (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 8. RESERVA
-- ------------------------------------------------------------
CREATE TABLE reserva (
  id             INT            NOT NULL AUTO_INCREMENT,
  turno_id       INT            NOT NULL,
  usuario_id     INT            NOT NULL,
  fecha_reserva  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado         ENUM('confirmada','cancelada_usuario','cancelada_centro','pendiente_pago','asistio','ausente')
                                NOT NULL DEFAULT 'pendiente_pago',
  metodo_pago    ENUM('mercado_pago','efectivo','membresia') NOT NULL,
  monto_total    DECIMAL(10,2)  NOT NULL,
  monto_pagado   DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
  resultado_pago VARCHAR(100),                               -- respuesta de MP
  PRIMARY KEY (id),
  CONSTRAINT fk_reserva_turno   FOREIGN KEY (turno_id)   REFERENCES turno   (id) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_reserva_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 9. DEPOSITO  (seña / pago en efectivo registrado por empleado)
-- ------------------------------------------------------------
CREATE TABLE deposito (
  id           INT            NOT NULL AUTO_INCREMENT,
  reserva_id   INT            NOT NULL,
  empleado_id  INT,                                          -- NULL si fue online
  monto        DECIMAL(10,2)  NOT NULL,
  fecha        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  comprobante  VARCHAR(255),
  tipo         ENUM('senia','pago_total','pago_parcial') NOT NULL DEFAULT 'senia',
  PRIMARY KEY (id),
  CONSTRAINT fk_deposito_reserva  FOREIGN KEY (reserva_id)  REFERENCES reserva  (id) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_deposito_empleado FOREIGN KEY (empleado_id) REFERENCES empleado (id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 10. LISTA_ESPERA
-- ------------------------------------------------------------
CREATE TABLE lista_espera (
  id                  INT        NOT NULL AUTO_INCREMENT,
  turno_id            INT        NOT NULL,
  usuario_id          INT        NOT NULL,
  fecha_inscripcion   DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  posicion            SMALLINT   NOT NULL,
  estado              ENUM('en_espera','notificado','confirmado','expirado','cancelado')
                                 NOT NULL DEFAULT 'en_espera',
  fecha_notificacion  DATETIME,
  PRIMARY KEY (id),
  UNIQUE KEY uq_lista_espera_turno_usuario (turno_id, usuario_id),
  CONSTRAINT fk_le_turno   FOREIGN KEY (turno_id)   REFERENCES turno   (id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_le_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 11. LISTA_EJERCER  (empleado/profesor que dicta una actividad)
-- ------------------------------------------------------------
CREATE TABLE lista_ejercer (
  id            INT NOT NULL AUTO_INCREMENT,
  actividad_id  INT NOT NULL,
  empleado_id   INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_ejercer (actividad_id, empleado_id),
  CONSTRAINT fk_ejercer_actividad FOREIGN KEY (actividad_id) REFERENCES actividad (id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ejercer_empleado  FOREIGN KEY (empleado_id)  REFERENCES empleado  (id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 12. LISTA_ACTIVIDAD_PROFESOR  (empleado asignado a un turno puntual)
-- ------------------------------------------------------------
CREATE TABLE lista_actividad_profesor (
  id           INT NOT NULL AUTO_INCREMENT,
  turno_id     INT NOT NULL,
  empleado_id  INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_actividad_profesor (turno_id, empleado_id),
  CONSTRAINT fk_lap_turno    FOREIGN KEY (turno_id)    REFERENCES turno    (id) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_lap_empleado FOREIGN KEY (empleado_id) REFERENCES empleado (id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
--  FIN DEL SCRIPT
-- ============================================================