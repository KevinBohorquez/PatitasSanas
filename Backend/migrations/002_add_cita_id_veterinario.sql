-- Migración: columna id_veterinario en tabla Cita (SC-016 / F4)
-- Permite asignar explícitamente un veterinario a la cita creada por el
-- recepcionista y listar las "Citas programadas" del veterinario por
-- Cita.id_veterinario, en lugar de depender de Resultado_servicio (que sólo
-- existía para citas del flujo del veterinario). Idempotente-friendly: ejecutar
-- contra veterinaria_db sólo si la columna aún no existe.

ALTER TABLE `Cita`
  ADD COLUMN `id_veterinario` int DEFAULT NULL,
  ADD CONSTRAINT `fk_cita_veterinario`
      FOREIGN KEY (`id_veterinario`) REFERENCES `Veterinario` (`id_veterinario`);
