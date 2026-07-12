-- Limpieza de datos legado (SC-029 / F10). Idempotente.
-- Ejecutar contra veterinaria_db.

-- Solicitudes 11 y 16: quedaron 'Pendiente' sin triaje (invisibles para todo
-- veterinario). Se marcan como 'Cancelada' para no quedar colgadas.
UPDATE `Solicitud_atencion`
   SET `estado` = 'Cancelada'
 WHERE `id_solicitud` IN (11, 16)
   AND `estado` = 'Pendiente';

-- Patologías 31 y 32 tenían nombre_patologia = NULL. Están referenciadas por
-- Diagnostico/Tratamiento (no se pueden borrar sin romper FK), así que se
-- completan con un nombre placeholder.
UPDATE `Patologia`
   SET `nombre_patologia` = CONCAT('Patología sin nombre ', `id_patologia`)
 WHERE `id_patologia` IN (31, 32)
   AND `nombre_patologia` IS NULL;
