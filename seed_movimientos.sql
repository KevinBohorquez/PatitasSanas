-- Seed data for Movimiento_financiero (test data for Flujo de Caja)
-- Run AFTER importing VeterinariaDump.sql
-- Admin users available: admin_carlos / Admin123! , admin_ana / Admin456!

INSERT INTO Movimiento_financiero (tipo, categoria, monto, concepto, fecha_movimiento, id_cita, id_administrador) VALUES
('Ingreso', 'Servicio', 65.00, 'Vacuna Séxtuple Canina - Cita #1', '2025-06-07 14:00:00', 1, 1),
('Ingreso', 'Servicio', 120.00, 'Perfil Bioquímico - Cita #2', '2025-05-26 09:00:00', 2, 1),
('Ingreso', 'Servicio', 90.00, 'Radiografía Simple - Cita #4', '2025-05-31 08:00:00', 4, 1),
('Ingreso', 'Servicio', 25.00, 'Desparasitación Interna - Cita #1', '2025-06-07 14:00:00', 1, 2),
('Egreso', 'Operativo', 150.00, 'Compra de insumos médicos (jeringas, gasas)', '2025-06-01 10:00:00', NULL, 1),
('Egreso', 'Operativo', 85.50, 'Recarga de oxígeno medicinal', '2025-06-05 11:30:00', NULL, 1),
('Egreso', 'Nomina', 2500.00, 'Pago nómina veterinarios - Junio', '2025-06-30 16:00:00', NULL, 1),
('Egreso', 'Nomina', 1800.00, 'Pago nómina recepcionistas - Junio', '2025-06-30 16:00:00', NULL, 2),
('Egreso', 'Operativo', 320.00, 'Mantenimiento de equipos de rayos X', '2025-06-12 09:00:00', NULL, 1),
('Ingreso', 'Servicio', 45.00, 'Vacuna Antirrábica - Cita #5', '2025-06-09 16:00:00', 5, 2),
('Ingreso', 'Servicio', 40.00, 'Control Preventivo General - Cita #8', '2025-06-12 11:00:00', 8, 2),
('Egreso', 'Operativo', 90.00, 'Compra de medicamentos (antibióticos)', '2025-06-15 14:00:00', NULL, 1),
('Egreso', 'Nomina', 1200.00, 'Pago personal de limpieza - Junio', '2025-06-30 16:00:00', NULL, 1),
('Ingreso', 'Servicio', 300.00, 'Esterilización Canina - Cita #3', '2025-05-29 10:00:00', 3, 1),
('Egreso', 'Operativo', 210.00, 'Factura de electricidad - Junio', '2025-07-05 10:00:00', NULL, 2),
('Egreso', 'Operativo', 180.00, 'Factura de agua - Junio', '2025-07-05 10:00:00', NULL, 2),
('Ingreso', 'Servicio', 85.00, 'Hemograma Completo - Cita #6', '2025-06-03 16:00:00', 6, 1);
