-- Migración: ampliar Resultado_servicio.archivo_adjunto para almacenar enlaces
-- (p. ej. de Google Drive), que superan los 100 caracteres (SC-020 / F27).
-- Ejecutar contra veterinaria_db.

ALTER TABLE `Resultado_servicio`
  MODIFY COLUMN `archivo_adjunto` varchar(500) DEFAULT NULL;
