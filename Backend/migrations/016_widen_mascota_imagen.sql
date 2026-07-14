-- SC-069: ensanchar Mascota.imagen para almacenar el enlace de la imagen (Google Drive),
-- que supera los 50 caracteres del VARCHAR original.
-- Ejecutar contra veterinaria_db.

ALTER TABLE `Mascota`
  MODIFY COLUMN `imagen` VARCHAR(500) DEFAULT NULL;
