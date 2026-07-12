CREATE DATABASE veterinaria_db;
USE veterinaria_db;

-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)

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
-- Table structure for table `Administrador`
--

DROP TABLE IF EXISTS `Administrador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Administrador` (
  `id_administrador` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido_paterno` varchar(50) NOT NULL,
  `apellido_materno` varchar(50) NOT NULL,
  `dni` char(8) NOT NULL,
  `telefono` char(9) NOT NULL,
  `email` varchar(100) NOT NULL,
  `fecha_ingreso` date NOT NULL,
  `genero` char(1) NOT NULL,
  PRIMARY KEY (`id_administrador`),
  UNIQUE KEY `id_usuario` (`id_usuario`),
  UNIQUE KEY `dni` (`dni`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `Administrador_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `Administrador_chk_1` CHECK (((trim(`nombre`) <> _utf8mb4'') and (length(trim(`nombre`)) >= 2))),
  CONSTRAINT `Administrador_chk_2` CHECK (((trim(`apellido_paterno`) <> _utf8mb4'') and (length(trim(`apellido_paterno`)) >= 2))),
  CONSTRAINT `Administrador_chk_3` CHECK (((trim(`apellido_materno`) <> _utf8mb4'') and (length(trim(`apellido_materno`)) >= 2))),
  CONSTRAINT `Administrador_chk_4` CHECK (regexp_like(`dni`,_utf8mb4'^[0-9]{8}')),
  CONSTRAINT `Administrador_chk_5` CHECK (regexp_like(`telefono`,_utf8mb4'^9[0-9]{8}$')),
  CONSTRAINT `Administrador_chk_6` CHECK (regexp_like(`email`,_utf8mb4'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,}$')),
  CONSTRAINT `Administrador_chk_7` CHECK ((`genero` in (_utf8mb4'F',_utf8mb4'M')))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Administrador`
--

LOCK TABLES `Administrador` WRITE;
/*!40000 ALTER TABLE `Administrador` DISABLE KEYS */;
INSERT INTO `Administrador` VALUES (1,1,'Carlos','Mendoza','Vega','12345678','987654321','carlos.mendoza@veterinaria.com','2024-01-15','M'),(2,2,'Ana','Torres','Silva','87654321','912345678','ana.torres@veterinaria.com','2024-03-10','F'),(3,19,'David','Sevantini','Reyesini','72649591','967819339','davidcitotuterror2@gmail.com','2025-07-07','M'),(4,21,'Juan Felipe','Gepeto','Pingostini','96874165','967819340','lostilinesnegrinis@gmail.com','2025-07-07','M'),(5,25,'Jose','Diaz','Luna','45678901','965432123','jose@gmail.com','2025-07-08','M');
/*!40000 ALTER TABLE `Administrador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Cita`
--

DROP TABLE IF EXISTS `Cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cita` (
    `id_cita` int NOT NULL AUTO_INCREMENT,
    `id_mascota` int DEFAULT NULL,
    `id_servicio_solicitado` int DEFAULT NULL,
    `fecha_hora_programada` datetime NOT NULL,
    `estado_cita` enum('Programada','Cancelada','Atendida') DEFAULT 'Programada',
    `requiere_ayuno` tinyint(1) DEFAULT NULL,
    `observaciones` text,
    `recordatorio_24h_enviado` tinyint(1) DEFAULT '0',
    `recordatorio_4h_enviado` tinyint(1) DEFAULT '0',

  PRIMARY KEY (`id_cita`),
  KEY `id_mascota` (`id_mascota`),
  KEY `id_servicio_solicitado` (`id_servicio_solicitado`),
  CONSTRAINT `Cita_ibfk_1` FOREIGN KEY (`id_mascota`) REFERENCES `Mascota` (`id_mascota`),
  CONSTRAINT `Cita_ibfk_2` FOREIGN KEY (`id_servicio_solicitado`) REFERENCES `Servicio_Solicitado` (`id_servicio_solicitado`),
  CONSTRAINT `Cita_chk_1` CHECK (((`observaciones` is null) or (length(trim(`observaciones`)) >= 3)))
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cita`
--

LOCK TABLES `Cita` WRITE;
/*!40000 ALTER TABLE `Cita` DISABLE KEYS */;
INSERT INTO `Cita` VALUES (1,9,2,'2025-06-07 14:00:00','Atendida',0,'Desparasitación aplicada',0,0),(2,3,4,'2025-05-26 09:00:00','Atendida',1,'Análisis hemograma',0,0),(3,4,5,'2025-05-29 10:00:00','Atendida',1,'Perfil bioquímico',0,0),(4,5,7,'2025-05-31 08:00:00','Atendida',0,'Radiografía pata trasera',0,0),(5,8,3,'2025-06-09 16:00:00','Programada',0,'Primera vacuna séxtuple',0,0),(6,7,6,'2025-06-10 09:00:00','Programada',1,'Perfil renal geriátrico',0,0),(7,10,8,'2025-06-09 10:00:00','Programada',0,'Control herida quirúrgica',0,0),(8,1,NULL,'2025-06-12 11:00:00','Programada',0,'Control preventivo anual',0,0),(9,6,NULL,'2025-06-15 14:00:00','Programada',1,'Chequeo completo',0,0),(10,3,3,'2025-07-10 10:00:00','Programada',1,'Vacuna Séxtuple oh',0,0),(11,1,9,'2025-07-08 08:07:40','Programada',1,'Posible enfermedad',0,0),(13,1,11,'2025-07-08 08:07:40','Programada',1,'Posible enfermedad',0,0),(14,1,12,'2025-07-08 08:07:40','Programada',1,'Posible enfermedad',0,0),(15,1,13,'2025-08-01 09:21:00','Programada',0,NULL,0,0),(16,4,14,'2025-07-17 09:21:00','Programada',1,NULL,0,0),(17,8,15,'2025-07-18 09:27:00','Programada',0,NULL,0,0),(18,14,14,'2025-07-10 07:14:00','Programada',1,'Esta muy flaco',0,0);
/*!40000 ALTER TABLE `Cita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Cliente`
--

DROP TABLE IF EXISTS `Cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cliente` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellido_paterno` varchar(50) NOT NULL,
  `apellido_materno` varchar(50) NOT NULL,
  `dni` char(8) NOT NULL,
  `telefono` char(9) NOT NULL,
  `email` varchar(100) NOT NULL,
  `direccion` text,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  `genero` char(1) NOT NULL,
  `estado` enum('Activo','Inactivo') DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `dni` (`dni`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `Cliente_chk_1` CHECK (((trim(`nombre`) <> _utf8mb4'') and (length(trim(`nombre`)) >= 2))),
  CONSTRAINT `Cliente_chk_2` CHECK (((trim(`apellido_paterno`) <> _utf8mb4'') and (length(trim(`apellido_paterno`)) >= 2))),
  CONSTRAINT `Cliente_chk_3` CHECK (((trim(`apellido_materno`) <> _utf8mb4'') and (length(trim(`apellido_materno`)) >= 2))),
  CONSTRAINT `Cliente_chk_4` CHECK (regexp_like(`dni`,_utf8mb4'^[0-9]{8}')),
  CONSTRAINT `Cliente_chk_5` CHECK (regexp_like(`telefono`,_utf8mb4'^9[0-9]{8}$')),
  CONSTRAINT `Cliente_chk_6` CHECK (regexp_like(`email`,_utf8mb4'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,}$')),
  CONSTRAINT `Cliente_chk_7` CHECK ((`genero` in (_utf8mb4'F',_utf8mb4'M')))
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cliente`
--

LOCK TABLES `Cliente` WRITE;
/*!40000 ALTER TABLE `Cliente` DISABLE KEYS */;
INSERT INTO `Cliente` VALUES (1,'María','González','Perota','45678901','987123456','maria.gonzalez@email.com','Av. Los Olivos 123, San Isidro','2025-06-09 03:31:23','F','Activo'),(2,'Juan','Rodríguez','López','56789012','987234567','juan.rodriguez@email.com','Jr. Las Flores 456, Miraflores','2025-06-09 03:31:23','M','Activo'),(3,'Carmen','Silva','Martín','67890123','987345678','carmen.silva@email.com','Av. Brasil 789, Magdalena','2025-06-09 03:31:23','F','Activo'),(4,'Pedro','Vásquez','Torres','78901234','987456789','pedro.vasquez@email.com','Calle Luna 321, San Borja','2025-06-09 03:31:23','M','Activo'),(5,'Lucía','Herrera','Ramos','89012345','987567890','lucia.herrera@email.com','Av. Petit Thouars 654, Lince','2025-06-09 03:31:23','F','Activo'),(6,'Miguel','Castro','Mendoza','90123456','987678901','miguel.castro@email.com','Jr. Camaná 987, Lima','2025-06-09 03:31:23','M','Activo'),(7,'Rosa','Morales','Díaz','01234567','987789012','rosa.morales@email.com','Av. Arequipa 147, La Victoria','2025-06-09 03:31:23','F','Activo'),(8,'Diego','Paredes','Gutiérrez','12340567','987890123','diego.paredes@email.com','Calle Real 258, Surco','2025-06-09 03:31:23','M','Activo'),(9,'Sofía','Ramírez','Flores','23450678','987901234','sofia.ramirez@email.com','Av. Universitaria 369, Los Olivos','2025-06-09 03:31:23','F','Activo'),(10,'Carlos','Fernández','Ruiz','34560789','987012345','carlos.fernandez@email.com','Jr. Huancavelica 741, Cercado','2025-06-09 03:31:23','M','Activo'),(11,'Kevin','Boh','Hua','71426213','918869297','kevinbohorquez0211@gmail.com','Union 1018 El agustino','2025-06-09 05:34:08','M','Inactivo'),(12,'David','Sevan','Reyes','72649591','967819339','david@gmail.com','jr.mollocarma 164','2025-06-10 02:33:13','M','Inactivo'),(13,'Lita','Huanca','Tapia','72443752','967572673','litaht2004@gmail.com','Av. Palmeras 112, Los Olivos','2025-06-10 05:38:08','F','Activo'),(14,'Nicolás','De Las Casas','Pampañaupa','72443721','945634344','ricolas123cp@gmail.com','Las Lomas, San Isidro','2025-06-10 19:28:39','M','Inactivo'),(15,'Paolo','Guerrero','Campos','72443645','987654321','paolo.guerrero@gmail.com','Av. Principal 123','2025-06-11 04:22:36','M','Activo'),(16,'Andrea','Lopez','Martinez','72443722','934123233','andreita1421@gmail.com','Las Lomas Del Campo Miraflores','2025-06-11 09:11:21','F','Activo'),(17,'Brat','Pitt','Mamani','72443546','967543432','brattpit12@gmail.com','Hollywood Bonito','2025-07-06 22:54:07','M','Activo'),(18,'Rosa','Maceta','Flores','45678904','901234567','rosa123@gmail.com','rosa123','2025-07-08 09:55:39','F','Activo');
/*!40000 ALTER TABLE `Cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Cliente_Mascota`
--

DROP TABLE IF EXISTS `Cliente_Mascota`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cliente_Mascota` (
  `id_cliente_mascota` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int DEFAULT NULL,
  `id_mascota` int DEFAULT NULL,
  PRIMARY KEY (`id_cliente_mascota`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_mascota` (`id_mascota`),
  CONSTRAINT `Cliente_Mascota_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `Cliente` (`id_cliente`),
  CONSTRAINT `Cliente_Mascota_ibfk_2` FOREIGN KEY (`id_mascota`) REFERENCES `Mascota` (`id_mascota`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cliente_Mascota`
--

LOCK TABLES `Cliente_Mascota` WRITE;
/*!40000 ALTER TABLE `Cliente_Mascota` DISABLE KEYS */;
INSERT INTO `Cliente_Mascota` VALUES (1,1,1),(2,1,2),(3,2,3),(4,3,4),(5,3,5),(6,4,6),(7,5,7),(8,6,8),(9,7,9),(10,8,10),(11,9,11),(12,10,12),(13,13,13),(14,13,14),(16,18,16);
/*!40000 ALTER TABLE `Cliente_Mascota` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Consulta`
--

DROP TABLE IF EXISTS `Consulta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Consulta` (
  `id_consulta` int NOT NULL AUTO_INCREMENT,
  `id_triaje` int NOT NULL,
  `id_veterinario` int NOT NULL,
  `tipo_consulta` varchar(100) NOT NULL,
  `fecha_consulta` datetime NOT NULL,
  `motivo_consulta` text,
  `sintomas_observados` text,
  `diagnostico_preliminar` text,
  `observaciones` text,
  `condicion_general` enum('Excelente','Buena','Regular','Mala','Critica') NOT NULL,
  `es_seguimiento` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_consulta`),
  KEY `id_triaje` (`id_triaje`),
  KEY `id_veterinario` (`id_veterinario`),
  CONSTRAINT `Consulta_ibfk_1` FOREIGN KEY (`id_triaje`) REFERENCES `Triaje` (`id_triaje`),
  CONSTRAINT `Consulta_ibfk_2` FOREIGN KEY (`id_veterinario`) REFERENCES `Veterinario` (`id_veterinario`),
  CONSTRAINT `Consulta_chk_1` CHECK (((trim(`tipo_consulta`) <> _utf8mb4'') and (length(trim(`tipo_consulta`)) >= 5))),
  CONSTRAINT `Consulta_chk_2` CHECK (((`motivo_consulta` is null) or (length(trim(`motivo_consulta`)) >= 5))),
  CONSTRAINT `Consulta_chk_3` CHECK (((`sintomas_observados` is null) or (length(trim(`sintomas_observados`)) >= 5))),
  CONSTRAINT `Consulta_chk_4` CHECK (((`diagnostico_preliminar` is null) or (length(trim(`diagnostico_preliminar`)) >= 5))),
  CONSTRAINT `Consulta_chk_5` CHECK (((`observaciones` is null) or (length(trim(`observaciones`)) >= 3)))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Consulta`
--

LOCK TABLES `Consulta` WRITE;
/*!40000 ALTER TABLE `Consulta` DISABLE KEYS */;
INSERT INTO `Consulta` VALUES (1,1,1,'Consulta de rutina','2025-05-15 09:30:00','Control de salud general','Animal activo, buen apetito','Animal sano','Mantener rutina de ejercicio','Excelente',0),(2,2,1,'Consulta preventiva','2025-05-20 11:00:00','Vacunación anual','Sin síntomas aparentes','Animal sano para vacunación','Aplicar vacuna triple felina','Buena',0),(3,3,2,'Consulta de urgencia','2025-05-25 14:30:00','Vómitos y diarrea','Vómitos frecuentes, diarrea, letargo','Gastroenteritis aguda','Iniciar tratamiento sintomático','Regular',0),(4,4,3,'Consulta especializada','2025-05-28 11:30:00','Problemas de piel','Picazón excesiva, enrojecimiento','Dermatitis alérgica','Evitar alérgenos conocidos','Excelente',0),(5,5,4,'Consulta de urgencia','2025-05-30 21:00:00','Cojera en pata trasera','Dificultad para caminar','Posible esguince','Reposo y antiinflamatorios','Regular',0),(6,6,2,'Consulta de rutina','2025-06-03 16:00:00','Revisión general','Animal energético, come bien','Animal sano','Continuar cuidados actuales','Excelente',0),(7,7,1,'Consulta geriátrica','2025-06-05 09:00:00','Control de edad avanzada','Leve rigidez articular','Cambios propios de la edad','Considerar suplementos articulares','Buena',0),(8,8,2,'Consulta pediátrica','2025-06-06 16:30:00','Primera consulta cachorro','Cachorro activo, primer control','Animal sano','Iniciar plan vacunal','Excelente',0),(9,9,4,'Consulta preventiva','2025-06-07 10:00:00','Desparasitación','Sin síntomas, control rutinario','Animal sano','Aplicar desparasitante','Buena',0),(10,10,1,'Consulta de seguimiento','2025-06-08 11:30:00','Control post-cirugía','Herida cicatrizando bien','Evolución favorable','Continuar cuidados','Buena',1),(11,11,3,'Consulta general','2025-07-08 02:56:57',NULL,NULL,NULL,NULL,'Regular',0),(12,12,3,'Consulta general','2025-07-08 05:00:50',NULL,NULL,NULL,NULL,'Regular',0);
/*!40000 ALTER TABLE `Consulta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Diagnostico`
--

DROP TABLE IF EXISTS `Diagnostico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Diagnostico` (
  `id_diagnostico` int NOT NULL AUTO_INCREMENT,
  `id_consulta` int DEFAULT NULL,
  `id_patologia` int DEFAULT NULL,
  `tipo_diagnostico` enum('Presuntivo','Confirmado','Descartado') DEFAULT NULL,
  `fecha_diagnostico` datetime DEFAULT NULL,
  `estado_patologia` enum('Activa','Controlada','Curada','En seguimiento') DEFAULT NULL,
  `diagnostico` text,
  PRIMARY KEY (`id_diagnostico`),
  KEY `id_consulta` (`id_consulta`),
  KEY `id_patologia` (`id_patologia`),
  CONSTRAINT `Diagnostico_ibfk_1` FOREIGN KEY (`id_consulta`) REFERENCES `Consulta` (`id_consulta`),
  CONSTRAINT `Diagnostico_ibfk_2` FOREIGN KEY (`id_patologia`) REFERENCES `Patologia` (`id_patologia`),
  CONSTRAINT `Diagnostico_chk_1` CHECK ((length(trim(`diagnostico`)) >= 5))
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Diagnostico`
--

LOCK TABLES `Diagnostico` WRITE;
/*!40000 ALTER TABLE `Diagnostico` DISABLE KEYS */;
INSERT INTO `Diagnostico` VALUES (1,3,6,'Confirmado','2025-05-25 15:00:00','Curada','Gastroenteritis aguda por probable indiscreción alimentaria'),(2,4,4,'Confirmado','2025-05-28 12:00:00','Controlada','Dermatitis alérgica por contacto, respondiendo bien al tratamiento'),(3,9,9,'Descartado','2025-06-07 10:30:00','Activa','Se descarta parasitosis tras análisis negativo'),(4,7,11,'Presuntivo','2025-06-05 09:30:00','En seguimiento','Displasia de cadera leve en animal geriátrico, requiere monitoreo'),(16,4,29,'Confirmado','2025-07-08 06:59:49','Activa','Diagnósticazo'),(17,4,30,'Presuntivo','2025-07-08 07:03:43','Activa','Mal de altura'),(18,5,31,'Presuntivo','2025-07-08 07:10:05','Activa','Diagnóstico inicial'),(19,2,32,'Presuntivo','2025-07-08 07:13:47','Activa','Diagnóstico inicial'),(20,2,33,'Presuntivo','2025-07-08 07:15:31','Activa','Malito');
/*!40000 ALTER TABLE `Diagnostico` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `before_diagnostico_insert` BEFORE INSERT ON `Diagnostico` FOR EACH ROW BEGIN
    -- 1. Insertamos la patología con valores por defecto para los campos opcionales
    INSERT INTO Patologia (nombre_patologia, especie_afecta, gravedad, es_crónica, es_contagiosa)
    VALUES (NULL, 'Ambas', 'Moderada', False, False);  -- Asignamos valores por defecto en lugar de NULL
    
    -- 2. Obtenemos el id_patologia recién insertado
    SET @id_patologia = LAST_INSERT_ID();  -- Asignamos el id de la nueva patología

    -- 3. Insertamos el tratamiento con el id_patologia recién creado y valores por defecto
    INSERT INTO Tratamiento (id_consulta, id_patologia, fecha_inicio, eficacia_tratamiento, tipo_tratamiento)
    VALUES (NEW.id_consulta, @id_patologia, NOW(), 'Regular', 'Medicamentoso');  -- Valores por defecto

    -- 4. Asignamos el id_patologia al diagnóstico
    SET NEW.id_patologia = @id_patologia;  -- Asignamos el id_patologia en el diagnóstico
    
    -- 5. Asignamos la fecha actual al campo fecha_diagnostico
    SET NEW.fecha_diagnostico = NOW();  -- Asigna la fecha y hora actuales

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `Especialidad`
--

DROP TABLE IF EXISTS `Especialidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Especialidad` (
  `id_especialidad` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Especialidad`
--

LOCK TABLES `Especialidad` WRITE;
/*!40000 ALTER TABLE `Especialidad` DISABLE KEYS */;
INSERT INTO `Especialidad` VALUES (1,'Medicina General'),(2,'Cirugía Veterinaria'),(3,'Dermatología Veterinaria'),(4,'Cardiología Veterinaria'),(5,'Oftalmología Veterinaria'),(6,'Traumatología'),(7,'Medicina Interna'),(8,'Anestesiología'),(9,'Oncología Veterinaria'),(10,'Neurología Veterinaria');
/*!40000 ALTER TABLE `Especialidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Historial_clinico`
--

DROP TABLE IF EXISTS `Historial_clinico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Historial_clinico` (
  `id_historial` int NOT NULL AUTO_INCREMENT,
  `id_mascota` int DEFAULT NULL,
  `id_consulta` int DEFAULT NULL,
  `id_diagnostico` int DEFAULT NULL,
  `id_tratamiento` int DEFAULT NULL,
  `id_veterinario` int DEFAULT NULL,
  `fecha_evento` datetime NOT NULL,
  `tipo_evento` varchar(100) NOT NULL,
  `edad_meses` int DEFAULT NULL,
  `descripcion_evento` text NOT NULL,
  `peso_momento` decimal(5,2) DEFAULT NULL,
  `observaciones` text,
  PRIMARY KEY (`id_historial`),
  KEY `id_mascota` (`id_mascota`),
  KEY `id_consulta` (`id_consulta`),
  KEY `id_diagnostico` (`id_diagnostico`),
  KEY `id_tratamiento` (`id_tratamiento`),
  KEY `id_veterinario` (`id_veterinario`),
  CONSTRAINT `Historial_clinico_ibfk_1` FOREIGN KEY (`id_mascota`) REFERENCES `Mascota` (`id_mascota`),
  CONSTRAINT `Historial_clinico_ibfk_2` FOREIGN KEY (`id_consulta`) REFERENCES `Consulta` (`id_consulta`),
  CONSTRAINT `Historial_clinico_ibfk_3` FOREIGN KEY (`id_diagnostico`) REFERENCES `Diagnostico` (`id_diagnostico`),
  CONSTRAINT `Historial_clinico_ibfk_4` FOREIGN KEY (`id_tratamiento`) REFERENCES `Tratamiento` (`id_tratamiento`),
  CONSTRAINT `Historial_clinico_ibfk_5` FOREIGN KEY (`id_veterinario`) REFERENCES `Veterinario` (`id_veterinario`),
  CONSTRAINT `Historial_clinico_chk_1` CHECK (((trim(`tipo_evento`) <> _utf8mb4'') and (length(trim(`tipo_evento`)) >= 4))),
  CONSTRAINT `Historial_clinico_chk_2` CHECK (((`edad_meses` >= 0) and (`edad_meses` <= 300))),
  CONSTRAINT `Historial_clinico_chk_3` CHECK ((length(trim(`descripcion_evento`)) >= 5)),
  CONSTRAINT `Historial_clinico_chk_4` CHECK (((`peso_momento` > 0) and (`peso_momento` <= 200))),
  CONSTRAINT `Historial_clinico_chk_5` CHECK (((`observaciones` is null) or (length(trim(`observaciones`)) >= 3)))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Historial_clinico`
--

LOCK TABLES `Historial_clinico` WRITE;
/*!40000 ALTER TABLE `Historial_clinico` DISABLE KEYS */;
INSERT INTO `Historial_clinico` VALUES (1,1,1,NULL,NULL,1,'2025-05-15 09:30:00','Consulta de rutina',42,'Control de salud general - animal en excelente estado',25.50,'Mantener rutina actual'),(2,2,2,NULL,NULL,1,'2025-05-20 11:00:00','Vacunación',24,'Aplicación de vacuna triple felina - sin reacciones adversas',4.20,'Próxima vacuna en 1 año'),(3,3,3,1,1,2,'2025-05-25 14:30:00','Consulta urgente',62,'Episodio de gastroenteritis tratado exitosamente',35.80,'Respuesta favorable al tratamiento'),(4,4,4,2,2,3,'2025-05-28 11:30:00','Consulta dermatología',20,'Dermatitis alérgica en tratamiento',3.80,'Evitar contacto con alérgenos'),(5,5,5,NULL,3,4,'2025-05-30 21:00:00','Consulta traumatología',48,'Esguince en miembro posterior derecho',6.50,'Reposo absoluto por 10 días'),(6,6,6,NULL,NULL,2,'2025-06-03 16:00:00','Control preventivo',30,'Revisión general - animal en perfecto estado',18.20,'Continuar cuidados actuales'),(7,7,7,4,4,1,'2025-06-05 09:00:00','Control geriátrico',72,'Evaluación geriátrica - displasia leve detectada',42.30,'Iniciar suplementos articulares'),(8,8,8,NULL,NULL,2,'2025-06-06 16:30:00','Primera consulta',22,'Primera consulta de cachorro - excelente estado',1.80,'Iniciar programa vacunal'),(9,9,9,3,NULL,4,'2025-06-07 10:00:00','Desparasitación',40,'Desparasitación preventiva aplicada',4.80,'Sin parásitos detectados'),(10,10,10,NULL,NULL,1,'2025-06-08 11:30:00','Control post-cirugía',56,'Seguimiento post-esterilización - evolución favorable',28.50,'Herida cicatrizando correctamente');
/*!40000 ALTER TABLE `Historial_clinico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Mascota`
--

DROP TABLE IF EXISTS `Mascota`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Mascota` (
  `id_mascota` int NOT NULL AUTO_INCREMENT,
  `id_raza` int NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `sexo` enum('Macho','Hembra') NOT NULL,
  `color` varchar(50) DEFAULT NULL,
  `edad_anios` int DEFAULT NULL,
  `edad_meses` int DEFAULT NULL,
  `esterilizado` tinyint(1) DEFAULT '0',
  `imagen` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_mascota`),
  KEY `id_raza` (`id_raza`),
  CONSTRAINT `Mascota_ibfk_1` FOREIGN KEY (`id_raza`) REFERENCES `Raza` (`id_raza`),
  CONSTRAINT `Mascota_chk_1` CHECK (((trim(`nombre`) <> _utf8mb4'') and (length(trim(`nombre`)) >= 2))),
  CONSTRAINT `Mascota_chk_2` CHECK (((`color` is null) or ((trim(`color`) <> _utf8mb4'') and (length(trim(`color`)) >= 3)))),
  CONSTRAINT `Mascota_chk_3` CHECK (((`edad_anios` is null) or ((`edad_anios` >= 0) and (`edad_anios` <= 25)))),
  CONSTRAINT `Mascota_chk_4` CHECK (((`edad_meses` is null) or ((`edad_meses` >= 0) and (`edad_meses` <= 11))))
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Mascota`
--

LOCK TABLES `Mascota` WRITE;
/*!40000 ALTER TABLE `Mascota` DISABLE KEYS */;
INSERT INTO `Mascota` VALUES (1,1,'Maxito','Macho','Dorado',3,6,1,NULL),(2,17,'Luna','Hembra','Gris',2,0,1,NULL),(3,3,'Rocky','Macho','Negro y Marrón',5,2,0,NULL),(4,16,'Mimi','Hembra','Blanco',1,8,0,NULL),(5,5,'Pipo','Macho','Café',4,0,1,NULL),(6,8,'Toby','Macho','Tricolor',2,6,0,NULL),(7,18,'Simba','Macho','Anaranjado',6,0,1,NULL),(8,10,'Bruno','Macho','Marrón',1,10,0,NULL),(9,20,'Kitty','Hembra','Negro',3,4,1,NULL),(10,2,'Bella','Hembra','Dorado Claro',4,8,1,NULL),(11,12,'Loki','Macho','Blanco y Negro',2,2,0,NULL),(12,15,'Pelusa','Hembra','Marrón y Blanco',7,0,1,NULL),(13,15,'Lucky','Macho','Negro',3,10,0,NULL),(14,15,'Rex','Macho','Negro',8,7,0,NULL),(16,15,'Susy','Hembra','Negro',3,5,1,NULL);
/*!40000 ALTER TABLE `Mascota` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Patologia`
--

DROP TABLE IF EXISTS `Patologia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Patologia` (
  `id_patologia` int NOT NULL AUTO_INCREMENT,
  `nombre_patologia` varchar(100) DEFAULT NULL,
  `especie_afecta` enum('Perro','Gato','Ambas') DEFAULT NULL,
  `gravedad` enum('Leve','Moderada','Grave','Critica') DEFAULT NULL,
  `es_crónica` tinyint(1) DEFAULT NULL,
  `es_contagiosa` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_patologia`),
  UNIQUE KEY `nombre_patologia` (`nombre_patologia`),
  UNIQUE KEY `nombre_patologia_2` (`nombre_patologia`),
  UNIQUE KEY `nombre_patologia_3` (`nombre_patologia`),
  CONSTRAINT `Patologia_chk_1` CHECK (((trim(`nombre_patologia`) <> _utf8mb4'') and (length(trim(`nombre_patologia`)) >= 3))),
  CONSTRAINT `Patologia_chk_2` CHECK (((`nombre_patologia` is null) or ((trim(`nombre_patologia`) <> _utf8mb4'') and (length(trim(`nombre_patologia`)) >= 3))))
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Patologia`
--

LOCK TABLES `Patologia` WRITE;
/*!40000 ALTER TABLE `Patologia` DISABLE KEYS */;
INSERT INTO `Patologia` VALUES (1,'Parvovirus Canino','Perro','Grave',0,1),(2,'Moquillo Canino','Perro','Grave',0,1),(3,'Leucemia Felina','Gato','Grave',1,1),(4,'Dermatitis Alérgica','Ambas','Moderada',0,0),(5,'Otitis Externa','Ambas','Leve',0,0),(6,'Gastroenteritis','Ambas','Moderada',0,0),(7,'Diabetes Mellitus','Ambas','Grave',1,0),(8,'Insuficiencia Renal','Ambas','Grave',1,0),(9,'Parasitosis Intestinal','Ambas','Leve',0,0),(10,'Fracturas Óseas','Ambas','Grave',0,0),(11,'Displasia de Cadera','Perro','Moderada',1,0),(12,'Hipertiroidismo','Gato','Moderada',1,0),(29,'Malaria','Ambas','Moderada',0,0),(30,'Bebalaria','Ambas','Moderada',0,0),(31,NULL,'Ambas','Moderada',0,0),(32,NULL,'Ambas','Moderada',0,0),(33,'Dolor De Cabeza','Ambas','Moderada',0,0);
/*!40000 ALTER TABLE `Patologia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Raza`
--

DROP TABLE IF EXISTS `Raza`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Raza` (
  `id_raza` int NOT NULL AUTO_INCREMENT,
  `nombre_raza` varchar(60) NOT NULL,
  PRIMARY KEY (`id_raza`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Raza`
--

LOCK TABLES `Raza` WRITE;
/*!40000 ALTER TABLE `Raza` DISABLE KEYS */;
INSERT INTO `Raza` VALUES (1,'Labrador Retriever'),(2,'Golden Retriever'),(3,'Pastor Alemán'),(4,'Bulldog Francés'),(5,'Chihuahua'),(6,'Poodle'),(7,'Rottweiler'),(8,'Beagle'),(9,'Yorkshire Terrier'),(10,'Boxer'),(11,'Husky Siberiano'),(12,'Border Collie'),(13,'Dálmata'),(14,'Cocker Spaniel'),(15,'Mestizo Perro'),(16,'Persa'),(17,'Siamés'),(18,'Maine Coon'),(19,'Británico de Pelo Corto'),(20,'Ragdoll'),(21,'Bengalí'),(22,'Sphynx'),(23,'Angora Turco'),(24,'Abisinio'),(25,'Mestizo Gato');
/*!40000 ALTER TABLE `Raza` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Recepcionista`
--

DROP TABLE IF EXISTS `Recepcionista`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Recepcionista` (
  `id_recepcionista` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido_paterno` varchar(50) NOT NULL,
  `apellido_materno` varchar(50) NOT NULL,
  `dni` char(8) NOT NULL,
  `telefono` char(9) NOT NULL,
  `email` varchar(100) NOT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  `turno` enum('Mañana','Tarde','Noche','Madrugada') DEFAULT NULL,
  `genero` char(1) NOT NULL,
  PRIMARY KEY (`id_recepcionista`),
  UNIQUE KEY `id_usuario` (`id_usuario`),
  UNIQUE KEY `dni` (`dni`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `Recepcionista_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `Recepcionista_chk_1` CHECK (((trim(`nombre`) <> _utf8mb4'') and (length(trim(`nombre`)) >= 2))),
  CONSTRAINT `Recepcionista_chk_2` CHECK (((trim(`apellido_paterno`) <> _utf8mb4'') and (length(trim(`apellido_paterno`)) >= 2))),
  CONSTRAINT `Recepcionista_chk_3` CHECK (((trim(`apellido_materno`) <> _utf8mb4'') and (length(trim(`apellido_materno`)) >= 2))),
  CONSTRAINT `Recepcionista_chk_4` CHECK (regexp_like(`dni`,_utf8mb4'^[0-9]{8}')),
  CONSTRAINT `Recepcionista_chk_5` CHECK (regexp_like(`telefono`,_utf8mb4'^9[0-9]{8}$')),
  CONSTRAINT `Recepcionista_chk_6` CHECK (regexp_like(`email`,_utf8mb4'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,}$')),
  CONSTRAINT `Recepcionista_chk_7` CHECK ((`genero` in (_utf8mb4'F',_utf8mb4'M')))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Recepcionista`
--

LOCK TABLES `Recepcionista` WRITE;
/*!40000 ALTER TABLE `Recepcionista` DISABLE KEYS */;
INSERT INTO `Recepcionista` VALUES (1,9,'María','Jiménez','Soto','11223344','987111222','maria.jimenez@veterinaria.com','2024-02-01','Mañana','F'),(2,10,'Ana','Vargas','Cruz','22334455','987222333','ana.vargas@veterinaria.com','2024-02-15','Tarde','F'),(3,11,'Carlos','Reyes','Flores','33445566','987333444','carlos.reyes@veterinaria.com','2024-03-01','Noche','M'),(4,12,'Lucía','Morales','Díaz','44556677','987444555','lucia.morales@veterinaria.com','2024-04-01','Mañana','F'),(7,20,'Susy','Diazaaaaa','Diaz','12345678','987654321','asdasd@gmail.com','2025-07-07','Noche','F'),(8,26,'Luisa','Diaz','Perez','34567890','976543212','luisa@gmail.com','2025-07-08','Mañana','F'),(9,27,'Roberto','Rodríguez','Mego','23456784','965432123','roberto@gmail.com','2025-07-08','Tarde','M');
/*!40000 ALTER TABLE `Recepcionista` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Resultado_servicio`
--

DROP TABLE IF EXISTS `Resultado_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Resultado_servicio` (
  `id_resultado` int NOT NULL AUTO_INCREMENT,
  `id_cita` int DEFAULT NULL,
  `id_veterinario` int DEFAULT NULL,
  `resultado` text,
  `interpretacion` text,
  `archivo_adjunto` varchar(100) DEFAULT NULL,
  `fecha_realizacion` datetime NOT NULL,
  PRIMARY KEY (`id_resultado`),
  KEY `id_cita` (`id_cita`),
  KEY `id_veterinario` (`id_veterinario`),
  CONSTRAINT `Resultado_servicio_ibfk_1` FOREIGN KEY (`id_cita`) REFERENCES `Cita` (`id_cita`),
  CONSTRAINT `Resultado_servicio_ibfk_2` FOREIGN KEY (`id_veterinario`) REFERENCES `Veterinario` (`id_veterinario`),
  CONSTRAINT `Resultado_servicio_chk_1` CHECK ((length(trim(`resultado`)) >= 5)),
  CONSTRAINT `Resultado_servicio_chk_2` CHECK (((`interpretacion` is null) or (length(trim(`interpretacion`)) >= 5))),
  CONSTRAINT `Resultado_servicio_chk_3` CHECK (((`archivo_adjunto` is null) or (length(trim(`archivo_adjunto`)) >= 5))),
  CONSTRAINT `Resultado_servicio_chk_4` CHECK ((length(trim(`resultado`)) >= 5))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Resultado_servicio`
--

LOCK TABLES `Resultado_servicio` WRITE;
/*!40000 ALTER TABLE `Resultado_servicio` DISABLE KEYS */;
INSERT INTO `Resultado_servicio` VALUES (1,1,4,'Desparasitación interna aplicada. No se observaron parásitos en heces.','Animal libre de parásitos intestinales.','Sesion 14 Base de Datos I.pdf','2025-07-09 00:00:00'),(2,2,2,'Hemograma: Leucocitos 8500/ul, Eritrocitos 6.2M/ul, Hemoglobina 14.5g/dl','Valores dentro de parámetros normales. No signos de infección.','hemograma_032025.pdf','2025-05-26 09:30:00'),(3,3,3,'Perfil bioquímico: ALT 45 U/L, AST 38 U/L, Creatinina 1.2 mg/dl','Función hepática y renal normales. Continuar tratamiento dermatológico.','bioquimico_042025.pdf','2025-05-29 10:45:00'),(4,4,4,'Radiografía: No se observan fracturas. Leve inflamación de tejidos blandos.','Esguince leve confirmado. Reposo por 10 días y antiinflamatorios.','rx_pata_052025.jpg','2025-05-31 00:00:00'),(5,13,1,'Resultadp','Interpretado',NULL,'2025-07-08 00:00:00'),(6,14,1,NULL,NULL,NULL,'2025-07-08 08:56:22'),(7,15,3,NULL,NULL,NULL,'2025-07-08 09:21:35'),(8,16,7,NULL,NULL,NULL,'2025-07-08 09:21:55'),(9,17,1,NULL,NULL,NULL,'2025-07-08 09:27:19');
/*!40000 ALTER TABLE `Resultado_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Servicio`
--

DROP TABLE IF EXISTS `Servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Servicio` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `id_tipo_servicio` int NOT NULL,
  `nombre_servicio` varchar(50) NOT NULL,
  `precio` decimal(6,2) NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_servicio`),
  KEY `id_tipo_servicio` (`id_tipo_servicio`),
  CONSTRAINT `Servicio_ibfk_1` FOREIGN KEY (`id_tipo_servicio`) REFERENCES `Tipo_servicio` (`id_tipo_servicio`),
  CONSTRAINT `Servicio_chk_1` CHECK (((trim(`nombre_servicio`) <> _utf8mb4'') and (length(trim(`nombre_servicio`)) >= 3))),
  CONSTRAINT `Servicio_chk_2` CHECK (((`precio` >= 0) and (`precio` <= 9999.99)))
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Servicio`
--

LOCK TABLES `Servicio` WRITE;
/*!40000 ALTER TABLE `Servicio` DISABLE KEYS */;
INSERT INTO `Servicio` VALUES (1,1,'Vacuna Séxtuple Canina',65.00,1),(2,1,'Vacuna Antirrábica',45.00,1),(3,1,'Vacuna Triple Felina',60.00,1),(4,1,'Vacuna Leucemia Felina',80.00,1),(5,1,'Desparasitación Interna',25.00,1),(6,1,'Desparasitación Externa',30.00,1),(7,1,'Desparasitación Completa',50.00,1),(8,1,'Control Preventivo General',40.00,1),(9,1,'Esterilización Canina',300.00,1),(10,1,'Esterilización Felina',250.00,1),(11,2,'Radiografía Simple',90.00,1),(12,2,'Radiografía con Contraste',150.00,1),(13,2,'Ecografía Abdominal',120.00,1),(14,2,'Ecografía Obstétrica',100.00,1),(15,2,'Radiografía Torácica',100.00,1),(16,2,'Ecografía Cardiaca',180.00,1),(17,3,'Hemograma Completo',85.00,1),(18,3,'Perfil Bioquímico',120.00,1),(19,3,'Examen de Orina',45.00,1),(20,3,'Coproscópico',35.00,1),(21,3,'Perfil Hepático',95.00,1),(22,3,'Perfil Renal',90.00,1),(23,3,'Perfil Tiroideo',110.00,1),(24,3,'Glucosa en Sangre',30.00,1),(25,3,'Examen Parasitológico',40.00,1),(26,3,'Cultivo Bacteriológico',80.00,1);
/*!40000 ALTER TABLE `Servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Servicio_Solicitado`
--

DROP TABLE IF EXISTS `Servicio_Solicitado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Servicio_Solicitado` (
  `id_servicio_solicitado` int NOT NULL AUTO_INCREMENT,
  `id_consulta` int DEFAULT NULL,
  `id_servicio` int DEFAULT NULL,
  `fecha_solicitado` datetime DEFAULT NULL,
  `prioridad` enum('Urgente','Normal','Programable') DEFAULT NULL,
  `estado_examen` enum('Solicitado','Citado','En proceso','Completado') DEFAULT 'Solicitado',
  `comentario_opcional` text,
  PRIMARY KEY (`id_servicio_solicitado`),
  KEY `id_consulta` (`id_consulta`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `Servicio_Solicitado_ibfk_1` FOREIGN KEY (`id_consulta`) REFERENCES `Consulta` (`id_consulta`),
  CONSTRAINT `Servicio_Solicitado_ibfk_2` FOREIGN KEY (`id_servicio`) REFERENCES `Servicio` (`id_servicio`),
  CONSTRAINT `Servicio_Solicitado_chk_1` CHECK (((`comentario_opcional` is null) or (length(trim(`comentario_opcional`)) >= 3)))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Servicio_Solicitado`
--

LOCK TABLES `Servicio_Solicitado` WRITE;
/*!40000 ALTER TABLE `Servicio_Solicitado` DISABLE KEYS */;
INSERT INTO `Servicio_Solicitado` VALUES (1,2,3,'2025-07-07 18:53:31','Urgente','Completado','Primera vacuna del cachorro'),(2,9,5,'2025-06-07 10:00:00','Normal','Completado','Desparasitación rutinaria'),(3,8,1,'2025-06-06 16:30:00','Normal','Solicitado','Primera vacuna del cachorro'),(4,3,17,'2025-05-25 14:30:00','Urgente','Completado','Para confirmar diagnóstico'),(5,4,18,'2025-05-28 11:30:00','Normal','Completado','Evaluar función hepática'),(6,7,21,'2025-06-05 09:00:00','Normal','Citado','Control geriátrico'),(7,5,11,'2025-05-30 21:00:00','Urgente','Completado','Descartar fractura'),(8,10,13,'2025-06-08 11:30:00','Normal','Citado','Control post-operatorio'),(9,1,2,'2025-07-08 08:17:44','Programable','Solicitado','nada'),(11,1,2,'2025-07-08 08:34:57','Programable','Solicitado','nada'),(12,1,2,'2025-07-08 08:56:21','Programable','Solicitado','nada'),(13,1,20,'2025-07-08 09:21:35','Normal','Solicitado',NULL),(14,4,20,'2025-07-08 09:21:55','Normal','Solicitado',NULL),(15,8,7,'2025-07-08 09:27:19','Normal','Solicitado',NULL);
/*!40000 ALTER TABLE `Servicio_Solicitado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Solicitud_atencion`
--

DROP TABLE IF EXISTS `Solicitud_atencion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Solicitud_atencion` (
  `id_solicitud` int NOT NULL AUTO_INCREMENT,
  `id_mascota` int DEFAULT NULL,
  `id_recepcionista` int DEFAULT NULL,
  `fecha_hora_solicitud` datetime DEFAULT NULL,
  `tipo_solicitud` enum('Consulta urgente','Consulta normal','Servicio programado') NOT NULL,
  `estado` enum('Pendiente','En atencion','Completada','Cancelada') DEFAULT 'Pendiente',
  PRIMARY KEY (`id_solicitud`),
  KEY `id_mascota` (`id_mascota`),
  KEY `id_recepcionista` (`id_recepcionista`),
  CONSTRAINT `Solicitud_atencion_ibfk_1` FOREIGN KEY (`id_mascota`) REFERENCES `Mascota` (`id_mascota`),
  CONSTRAINT `Solicitud_atencion_ibfk_2` FOREIGN KEY (`id_recepcionista`) REFERENCES `Recepcionista` (`id_recepcionista`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Solicitud_atencion`
--

LOCK TABLES `Solicitud_atencion` WRITE;
/*!40000 ALTER TABLE `Solicitud_atencion` DISABLE KEYS */;
INSERT INTO `Solicitud_atencion` VALUES (1,1,1,'2025-05-15 09:00:00','Consulta normal','Completada'),(2,2,1,'2025-05-20 10:30:00','Consulta normal','Completada'),(3,3,2,'2025-05-25 14:00:00','Consulta urgente','Completada'),(4,4,1,'2025-05-28 11:00:00','Servicio programado','Completada'),(5,5,3,'2025-05-30 20:30:00','Consulta urgente','Completada'),(6,6,2,'2025-06-03 15:30:00','Consulta normal','Completada'),(7,7,1,'2025-06-05 08:30:00','Consulta normal','Completada'),(8,8,2,'2025-06-06 16:00:00','Consulta normal','En atencion'),(9,9,4,'2025-06-07 09:30:00','Consulta normal','Completada'),(10,9,1,'2025-06-08 11:00:00','Servicio programado','Completada'),(11,11,1,'2025-06-08 14:00:00','Consulta urgente','Pendiente'),(16,14,2,'2025-07-07 12:40:18','Consulta normal','Pendiente'),(17,13,2,'2025-07-08 02:56:57','Consulta normal','Pendiente'),(18,16,1,'2025-07-08 05:00:50','Consulta normal','Pendiente');
/*!40000 ALTER TABLE `Solicitud_atencion` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `crear_triaje_y_consulta_automatico` AFTER INSERT ON `Solicitud_atencion` FOR EACH ROW BEGIN
    DECLARE veterinario_asignado INT;
    DECLARE triaje_id INT;
    DECLARE fecha_actual DATETIME;
    
    IF NEW.estado = 'Pendiente' THEN
        SET veterinario_asignado = asignar_veterinario_optimo();
        SET fecha_actual = (NOW() - INTERVAL 5 HOUR);
        IF veterinario_asignado IS NOT NULL THEN
            -- registro en Triaje
            INSERT INTO Triaje (
                id_solicitud,
                id_veterinario,
                fecha_hora_triaje,
                peso_mascota,
                latido_por_minuto,
                frecuencia_respiratoria_rpm,
                temperatura,
                frecuencia_pulso,
                clasificacion_urgencia
            ) VALUES (
                NEW.id_solicitud,
                veterinario_asignado,
                fecha_actual,  
                1.00, 
                60,
                30,
                38.5,
                60,
                'No urgente'
            );
            SET triaje_id = LAST_INSERT_ID();
            
            INSERT INTO Consulta (
                id_triaje,
                id_veterinario,
                tipo_consulta,
                fecha_consulta,
                condicion_general,
                es_seguimiento
            ) VALUES (
                triaje_id,
                veterinario_asignado,
                'Consulta general',
                fecha_actual, 
                'Regular',
                FALSE
            );
            
        END IF;
        
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `trigger_veterinario_disponibilidad` AFTER UPDATE ON `Solicitud_atencion` FOR EACH ROW BEGIN
    DECLARE vet_id INT DEFAULT NULL;
    DECLARE hora_peru INT;
    
    -- Buscar el veterinario asignado en el triaje
    SELECT t.id_veterinario INTO vet_id
    FROM Triaje t 
    WHERE t.id_solicitud = NEW.id_solicitud
    LIMIT 1;
    
    -- Solo actuar si encontramos veterinario
    IF vet_id IS NOT NULL THEN
        
        -- CASO 1: Cualquier estado → "En atencion"
        IF NEW.estado = 'En atencion' AND OLD.estado != 'En atencion' THEN
            UPDATE Veterinario 
            SET disposicion = 'Ocupado'
            WHERE id_veterinario = vet_id;
        END IF;
        
        -- CASO 2: "En atencion" → "Completada"
        IF NEW.estado = 'Completada' AND OLD.estado = 'En atencion' THEN
            -- Obtener hora de Perú
            SET hora_peru = HOUR((NOW() - INTERVAL 5 HOUR));
            IF hora_peru IS NULL THEN
                SET hora_peru = HOUR(NOW());
            END IF;
            
            -- Liberar veterinario según horario actual de Perú
            UPDATE Veterinario v
            SET disposicion = CASE 
                WHEN (v.turno = 'Mañana' AND hora_peru >= 7 AND hora_peru < 13) 
                     OR (v.turno = 'Tarde' AND hora_peru >= 13 AND hora_peru < 19)
                     OR (v.turno = 'Noche' AND hora_peru >= 19 AND hora_peru < 23)
                     OR (v.turno = 'Madrugada' AND (hora_peru >= 23 OR hora_peru < 7))
                THEN 'Libre'
                ELSE 'Fuera de turno'
            END
            WHERE id_veterinario = vet_id;
        END IF;
        
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `Tipo_animal`
--

DROP TABLE IF EXISTS `Tipo_animal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Tipo_animal` (
  `id_tipo_animal` int NOT NULL AUTO_INCREMENT,
  `id_raza` int NOT NULL,
  `descripcion` enum('Perro','Gato') NOT NULL,
  PRIMARY KEY (`id_tipo_animal`),
  KEY `id_raza` (`id_raza`),
  CONSTRAINT `Tipo_animal_ibfk_1` FOREIGN KEY (`id_raza`) REFERENCES `Raza` (`id_raza`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tipo_animal`
--

LOCK TABLES `Tipo_animal` WRITE;
/*!40000 ALTER TABLE `Tipo_animal` DISABLE KEYS */;
INSERT INTO `Tipo_animal` VALUES (1,1,'Perro'),(2,2,'Perro'),(3,3,'Perro'),(4,4,'Perro'),(5,5,'Perro'),(6,6,'Perro'),(7,7,'Perro'),(8,8,'Perro'),(9,9,'Perro'),(10,10,'Perro'),(11,11,'Perro'),(12,12,'Perro'),(13,13,'Perro'),(14,14,'Perro'),(15,15,'Perro'),(16,16,'Gato'),(17,17,'Gato'),(18,18,'Gato'),(19,19,'Gato'),(20,20,'Gato'),(21,21,'Gato'),(22,22,'Gato'),(23,23,'Gato'),(24,24,'Gato'),(25,25,'Gato');
/*!40000 ALTER TABLE `Tipo_animal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tipo_servicio`
--

DROP TABLE IF EXISTS `Tipo_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Tipo_servicio` (
  `id_tipo_servicio` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`id_tipo_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tipo_servicio`
--

LOCK TABLES `Tipo_servicio` WRITE;
/*!40000 ALTER TABLE `Tipo_servicio` DISABLE KEYS */;
INSERT INTO `Tipo_servicio` VALUES (1,'Medicina Preventiva'),(2,'Imágenes'),(3,'Laboratorio');
/*!40000 ALTER TABLE `Tipo_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tratamiento`
--

DROP TABLE IF EXISTS `Tratamiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Tratamiento` (
  `id_tratamiento` int NOT NULL AUTO_INCREMENT,
  `id_consulta` int DEFAULT NULL,
  `id_patologia` int DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `eficacia_tratamiento` enum('Muy buena','Buena','Regular','Mala') DEFAULT NULL,
  `tipo_tratamiento` enum('Medicamentoso','Quirurgico','Terapeutico','Preventivo') DEFAULT NULL,
  PRIMARY KEY (`id_tratamiento`),
  KEY `id_consulta` (`id_consulta`),
  KEY `id_patologia` (`id_patologia`),
  CONSTRAINT `Tratamiento_ibfk_1` FOREIGN KEY (`id_consulta`) REFERENCES `Consulta` (`id_consulta`),
  CONSTRAINT `Tratamiento_ibfk_2` FOREIGN KEY (`id_patologia`) REFERENCES `Patologia` (`id_patologia`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tratamiento`
--

LOCK TABLES `Tratamiento` WRITE;
/*!40000 ALTER TABLE `Tratamiento` DISABLE KEYS */;
INSERT INTO `Tratamiento` VALUES (1,3,6,'2025-05-25','Muy buena','Medicamentoso'),(2,4,4,'2025-05-28','Buena','Medicamentoso'),(3,5,10,'2025-05-30','Buena','Medicamentoso'),(4,7,11,'2025-06-05',NULL,'Terapeutico'),(17,4,29,'2025-07-08','Regular','Medicamentoso'),(18,4,30,'2025-07-08','Regular','Medicamentoso'),(19,5,31,'2025-07-08','Regular','Medicamentoso'),(20,2,32,'2025-07-08','Regular','Medicamentoso'),(21,2,33,'2025-07-08','Regular','Medicamentoso');
/*!40000 ALTER TABLE `Tratamiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Triaje`
--

DROP TABLE IF EXISTS `Triaje`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Triaje` (
  `id_triaje` int NOT NULL AUTO_INCREMENT,
  `id_solicitud` int NOT NULL,
  `id_veterinario` int NOT NULL,
  `fecha_hora_triaje` datetime NOT NULL,
  `peso_mascota` decimal(5,2) NOT NULL,
  `latido_por_minuto` int NOT NULL,
  `frecuencia_respiratoria_rpm` int NOT NULL,
  `temperatura` decimal(4,2) NOT NULL,
  `talla` decimal(5,2) DEFAULT NULL,
  `tiempo_capilar` varchar(50) DEFAULT NULL,
  `color_mucosas` varchar(50) DEFAULT NULL,
  `frecuencia_pulso` int NOT NULL,
  `porce_deshidratacion` decimal(4,2) DEFAULT NULL,
  `condicion_corporal` enum('Muy delgado','Delgado','Ideal','Sobrepeso','Obeso') DEFAULT 'Ideal',
  `clasificacion_urgencia` enum('No urgente','Poco urgente','Urgente','Muy urgente','Critico') NOT NULL,
  PRIMARY KEY (`id_triaje`),
  KEY `id_solicitud` (`id_solicitud`),
  KEY `id_veterinario` (`id_veterinario`),
  CONSTRAINT `Triaje_ibfk_1` FOREIGN KEY (`id_solicitud`) REFERENCES `Solicitud_atencion` (`id_solicitud`),
  CONSTRAINT `Triaje_ibfk_2` FOREIGN KEY (`id_veterinario`) REFERENCES `Veterinario` (`id_veterinario`),
  CONSTRAINT `Triaje_chk_1` CHECK (((`peso_mascota` > 0) and (`peso_mascota` <= 100))),
  CONSTRAINT `Triaje_chk_2` CHECK ((`latido_por_minuto` between 40 and 300)),
  CONSTRAINT `Triaje_chk_3` CHECK ((`frecuencia_respiratoria_rpm` between 10 and 150)),
  CONSTRAINT `Triaje_chk_4` CHECK ((`temperatura` between 35.0 and 42.0)),
  CONSTRAINT `Triaje_chk_5` CHECK (((`talla` is null) or ((`talla` > 0) and (`talla` <= 200)))),
  CONSTRAINT `Triaje_chk_6` CHECK (((`tiempo_capilar` is null) or (length(trim(`tiempo_capilar`)) >= 1))),
  CONSTRAINT `Triaje_chk_7` CHECK (((`color_mucosas` is null) or (length(trim(`color_mucosas`)) >= 3))),
  CONSTRAINT `Triaje_chk_8` CHECK ((`frecuencia_pulso` between 30 and 250)),
  CONSTRAINT `Triaje_chk_9` CHECK (((`porce_deshidratacion` >= 0) and (`porce_deshidratacion` <= 100)))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Triaje`
--

LOCK TABLES `Triaje` WRITE;
/*!40000 ALTER TABLE `Triaje` DISABLE KEYS */;
INSERT INTO `Triaje` VALUES (1,1,1,'2025-05-15 09:15:00',25.50,80,25,38.50,60.00,'2 segundos','Rosadas',85,0.00,'Ideal','No urgente'),(2,2,1,'2025-05-20 10:45:00',4.20,120,30,38.80,25.00,'2 segundos','Rosadas',125,0.00,'Ideal','No urgente'),(3,3,1,'2025-05-25 14:15:00',35.80,110,35,39.20,65.00,'3 segundos','Pálidas',115,5.00,'Sobrepeso','Urgente'),(4,4,1,'2025-05-28 11:15:00',3.80,140,28,38.60,22.00,'2 segundos','Rosadas',145,0.00,'Delgado','Urgente'),(5,5,1,'2025-05-30 20:45:00',6.50,95,22,38.90,30.00,'2 segundos','Rosadas',100,0.00,'Ideal','Poco urgente'),(6,6,2,'2025-06-03 15:45:00',18.20,90,26,38.70,45.00,'2 segundos','Rosadas',95,0.00,'Ideal','No urgente'),(7,7,1,'2025-06-05 08:45:00',42.30,85,24,38.60,70.00,'2 segundos','Rosadas',90,0.00,'Ideal','No urgente'),(8,8,1,'2025-06-06 16:15:00',1.80,150,35,38.90,18.00,'2 segundos','Rosadas',155,0.00,'Delgado','Poco urgente'),(9,9,1,'2025-06-07 09:45:00',4.80,130,32,38.40,28.00,'2 segundos','Rosadas',135,0.00,'Ideal','No urgente'),(10,10,1,'2025-06-08 11:15:00',28.50,88,26,38.70,55.00,'2 segundos','Rosadas',92,0.00,'Sobrepeso','No urgente'),(11,17,3,'2025-07-08 02:56:57',1.00,60,30,38.50,NULL,NULL,NULL,60,NULL,'Ideal','No urgente'),(12,18,3,'2025-07-08 05:00:50',1.00,60,30,38.50,NULL,NULL,NULL,60,NULL,'Ideal','No urgente');
/*!40000 ALTER TABLE `Triaje` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Veterinario`
--

DROP TABLE IF EXISTS `Veterinario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Veterinario` (
  `id_veterinario` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `id_especialidad` int NOT NULL,
  `codigo_CMVP` varchar(20) NOT NULL,
  `tipo_veterinario` enum('Medico General','Especializado') NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` char(1) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido_paterno` varchar(50) NOT NULL,
  `apellido_materno` varchar(50) NOT NULL,
  `dni` char(8) NOT NULL,
  `telefono` char(9) NOT NULL,
  `email` varchar(100) NOT NULL,
  `fecha_ingreso` date NOT NULL,
  `disposicion` enum('Ocupado','Libre','Fuera de turno') DEFAULT 'Libre',
  `turno` enum('Mañana','Tarde','Noche','Madrugada') NOT NULL,
  PRIMARY KEY (`id_veterinario`),
  UNIQUE KEY `id_usuario` (`id_usuario`),
  UNIQUE KEY `dni` (`dni`),
  UNIQUE KEY `email` (`email`),
  KEY `id_especialidad` (`id_especialidad`),
  CONSTRAINT `Veterinario_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `Veterinario_ibfk_2` FOREIGN KEY (`id_especialidad`) REFERENCES `Especialidad` (`id_especialidad`),
  CONSTRAINT `Veterinario_chk_1` CHECK (((trim(`codigo_CMVP`) <> _utf8mb4'') and (length(trim(`codigo_CMVP`)) >= 6))),
  CONSTRAINT `Veterinario_chk_2` CHECK ((`genero` in (_utf8mb4'F',_utf8mb4'M'))),
  CONSTRAINT `Veterinario_chk_3` CHECK (((trim(`nombre`) <> _utf8mb4'') and (length(trim(`nombre`)) >= 2))),
  CONSTRAINT `Veterinario_chk_4` CHECK (((trim(`apellido_paterno`) <> _utf8mb4'') and (length(trim(`apellido_paterno`)) >= 2))),
  CONSTRAINT `Veterinario_chk_5` CHECK (((trim(`apellido_materno`) <> _utf8mb4'') and (length(trim(`apellido_materno`)) >= 2))),
  CONSTRAINT `Veterinario_chk_6` CHECK (regexp_like(`dni`,_utf8mb4'^[0-9]{8}')),
  CONSTRAINT `Veterinario_chk_7` CHECK (regexp_like(`telefono`,_utf8mb4'^9[0-9]{8}$')),
  CONSTRAINT `Veterinario_chk_8` CHECK (regexp_like(`email`,_utf8mb4'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,}$'))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Veterinario`
--

LOCK TABLES `Veterinario` WRITE;
/*!40000 ALTER TABLE `Veterinario` DISABLE KEYS */;
INSERT INTO `Veterinario` VALUES (1,3,1,'CMVP001234','Medico General','1985-03-15','M','Roberto','Rodríguez','Sánchez','45612378','987123789','roberto.rodriguez@veterinaria.com','2024-01-20','Ocupado','Tarde'),(2,4,2,'CMVP005678','Especializado','1982-07-22','F','Laura','García','Moreno','78945612','987456123','laura.garcia@veterinaria.com','2024-02-01','Ocupado','Tarde'),(3,5,3,'CMVP009876','Especializado','1988-11-10','M','Diego','López','Hernández','32165498','987789456','diego.lopez@veterinaria.com','2024-02-15','Ocupado','Mañana'),(4,6,1,'CMVP004321','Medico General','1990-05-08','F','Patricia','Martínez','Ruiz','65498732','987321654','patricia.martinez@veterinaria.com','2024-03-01','Fuera de turno','Noche'),(5,7,4,'CMVP007890','Especializado','1987-09-14','M','Andrés','Vásquez','Paredes','14785236','987147852','andres.vasquez@veterinaria.com','2024-03-15','Fuera de turno','Tarde'),(6,8,5,'CMVP002468','Especializado','1984-12-03','F','Carmen','Silva','Romero','96321478','987963214','carmen.silva@veterinaria.com','2024-04-01','Fuera de turno','Mañana'),(7,15,1,'CMVP001111','Medico General','2025-07-07','M','Martin','Tin','Tin','71426213','987123789','robz@veterinaria.com','2025-07-07','Fuera de turno','Tarde'),(8,22,1,'CMVP005676','Medico General','1999-01-12','M','Juan','Perez','Perez','23456789','987123789','juan@gmail.com','2025-07-07','Fuera de turno','Tarde'),(9,23,3,'CMVP001238','Especializado','1996-03-02','M','Pepe','Gonzalez','Gonzales','12345678','987123789','pepe@gmail.com','2025-07-08','Fuera de turno','Noche');
/*!40000 ALTER TABLE `Veterinario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `contraseña` varchar(60) NOT NULL,
  `tipo_usuario` enum('Veterinario','Recepcionista','Administrador') NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('Activo','Inactivo') DEFAULT 'Activo',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`),
  CONSTRAINT `usuarios_chk_1` CHECK ((length(`contraseña`) >= 3))
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin_carlos','Admin123!','Administrador','2025-06-09 03:31:22','Activo'),(2,'admin_ana','Admin456!','Administrador','2025-06-09 03:31:22','Activo'),(3,'vet_rodriguez','VetRod789!','Veterinario','2025-06-09 03:31:22','Activo'),(4,'vet_garcia','VetGar321!','Veterinario','2025-06-09 03:31:22','Activo'),(5,'vet_lopez','VetLop654!','Veterinario','2025-06-09 03:31:22','Activo'),(6,'vet_martinez','VetMar987!','Veterinario','2025-06-09 03:31:22','Activo'),(7,'vet_vasquez','VetVas456!','Veterinario','2025-06-09 03:31:22','Activo'),(8,'vet_silva','VetSil123!','Veterinario','2025-06-09 03:31:22','Activo'),(9,'recep_maria','RecMar123!','Recepcionista','2025-06-09 03:31:22','Activo'),(10,'recep_ana','RecAna456!','Recepcionista','2025-06-09 03:31:22','Activo'),(11,'recep_carlos','RecCar789!','Recepcionista','2025-06-09 03:31:22','Activo'),(12,'recep_lucia','RecLuc321!','Recepcionista','2025-06-09 03:31:22','Activo'),(15,'vet_r','contrasenaaaa','Veterinario','2025-07-07 04:19:01','Inactivo'),(19,'admin_davidcini','jklmn','Administrador','2025-07-07 04:59:29','Inactivo'),(20,'recep_susy','susy123','Recepcionista','2025-07-07 05:18:08','Inactivo'),(21,'admin_juan','abcdefafdwadadw','Administrador','2025-07-07 05:29:01','Activo'),(22,'vet_juan','juan123','Veterinario','2025-07-07 21:16:10','Activo'),(23,'vet_pepe','pepe123','Veterinario','2025-07-08 00:50:35','Activo'),(25,'admin_jose','jose123','Administrador','2025-07-08 06:47:15','Inactivo'),(26,'recep_luisa','luisa123','Recepcionista','2025-07-08 08:25:13','Inactivo'),(27,'recep_roberto','roberto123','Recepcionista','2025-07-08 09:43:19','Inactivo');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Movimiento_financiero`
--

DROP TABLE IF EXISTS `Movimiento_financiero`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Movimiento_financiero` (
  `id_movimiento`   int NOT NULL AUTO_INCREMENT,
  `tipo`            enum('Ingreso','Egreso') NOT NULL,
  `categoria`       enum('Servicio','Operativo','Nomina') NOT NULL,
  `monto`           decimal(10,2) NOT NULL,
  `concepto`        varchar(150) NOT NULL,
  `fecha_movimiento` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_cita`         int DEFAULT NULL,
  `id_administrador` int DEFAULT NULL,
  PRIMARY KEY (`id_movimiento`),
  CONSTRAINT `MF_ibfk_1` FOREIGN KEY (`id_cita`) REFERENCES `Cita` (`id_cita`),
  CONSTRAINT `MF_ibfk_2` FOREIGN KEY (`id_administrador`) REFERENCES `Administrador` (`id_administrador`),
  CONSTRAINT `MF_chk_1` CHECK (`monto` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'railway'
--
/*!50106 SET @save_time_zone= @@TIME_ZONE */ ;
/*!50106 DROP EVENT IF EXISTS `EventoActualizarTurnos` */;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`%`*/ /*!50106 EVENT `EventoActualizarTurnos` ON SCHEDULE EVERY 5 MINUTE STARTS '2025-07-08 01:18:24' ON COMPLETION NOT PRESERVE ENABLE DO CALL ActualizarTurnosVeterinarios() */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;

--
-- Dumping routines for database 'railway'
--
/*!50003 DROP FUNCTION IF EXISTS `asignar_veterinario_optimo` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` FUNCTION `asignar_veterinario_optimo`() RETURNS int
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE veterinario_id INT DEFAULT NULL;
    DECLARE hora_actual INT;
    DECLARE turno_actual VARCHAR(10);

    SET hora_actual = HOUR((NOW() - INTERVAL 5 HOUR));
    
    -- Hallamos el turno actual según la hora
    IF hora_actual >= 7 AND hora_actual < 13 THEN
        SET turno_actual = 'Mañana';
    ELSEIF hora_actual >= 13 AND hora_actual < 19 THEN
        SET turno_actual = 'Tarde';
    ELSEIF hora_actual >= 19 AND hora_actual < 23 THEN
        SET turno_actual = 'Noche';
    ELSE
        -- Franja 23:00-07:00: turno Madrugada (SC-026 / F7).
        SET turno_actual = 'Madrugada';
    END IF;
    
    -- Caso 1: Médicos GENERALES LIBRES en turno actual
    SELECT v.id_veterinario INTO veterinario_id
    FROM Veterinario v
    LEFT JOIN (
        SELECT 
            t.id_veterinario,
            COUNT(t.id_triaje) as triajes_pendientes
        FROM Triaje t
        WHERE t.id_triaje NOT IN (
            SELECT DISTINCT c.id_triaje 
            FROM Consulta c 
            WHERE c.id_triaje IS NOT NULL
        )
        GROUP BY t.id_veterinario
    ) tp ON v.id_veterinario = tp.id_veterinario
    WHERE v.tipo_veterinario = 'Medico General'
        AND v.turno = turno_actual
        AND v.disposicion = 'Libre'
    ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
    LIMIT 1;
    
    -- Caso 2: Médicos GENERALES OCUPADOS en turno actual
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT 
                t.id_veterinario,
                COUNT(t.id_triaje) as triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (
                SELECT DISTINCT c.id_triaje 
                FROM Consulta c 
                WHERE c.id_triaje IS NOT NULL
            )
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Medico General'
            AND v.turno = turno_actual
            AND v.disposicion = 'Ocupado'
        ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;
    
    -- Caso 3: ESPECIALISTAS LIBRES en turno actual 
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT 
                t.id_veterinario,
                COUNT(t.id_triaje) as triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (
                SELECT DISTINCT c.id_triaje 
                FROM Consulta c 
                WHERE c.id_triaje IS NOT NULL
            )
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Especializado'
            AND v.turno = turno_actual
            AND v.disposicion = 'Libre'
        ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;
    
    -- Caso 4: ESPECIALISTAS OCUPADOS en turno actual 
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT 
                t.id_veterinario,
                COUNT(t.id_triaje) as triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (
                SELECT DISTINCT c.id_triaje 
                FROM Consulta c 
                WHERE c.id_triaje IS NOT NULL
            )
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Especializado'
            AND v.turno = turno_actual
            AND v.disposicion = 'Ocupado'
        ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;
    
    -- Caso 5: ESPECIALISTAS FUERA DE TURNO (último recurso absoluto)
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT 
                t.id_veterinario,
                COUNT(t.id_triaje) as triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (
                SELECT DISTINCT c.id_triaje 
                FROM Consulta c 
                WHERE c.id_triaje IS NOT NULL
            )
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Especializado'
            AND v.disposicion = 'Fuera de turno'
        ORDER BY 
            CASE 
                WHEN v.turno = turno_actual THEN 1
                ELSE 2
            END,
            COALESCE(tp.triajes_pendientes, 0) ASC,
            v.id_veterinario ASC
        LIMIT 1;
    END IF;

    -- Caso 6: ULTIMO RECURSO ABSOLUTO - cualquier veterinario existente.
    -- Garantiza que toda solicitud reciba un triaje y sea visible para algun
    -- veterinario, aunque ningun caso anterior calce (p. ej. solo hay Medicos
    -- Generales fuera de turno). Prioriza: turno actual, luego Libre/Ocupado,
    -- luego Medico General, y finalmente menor carga de triajes pendientes.
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT
                t.id_veterinario,
                COUNT(t.id_triaje) as triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (
                SELECT DISTINCT c.id_triaje
                FROM Consulta c
                WHERE c.id_triaje IS NOT NULL
            )
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        ORDER BY
            CASE WHEN v.turno = turno_actual THEN 0 ELSE 1 END,
            CASE v.disposicion WHEN 'Libre' THEN 0 WHEN 'Ocupado' THEN 1 ELSE 2 END,
            CASE WHEN v.tipo_veterinario = 'Medico General' THEN 0 ELSE 1 END,
            COALESCE(tp.triajes_pendientes, 0) ASC,
            v.id_veterinario ASC
        LIMIT 1;
    END IF;

    RETURN veterinario_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `ActualizarTurnosVeterinarios` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`%` PROCEDURE `ActualizarTurnosVeterinarios`()
BEGIN
    DECLARE hora_actual INT;
    DECLARE minuto_actual INT;
    DECLARE hora_total DECIMAL(4,2);
    
    -- Asegurar que usamos hora de Perú
    SET hora_actual = HOUR((NOW() - INTERVAL 5 HOUR));
    SET minuto_actual = MINUTE((NOW() - INTERVAL 5 HOUR));
    SET hora_total = hora_actual + (minuto_actual / 60);
    
    -- Si no funciona CONVERT_TZ, usar hora local ajustada
    IF hora_actual IS NULL THEN
        SET hora_actual = HOUR(NOW());
        SET minuto_actual = MINUTE(NOW());
        SET hora_total = hora_actual + (minuto_actual / 60);
    END IF;
    
    -- Cambiar a "Fuera de turno" veterinarios que están "Libre" pero fuera de horario
    UPDATE Veterinario 
    SET disposicion = 'Fuera de turno'
    WHERE disposicion = 'Libre'
    AND (
        (turno = 'Mañana' AND (hora_total < 7 OR hora_total >= 13))
        OR (turno = 'Tarde' AND (hora_total < 13 OR hora_total >= 19))
        OR (turno = 'Noche' AND (hora_total < 19 OR hora_total >= 23))
        OR (turno = 'Madrugada' AND (hora_total >= 7 AND hora_total < 23))
    );
    
    -- Cambiar a "Libre" veterinarios que están "Fuera de turno" pero ya en horario
    UPDATE Veterinario 
    SET disposicion = 'Libre'
    WHERE disposicion = 'Fuera de turno'
    AND (
        (turno = 'Mañana' AND hora_total >= 7 AND hora_total < 13)
        OR (turno = 'Tarde' AND hora_total >= 13 AND hora_total < 19)
        OR (turno = 'Noche' AND hora_total >= 19 AND hora_total < 23)
        OR (turno = 'Madrugada' AND (hora_total >= 23 OR hora_total < 7))
    );
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-08  6:23:10