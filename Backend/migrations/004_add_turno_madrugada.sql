-- Migración: agregar el turno 'Madrugada' (23:00-07:00) al enum `turno`
-- para cubrir la franja nocturna que antes quedaba sin turno activo (SC-026 / F7).
-- Ejecutar contra veterinaria_db.

ALTER TABLE `Veterinario`
  MODIFY COLUMN `turno` enum('Mañana','Tarde','Noche','Madrugada') NOT NULL;

ALTER TABLE `Recepcionista`
  MODIFY COLUMN `turno` enum('Mañana','Tarde','Noche','Madrugada') DEFAULT NULL;
