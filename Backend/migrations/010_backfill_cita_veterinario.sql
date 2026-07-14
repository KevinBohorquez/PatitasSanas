-- SC-058 / F42: las citas legacy tienen id_veterinario NULL, por lo que en la
-- vista de recepción (Gestión de Citas) aparecen como "Sin asignar". El
-- veterinario sí es derivable de la consulta asociada a la cita:
--   cita -> servicio_solicitado -> consulta -> id_veterinario.
-- Se rellena el id_veterinario de las citas que lo tengan NULL a partir de esa
-- cadena. (SC-016 ya asigna el vet a las citas nuevas creadas desde la consulta.)
-- Las citas sin servicio/consulta asociada quedan sin vet (correcto). Idempotente.
-- Ejecutar contra veterinaria_db.
UPDATE `Cita` c
  JOIN `Servicio_Solicitado` ss ON ss.id_servicio_solicitado = c.id_servicio_solicitado
  JOIN `Consulta` co ON co.id_consulta = ss.id_consulta
   SET c.id_veterinario = co.id_veterinario
 WHERE c.id_veterinario IS NULL
   AND co.id_veterinario IS NOT NULL;
