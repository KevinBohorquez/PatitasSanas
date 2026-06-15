-- Migración: columnas de control de recordatorios por correo en tabla Cita
-- Requeridas por el modelo SQLAlchemy y el scheduler de alarmas.
-- Ejecutar contra la base de datos veterinaria_db si aún no existen.

ALTER TABLE `Cita`
  ADD COLUMN `recordatorio_24h_enviado` tinyint(1) NOT NULL DEFAULT 0,
  ADD COLUMN `recordatorio_4h_enviado` tinyint(1) NOT NULL DEFAULT 0;
