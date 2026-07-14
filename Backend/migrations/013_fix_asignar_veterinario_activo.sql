-- SC-065: la función asignar_veterinario_optimo() no consideraba si el veterinario
-- estaba Activo. El estado (Activo/Inactivo) vive en `usuarios`, y la función nunca
-- lo consultaba, por lo que podía asignar (vía el trigger crear_triaje_y_consulta_automatico)
-- un veterinario cuyo usuario está Inactivo.
--
-- Se recrea la función agregando a CADA consulta de la cascada el filtro de usuario
-- Activo. La lógica de preferencias (tipo de vet, turno, disposición y carga de triajes)
-- se mantiene igual. El último fallback también queda restringido a vets activos.
--
-- IMPORTANTE: por el cuerpo BEGIN...END, aplicar con un cliente que envíe la sentencia
-- completa (pymysql en la consola del contenedor, como la 009/012), NO en la consola web.
-- Ejecutar contra veterinaria_db.

DROP FUNCTION IF EXISTS asignar_veterinario_optimo;

CREATE FUNCTION asignar_veterinario_optimo() RETURNS int
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE veterinario_id INT DEFAULT NULL;
    DECLARE hora_actual INT;
    DECLARE turno_actual VARCHAR(10);

    SET hora_actual = HOUR(COALESCE(CONVERT_TZ(NOW(), 'UTC', 'America/Lima'), NOW()));

    IF hora_actual >= 7 AND hora_actual < 13 THEN
        SET turno_actual = 'Mañana';
    ELSEIF hora_actual >= 13 AND hora_actual < 19 THEN
        SET turno_actual = 'Tarde';
    ELSEIF hora_actual >= 19 AND hora_actual < 23 THEN
        SET turno_actual = 'Noche';
    ELSE
        SET turno_actual = 'Mañana';
    END IF;

    -- 1) Médico General, turno actual, Libre
    SELECT v.id_veterinario INTO veterinario_id
    FROM Veterinario v
    LEFT JOIN (
        SELECT t.id_veterinario, COUNT(t.id_triaje) AS triajes_pendientes
        FROM Triaje t
        WHERE t.id_triaje NOT IN (SELECT DISTINCT c.id_triaje FROM Consulta c WHERE c.id_triaje IS NOT NULL)
        GROUP BY t.id_veterinario
    ) tp ON v.id_veterinario = tp.id_veterinario
    WHERE v.tipo_veterinario = 'Medico General'
        AND v.turno = turno_actual
        AND v.disposicion = 'Libre'
        AND EXISTS (SELECT 1 FROM usuarios u WHERE u.id_usuario = v.id_usuario AND u.estado = 'Activo')
    ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
    LIMIT 1;

    -- 2) Médico General, turno actual, Ocupado
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT t.id_veterinario, COUNT(t.id_triaje) AS triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (SELECT DISTINCT c.id_triaje FROM Consulta c WHERE c.id_triaje IS NOT NULL)
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Medico General'
            AND v.turno = turno_actual
            AND v.disposicion = 'Ocupado'
            AND EXISTS (SELECT 1 FROM usuarios u WHERE u.id_usuario = v.id_usuario AND u.estado = 'Activo')
        ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;

    -- 3) Especializado, turno actual, Libre
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT t.id_veterinario, COUNT(t.id_triaje) AS triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (SELECT DISTINCT c.id_triaje FROM Consulta c WHERE c.id_triaje IS NOT NULL)
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Especializado'
            AND v.turno = turno_actual
            AND v.disposicion = 'Libre'
            AND EXISTS (SELECT 1 FROM usuarios u WHERE u.id_usuario = v.id_usuario AND u.estado = 'Activo')
        ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;

    -- 4) Especializado, turno actual, Ocupado
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT t.id_veterinario, COUNT(t.id_triaje) AS triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (SELECT DISTINCT c.id_triaje FROM Consulta c WHERE c.id_triaje IS NOT NULL)
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Especializado'
            AND v.turno = turno_actual
            AND v.disposicion = 'Ocupado'
            AND EXISTS (SELECT 1 FROM usuarios u WHERE u.id_usuario = v.id_usuario AND u.estado = 'Activo')
        ORDER BY COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;

    -- 5) Especializado, Fuera de turno (prefiere el turno actual)
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT t.id_veterinario, COUNT(t.id_triaje) AS triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (SELECT DISTINCT c.id_triaje FROM Consulta c WHERE c.id_triaje IS NOT NULL)
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE v.tipo_veterinario = 'Especializado'
            AND v.disposicion = 'Fuera de turno'
            AND EXISTS (SELECT 1 FROM usuarios u WHERE u.id_usuario = v.id_usuario AND u.estado = 'Activo')
        ORDER BY CASE WHEN v.turno = turno_actual THEN 1 ELSE 2 END,
                 COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;

    -- 6) Fallback general: cualquier veterinario ACTIVO, por preferencia
    IF veterinario_id IS NULL THEN
        SELECT v.id_veterinario INTO veterinario_id
        FROM Veterinario v
        LEFT JOIN (
            SELECT t.id_veterinario, COUNT(t.id_triaje) AS triajes_pendientes
            FROM Triaje t
            WHERE t.id_triaje NOT IN (SELECT DISTINCT c.id_triaje FROM Consulta c WHERE c.id_triaje IS NOT NULL)
            GROUP BY t.id_veterinario
        ) tp ON v.id_veterinario = tp.id_veterinario
        WHERE EXISTS (SELECT 1 FROM usuarios u WHERE u.id_usuario = v.id_usuario AND u.estado = 'Activo')
        ORDER BY CASE WHEN v.turno = turno_actual THEN 0 ELSE 1 END,
                 CASE v.disposicion WHEN 'Libre' THEN 0 WHEN 'Ocupado' THEN 1 ELSE 2 END,
                 CASE WHEN v.tipo_veterinario = 'Medico General' THEN 0 ELSE 1 END,
                 COALESCE(tp.triajes_pendientes, 0) ASC, v.id_veterinario ASC
        LIMIT 1;
    END IF;

    RETURN veterinario_id;
END
