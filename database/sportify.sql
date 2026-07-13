CREATE DATABASE  IF NOT EXISTS `sportify` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `sportify`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: sportify
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actividad`
--

DROP TABLE IF EXISTS `actividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actividad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `precio_base` decimal(10,2) NOT NULL DEFAULT '0.00',
  `activa` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `actividad`
--

LOCK TABLES `actividad` WRITE;
/*!40000 ALTER TABLE `actividad` DISABLE KEYS */;
INSERT INTO `actividad` VALUES (1,'Fútbol','Canchas de césped sintético para fútbol 5 y 11.',20000.00,1),(2,'Básquet','Cancha cubierta de piso flotante profesional.',18000.00,1),(3,'Vóley','Turnos para vóley mixto e institucional.',18000.00,1),(4,'Pádel','Canchas de blindex de última generación.',16000.00,1),(5,'Crossfit Test','Prueba',15000.00,1),(6,'Crossfit Actualizado','Nueva descripcion',18000.00,1),(7,'Crossfit Test','Prueba',15000.00,0),(8,'Crossfit Test','Prueba',15000.00,0),(9,'Crossfit Test','Prueba',15000.00,1),(10,'Crossfit Test','Prueba',15000.00,1),(11,'Crossfit Test','Prueba',15000.00,0),(12,'Crossfit Test','Prueba',15000.00,0),(13,'Crossfit Test','Prueba',15000.00,1),(14,'Crossfit Test','Prueba',15000.00,1),(15,'Crossfit Test','Prueba',15000.00,0),(16,'Crossfit Test','Prueba',15000.00,0);
/*!40000 ALTER TABLE `actividad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `administrador`
--

DROP TABLE IF EXISTS `administrador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrador` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `nivel_acceso` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'total',
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `fk_admin_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrador`
--

LOCK TABLES `administrador` WRITE;
/*!40000 ALTER TABLE `administrador` DISABLE KEYS */;
INSERT INTO `administrador` VALUES (30,226,'total');
/*!40000 ALTER TABLE `administrador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificado`
--

DROP TABLE IF EXISTS `certificado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificado` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `numero` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_emision` date DEFAULT NULL,
  `fecha_vencimiento` date NOT NULL,
  `estado` enum('vigente','vencido','pendiente') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pendiente',
  PRIMARY KEY (`id`),
  KEY `fk_cert_usuario` (`usuario_id`),
  CONSTRAINT `fk_cert_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificado`
--

LOCK TABLES `certificado` WRITE;
/*!40000 ALTER TABLE `certificado` DISABLE KEYS */;
INSERT INTO `certificado` VALUES (1,231,NULL,NULL,'2027-01-01','vigente');
/*!40000 ALTER TABLE `certificado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clase`
--

DROP TABLE IF EXISTS `clase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clase` (
  `id` int NOT NULL AUTO_INCREMENT,
  `turno_id` int NOT NULL,
  `fecha` date NOT NULL,
  `cupo_disponible` tinyint NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_clase_turno_fecha` (`turno_id`,`fecha`),
  CONSTRAINT `fk_clase_turno` FOREIGN KEY (`turno_id`) REFERENCES `turno` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=744 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clase`
--

LOCK TABLES `clase` WRITE;
/*!40000 ALTER TABLE `clase` DISABLE KEYS */;
INSERT INTO `clase` VALUES (714,243,'2026-07-03',12,1),(715,243,'2026-07-10',10,1),(716,243,'2026-07-17',12,1),(717,243,'2026-07-24',12,1),(718,243,'2026-07-31',12,1),(719,244,'2026-07-07',12,1),(720,244,'2026-07-14',10,1),(721,244,'2026-07-21',12,1),(722,244,'2026-07-28',12,1),(723,245,'2026-07-01',0,1),(724,245,'2026-07-08',0,1),(725,245,'2026-07-15',0,1),(726,245,'2026-07-22',0,1),(727,245,'2026-07-29',0,1),(728,246,'2026-07-02',12,1),(729,246,'2026-07-09',10,1),(730,246,'2026-07-16',12,1),(731,246,'2026-07-23',12,1),(732,246,'2026-07-30',12,1),(733,247,'2026-07-06',11,1),(734,247,'2026-07-13',12,1),(735,247,'2026-07-20',12,1),(736,247,'2026-07-27',12,1),(737,248,'2026-07-12',11,1),(738,249,'2026-07-15',11,1),(739,250,'2026-07-24',0,1),(740,251,'2026-07-24',0,1),(741,252,'2026-07-12',11,1),(742,253,'2026-07-12',11,1),(743,254,'2026-07-12',11,1);
/*!40000 ALTER TABLE `clase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credito`
--

DROP TABLE IF EXISTS `credito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `credito` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `monto_descuento` decimal(5,2) NOT NULL DEFAULT '20.00',
  `mes` tinyint NOT NULL,
  `anio` smallint NOT NULL,
  `pagado` tinyint(1) NOT NULL DEFAULT '0',
  `fecha_pago` datetime DEFAULT NULL,
  `cancelaciones` tinyint NOT NULL DEFAULT '0',
  `descuento_activo` tinyint(1) NOT NULL DEFAULT '1',
  `clases_a_favor` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_credito_usuario_mes_anio` (`usuario_id`,`mes`,`anio`),
  CONSTRAINT `fk_credito_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credito`
--

LOCK TABLES `credito` WRITE;
/*!40000 ALTER TABLE `credito` DISABLE KEYS */;
INSERT INTO `credito` VALUES (41,233,20.00,7,2026,1,NULL,0,1,0),(42,236,20.00,7,2026,1,NULL,0,1,0);
/*!40000 ALTER TABLE `credito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deposito`
--

DROP TABLE IF EXISTS `deposito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deposito` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reserva_id` int NOT NULL,
  `empleado_id` int DEFAULT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `comprobante` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tipo` enum('senia','pago_total','pago_parcial') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'senia',
  PRIMARY KEY (`id`),
  KEY `fk_deposito_reserva` (`reserva_id`),
  KEY `fk_deposito_empleado` (`empleado_id`),
  CONSTRAINT `fk_deposito_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `empleado` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_deposito_reserva` FOREIGN KEY (`reserva_id`) REFERENCES `reserva` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deposito`
--

LOCK TABLES `deposito` WRITE;
/*!40000 ALTER TABLE `deposito` DISABLE KEYS */;
/*!40000 ALTER TABLE `deposito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `legajo` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cargo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `fk_empleado_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
INSERT INTO `empleado` VALUES (28,227,'EMP001','Recepcionista');
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lista_actividad_profesor`
--

DROP TABLE IF EXISTS `lista_actividad_profesor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lista_actividad_profesor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `clase_id` int NOT NULL,
  `empleado_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_actividad_profesor` (`clase_id`,`empleado_id`),
  KEY `fk_lap_empleado` (`empleado_id`),
  CONSTRAINT `fk_lap_clase` FOREIGN KEY (`clase_id`) REFERENCES `clase` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_lap_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `empleado` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lista_actividad_profesor`
--

LOCK TABLES `lista_actividad_profesor` WRITE;
/*!40000 ALTER TABLE `lista_actividad_profesor` DISABLE KEYS */;
/*!40000 ALTER TABLE `lista_actividad_profesor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lista_ejercer`
--

DROP TABLE IF EXISTS `lista_ejercer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lista_ejercer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `actividad_id` int NOT NULL,
  `empleado_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ejercer` (`actividad_id`,`empleado_id`),
  KEY `fk_ejercer_empleado` (`empleado_id`),
  CONSTRAINT `fk_ejercer_actividad` FOREIGN KEY (`actividad_id`) REFERENCES `actividad` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ejercer_empleado` FOREIGN KEY (`empleado_id`) REFERENCES `empleado` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lista_ejercer`
--

LOCK TABLES `lista_ejercer` WRITE;
/*!40000 ALTER TABLE `lista_ejercer` DISABLE KEYS */;
/*!40000 ALTER TABLE `lista_ejercer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lista_espera`
--

DROP TABLE IF EXISTS `lista_espera`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lista_espera` (
  `id` int NOT NULL AUTO_INCREMENT,
  `clase_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `fecha_inscripcion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `posicion` smallint NOT NULL,
  `estado` enum('en_espera','notificado','confirmado','expirado','cancelado') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en_espera',
  `fecha_notificacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lista_espera_clase_usuario` (`clase_id`,`usuario_id`),
  KEY `fk_le_usuario` (`usuario_id`),
  CONSTRAINT `fk_le_clase` FOREIGN KEY (`clase_id`) REFERENCES `clase` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_le_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lista_espera`
--

LOCK TABLES `lista_espera` WRITE;
/*!40000 ALTER TABLE `lista_espera` DISABLE KEYS */;
/*!40000 ALTER TABLE `lista_espera` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificacion`
--

DROP TABLE IF EXISTS `notificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `mensaje` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `leida` tinyint(1) DEFAULT '0',
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `notificacion_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificacion`
--

LOCK TABLES `notificacion` WRITE;
/*!40000 ALTER TABLE `notificacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `notificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reserva`
--

DROP TABLE IF EXISTS `reserva`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reserva` (
  `id` int NOT NULL AUTO_INCREMENT,
  `clase_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `fecha_reserva` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('confirmada','cancelada_usuario','cancelada_centro','pendiente_pago','asistio','ausente') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pendiente_pago',
  `metodo_pago` enum('tarjeta_virtual','efectivo','membresia') COLLATE utf8mb4_unicode_ci NOT NULL,
  `monto_total` decimal(10,2) NOT NULL,
  `monto_pagado` decimal(10,2) NOT NULL DEFAULT '0.00',
  `resultado_pago` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_reserva_clase` (`clase_id`),
  KEY `fk_reserva_usuario` (`usuario_id`),
  CONSTRAINT `fk_reserva_clase` FOREIGN KEY (`clase_id`) REFERENCES `clase` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_reserva_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=289 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reserva`
--

LOCK TABLES `reserva` WRITE;
/*!40000 ALTER TABLE `reserva` DISABLE KEYS */;
INSERT INTO `reserva` VALUES (47,741,228,'2026-07-12 23:08:37','confirmada','efectivo',20000.00,20000.00,NULL),(48,742,229,'2026-07-12 23:08:37','confirmada','efectivo',20000.00,20000.00,NULL),(49,743,230,'2026-07-12 23:08:37','confirmada','efectivo',20000.00,20000.00,NULL),(50,741,228,'2026-07-12 23:08:37','cancelada_usuario','efectivo',20000.00,10000.00,NULL),(267,715,228,'2026-07-12 23:08:37','pendiente_pago','tarjeta_virtual',20000.00,10000.00,NULL),(268,720,228,'2026-07-12 23:08:37','pendiente_pago','tarjeta_virtual',18000.00,9000.00,NULL),(269,723,228,'2026-07-12 23:08:37','pendiente_pago','tarjeta_virtual',16000.00,8000.00,NULL),(270,729,228,'2026-07-12 23:08:37','pendiente_pago','tarjeta_virtual',18000.00,9000.00,NULL),(271,733,228,'2026-07-12 23:08:37','pendiente_pago','tarjeta_virtual',20000.00,10000.00,NULL),(272,737,228,'2026-07-12 23:08:37','pendiente_pago','tarjeta_virtual',18000.00,9000.00,NULL),(273,715,229,'2026-07-12 23:08:37','pendiente_pago','efectivo',20000.00,10000.00,NULL),(274,720,229,'2026-07-12 23:08:37','pendiente_pago','efectivo',18000.00,9000.00,NULL),(275,724,229,'2026-07-12 23:08:37','pendiente_pago','efectivo',16000.00,8000.00,NULL),(276,729,229,'2026-07-12 23:08:37','pendiente_pago','efectivo',18000.00,9000.00,NULL),(277,739,233,'2026-07-12 23:08:37','confirmada','efectivo',20000.00,20000.00,NULL),(278,740,234,'2026-07-12 23:08:37','confirmada','efectivo',20000.00,10000.00,NULL),(279,733,228,'2026-07-12 23:08:37','asistio','efectivo',20000.00,20000.00,NULL),(280,733,228,'2026-07-12 23:08:37','asistio','efectivo',20000.00,20000.00,NULL),(281,733,228,'2026-07-12 23:08:37','asistio','efectivo',20000.00,20000.00,NULL),(282,733,228,'2026-07-12 23:08:37','asistio','efectivo',20000.00,20000.00,NULL),(283,733,228,'2026-07-12 23:08:37','asistio','efectivo',20000.00,20000.00,NULL),(284,719,229,'2026-07-12 23:08:37','asistio','efectivo',18000.00,18000.00,NULL),(285,728,228,'2026-07-12 23:08:37','asistio','efectivo',18000.00,18000.00,NULL),(286,734,229,'2026-07-12 23:08:37','cancelada_usuario','efectivo',20000.00,10000.00,NULL),(287,720,228,'2026-07-12 23:08:37','cancelada_centro','efectivo',18000.00,9000.00,NULL),(288,729,237,'2026-07-12 23:08:37','confirmada','tarjeta_virtual',18000.00,9000.00,NULL);
/*!40000 ALTER TABLE `reserva` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `turno`
--

DROP TABLE IF EXISTS `turno`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `turno` (
  `id` int NOT NULL AUTO_INCREMENT,
  `actividad_id` int NOT NULL,
  `dia_semana` enum('lunes','martes','miercoles','jueves','viernes') COLLATE utf8mb4_unicode_ci NOT NULL,
  `horario_inicio` time NOT NULL,
  `horario_fin` time NOT NULL,
  `cupo_maximo` tinyint NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_turno_franja` (`actividad_id`,`dia_semana`,`horario_inicio`),
  CONSTRAINT `fk_turno_actividad` FOREIGN KEY (`actividad_id`) REFERENCES `actividad` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=255 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `turno`
--

LOCK TABLES `turno` WRITE;
/*!40000 ALTER TABLE `turno` DISABLE KEYS */;
INSERT INTO `turno` VALUES (243,1,'viernes','18:00:00','19:00:00',12,1),(244,3,'martes','17:00:00','18:00:00',12,1),(245,4,'miercoles','19:00:00','20:00:00',4,1),(246,2,'jueves','14:00:00','15:00:00',12,1),(247,1,'lunes','10:00:00','11:00:00',12,1),(248,2,'lunes','00:08:00','01:08:00',12,1),(249,1,'miercoles','23:08:00','00:08:00',12,1),(250,1,'viernes','20:00:00','21:00:00',1,1),(251,1,'viernes','21:00:00','22:00:00',1,1),(252,1,'martes','23:03:00','00:08:00',12,1),(253,1,'miercoles','08:00:00','09:00:00',12,1),(254,1,'jueves','23:00:00','23:59:00',12,1);
/*!40000 ALTER TABLE `turno` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dni` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_alta` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `token_recuperacion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `token_recuperacion_usado` tinyint NOT NULL DEFAULT '0',
  `email_confirmado` tinyint NOT NULL DEFAULT '0',
  `ultimo_recordatorio_enviado` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dni` (`dni`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=238 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (226,'Nicolás','Montanari','12345678','admin@sportify.com','scrypt:32768:8:1$VoJP5aru4h62CD30$4fcfafc12951728961dc7666e2fcb97f37952fefe18ca35a3f61ed625efcb750ae034b2e6dbe0905d4a4d9ba57c68d52a71b4f946568991e777612dd862bc9ae','1995-10-10',1,'2026-07-13 02:08:36',NULL,0,0,NULL),(227,'Mario','Gomez','55555555','empleado@sportify.com','scrypt:32768:8:1$JE6f5RpQ02S3x95Y$fbaaa7a83e15a3b55c935289380e1ce03e7fc25c583d1b648ca4305665f4eaaa8fe343f694280890c72c7ac6d4c38c03a59dcd0f6dd486e0eec0bc9b60021674','1990-05-15',1,'2026-07-13 02:08:37',NULL,0,0,NULL),(228,'Juan','Perez','99999999','casual@sportify.com','scrypt:32768:8:1$j8kUfP5Y3eR9x7Th$5c881745cc60c6f89c7c4fbcdd795ad143d0db4420bc5d37e5d6baef84207b1295e7c4cfb8f91c9f56e6b84a777f40765a0b1fb95790deb84b7b20f6c3180919','1995-03-20',1,'2026-07-13 02:08:37',NULL,0,0,NULL),(229,'Luis','Gonzalez','88888888','luis@sportify.com','scrypt:32768:8:1$t7DfDrP9rwCfLptG$dc8827a997f6943bfa439ec03b5a27f44cdfee694327d42b9b38e32356c95fb892ccbdf98ee788894a2e14595559b6226dd431adc3ed386a600ac2805846267d','1993-06-10',1,'2026-07-13 02:08:37',NULL,0,0,NULL),(230,'Gonzalo','Lopez','22555111','gonzalo@sportify.com','scrypt:32768:8:1$O9CFsvZsYNubJiM5$847cc974d1739490f4c7425e85dd3a64bce8c9a35f36376d207c52eef138adeac3aff082c4ce8fd8bfdd4fbaa1538b1e090ce4af0e81a3bbe99bca0d06f58b81','1988-11-05',1,'2026-07-13 02:08:37',NULL,0,0,NULL),(231,'Carlos','Gomez','33333333','abonado@sportify.com','scrypt:32768:8:1$kiqpytDoOPecpn4x$f788eaf121c962cb76b3edf0a8fe6c414bfff89201059a56a214d94713a4783a41609dd4e3baabb30515a5008ed969261adf9156053ddf86de22f7a4edcb68e3','1990-05-15',1,'2026-07-13 02:08:37',NULL,0,0,NULL),(232,'Pedro','Garcia','11122233','baja@sportify.com','scrypt:32768:8:1$uoICp7QT9kPz2qKj$5107f8b0f38ee7fbe28c6b821f1af4ab7349236de39c488f6e80316d85112fba2165b57ff6ebd27db4e9fd9ae402d706d2b3afb87572ea3df801ef20db3afc05','1990-05-15',0,'2026-07-13 02:08:37',NULL,0,0,NULL),(233,'Titular','Abonado','10000001','titular@sportify.com','scrypt:32768:8:1$uTex5oDguokWOB0C$f5e77efcb4af1481938289524db28955cc1ea6edac39aa47fcbb935c49ece8028bf15a73f67c6c5fe8de719d269335221de388e3d6d16215fb4ed2bf898ee928','1990-01-01',1,'2026-07-13 02:08:37',NULL,0,0,NULL),(234,'Titular','Casual','10000004','titular.casual@sportify.com','scrypt:32768:8:1$5PGDn57emhgSL45U$fd73976bd98b0e08228a767c7de1c4663ff9f78819bb1e8a660310e4a68522dfc1e9c709e4cf91d14e483642d3df87703127856ef276f31e08ab4474c4d453e4','1990-01-01',1,'2026-07-13 02:08:38',NULL,0,0,NULL),(235,'Espera','Casual','10000002','espera.casual@sportify.com','scrypt:32768:8:1$1leUrDYp4CI9fVgt$13058cf2538f978f5752a9338b19602a73567178e0e32f5e702f178bf52647526435e0e343f814d8271d7d2cce86901413fe23a34a3bf0a4f94e6d53a02c7cff','1990-01-01',1,'2026-07-13 02:08:38',NULL,0,0,NULL),(236,'Espera','Abonado','10000003','espera.abonado@sportify.com','scrypt:32768:8:1$fMs7axn96OaPB5C3$7ad22be14b854a8ee13c303563fcf22155731cfce113ea5d278f6bdbce6e1885b8c00a1043693afbd371977ba42543a78438a242719eea829d5b13c9bae110e3','1990-01-01',1,'2026-07-13 02:08:38',NULL,0,0,NULL),(237,'Moroso','Demo','10000099','moroso@sportify.com','scrypt:32768:8:1$UdVCjLN1WaIOCDmb$6100d272194786ca4dcb8e0119a8df1d63b411cf42472e22bf5754f4019ec7e58c5decdefab7256a7340bc94f46fe16924d2411951f173ecfca6a10ba3c03347','1992-04-04',1,'2026-07-13 02:08:38',NULL,0,0,NULL);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-12 23:13:50
