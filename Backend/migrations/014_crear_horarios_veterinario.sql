-- SC-066: cronograma de veterinarios.
-- Horario_veterinario: horario recurrente semanal (día de la semana + turno).
-- Horario_excepcion: excepciones puntuales por fecha (día libre o turno extra/cambio).
-- Ejecutar contra veterinaria_db. Cada CREATE es una sentencia independiente.

CREATE TABLE IF NOT EXISTS `Horario_veterinario` (
  `id_horario` INT NOT NULL AUTO_INCREMENT,
  `id_veterinario` INT NOT NULL,
  `dia_semana` ENUM('Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo') NOT NULL,
  `turno` ENUM('Mañana','Tarde','Noche','Madrugada') NOT NULL,
  PRIMARY KEY (`id_horario`),
  UNIQUE KEY `uq_horario_vet_dia_turno` (`id_veterinario`,`dia_semana`,`turno`),
  CONSTRAINT `fk_horario_veterinario` FOREIGN KEY (`id_veterinario`)
      REFERENCES `Veterinario` (`id_veterinario`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `Horario_excepcion` (
  `id_excepcion` INT NOT NULL AUTO_INCREMENT,
  `id_veterinario` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `turno` ENUM('Mañana','Tarde','Noche','Madrugada') DEFAULT NULL,
  `trabaja` TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_excepcion`),
  UNIQUE KEY `uq_excepcion_vet_fecha` (`id_veterinario`,`fecha`),
  CONSTRAINT `fk_excepcion_veterinario` FOREIGN KEY (`id_veterinario`)
      REFERENCES `Veterinario` (`id_veterinario`) ON DELETE CASCADE
);
