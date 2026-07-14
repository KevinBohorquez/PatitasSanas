-- SC-064: corrige el trigger `before_diagnostico_insert`.
--
-- Antes, en CADA inserción de diagnóstico, el trigger:
--   1) creaba una Patologia con nombre_patologia = NULL,
--   2) creaba un Tratamiento apuntando a esa patología NULL,
--   3) sobrescribía NEW.id_patologia con la patología NULL (descartando la real).
-- Eso es la CAUSA RAÍZ de las "patologías sin nombre" que la migración 006 solo
-- limpiaba a posteriori: el trigger las volvía a crear en cada diagnóstico.
--
-- Versión corregida: conserva la patología real del diagnóstico, crea el
-- tratamiento asociado con ESA patología, y setea la fecha si viene NULL.
--
-- IMPORTANTE: por el cuerpo BEGIN...END (con `;` internos), aplicar esta migración
-- con un cliente que envíe la sentencia completa (p. ej. pymysql en la consola del
-- contenedor, como la 009), NO en la consola web de Railway que parte por `;`.
-- Ejecutar contra veterinaria_db.

DROP TRIGGER IF EXISTS before_diagnostico_insert;

CREATE TRIGGER before_diagnostico_insert
BEFORE INSERT ON Diagnostico
FOR EACH ROW
BEGIN
    IF NEW.fecha_diagnostico IS NULL THEN
        SET NEW.fecha_diagnostico = NOW();
    END IF;

    INSERT INTO Tratamiento (id_consulta, id_patologia, fecha_inicio, eficacia_tratamiento, tipo_tratamiento)
    VALUES (NEW.id_consulta, NEW.id_patologia, CURDATE(), 'Regular', 'Medicamentoso');
END
