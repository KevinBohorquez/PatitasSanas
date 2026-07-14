-- SC-068: cronograma de recepcionistas (espejo del de veterinarios).
-- Horario_recepcionista: horario recurrente semanal. Horario_excepcion_recep: excepciones por fecha.
-- Ejecutar contra veterinaria_db. Cada CREATE es una sentencia independiente.

CREATE TABLE IF NOT EXISTS `Horario_recepcionista` (
  `id_horario` INT NOT NULL AUTO_INCREMENT,
  `id_recepcionista` INT NOT NULL,
  `dia_semana` ENUM('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo') NOT NULL,
  `turno` ENUM('Mañana','Tarde','Noche','Madrugada') NOT NULL,
  PRIMARY KEY (`id_horario`),
  UNIQUE KEY `uq_horario_recep_dia_turno` (`id_recepcionista`,`dia_semana`,`turno`),
  CONSTRAINT `fk_horario_recepcionista` FOREIGN KEY (`id_recepcionista`)
      REFERENCES `Recepcionista` (`id_recepcionista`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `Horario_excepcion_recep` (
  `id_excepcion` INT NOT NULL AUTO_INCREMENT,
  `id_recepcionista` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `turno` ENUM('Mañana','Tarde','Noche','Madrugada') DEFAULT NULL,
  `trabaja` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_excepcion`),
  UNIQUE KEY `uq_exc_recep_fecha` (`id_recepcionista`,`fecha`),
  CONSTRAINT `fk_excepcion_recepcionista` FOREIGN KEY (`id_recepcionista`)
      REFERENCES `Recepcionista` (`id_recepcionista`) ON DELETE CASCADE
);
