-- SC-048 / F33: patologías con nombre_patologia NULL rompen la serialización de
-- GET /catalogos/patologias/ (nombre_patologia es NOT NULL en el modelo y el
-- schema de respuesta lo exige, así que un NULL en la lista devuelve 500).
--
-- La migración 005 (SC-029) sólo saneó las patologías 31 y 32 por id; quedaron
-- otras sin nombre (p. ej. id 34). Se generaliza el saneo a CUALQUIER patología
-- sin nombre, con el mismo criterio placeholder. Idempotente.
-- Ejecutar contra veterinaria_db.
UPDATE `Patologia`
   SET `nombre_patologia` = CONCAT('Patología sin nombre ', `id_patologia`)
 WHERE `nombre_patologia` IS NULL
    OR `nombre_patologia` = '';
