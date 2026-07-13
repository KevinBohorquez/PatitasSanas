-- SC-046 / F31: los hashes pbkdf2_sha256 (~87 caracteres) no caben en el
-- VARCHAR(60) original de usuarios.contraseña. Se ensancha la columna para
-- poder almacenar el hash. Ejecutar ANTES de 009_hash_passwords.py.
-- Ejecutar contra veterinaria_db.
ALTER TABLE `usuarios`
  MODIFY COLUMN `contraseña` VARCHAR(255) NOT NULL;
