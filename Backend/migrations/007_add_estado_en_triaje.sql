-- SC-052 / F37: el enum de estado de Solicitud_atencion en la BD nunca incluyó
-- 'En triaje', pero SC-018 (y el modelo solicitud_atencion.py) lo usan al guardar
-- el triaje. En MySQL con sql_mode estricto, el UPDATE ... SET estado='En triaje'
-- lanza DataError 1265 (Data truncated) y hace fallar el guardado del triaje (500).
-- Se agrega 'En triaje' al enum, alineándolo con el modelo. Idempotente.
-- Ejecutar contra veterinaria_db.
ALTER TABLE `Solicitud_atencion`
  MODIFY COLUMN `estado`
  ENUM('Pendiente','En triaje','En atencion','Completada','Cancelada')
  NULL DEFAULT 'Pendiente';
