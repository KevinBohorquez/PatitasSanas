# SRS — Requisitos del Sistema & Matriz de Trazabilidad

## Requerimientos Funcionales (RF)

| ID | Requerimiento |
|---|---|
| RF-001 | Registro, edición y consulta de clientes y sus mascotas |
| RF-002 | Recepcionista programa, cancela y completa citas |
| RF-003 | Alarma por correo 24h antes de la cita |
| RF-004 | Recordatorio por correo 4h antes de la cita |
| RF-005 | Recordatorios automáticos sin intervención manual |
| RF-006 | Gestión de historial clínico (consultas, diagnósticos, tratamientos) |
| RF-007 | Reportes básicos: citas del día e historial, exportación PDF |
| RF-008 | Inicio de sesión diferenciado por rol (Admin, Recep, Vet) |
| RF-009 | Citas solo a veterinarios activos |
| RF-010 | Exportación de dashboards y reportes estratégicos a PDF |
| RF-011 | Registro de triaje, consulta, diagnósticos y tratamientos por el vet |
| RF-012 | Endpoint de monitoreo `/api/v1/alarmas/status` |
| RF-013 | Dashboard analítico con gráfico de barras de servicios |
| RF-014 | Diagrama sectorial de especies de mascotas |
| RF-015 | Tarjetas KPI (ingresos estimados, tasa de asistencia) |
| RF-016 | Registro automático de ingreso al marcar cita como atendida |
| RF-017 | Registro manual de gastos operativos y nóminas |
| RF-018 | Balance financiero del período (ingresos vs gastos) |

## Requerimientos No Funcionales (RNF)

| ID | Requerimiento |
|---|---|
| RNF-001 | Interfaz clara y operable sin conocimientos técnicos |
| RNF-002 | Ejecutable en navegadores modernos sin instalación adicional |
| RNF-003 | Autenticación usuario/contraseña con control de roles |
| RNF-004 | Arquitectura Cliente-Servidor con API REST |
| RNF-005 | Tiempos de respuesta < 2 segundos |
| RNF-006 | Base de datos relacional MySQL |
| RNF-007 | Envío de correos asíncrono en segundo plano (scheduler) |
| RNF-008 | Credenciales de correo en variables de entorno |
| RNF-009 | Tolerancia a fallos de conectividad en notificaciones |

## Matriz de Trazabilidad de Requisitos

| ID | Prioridad | Artefactos Asociados (ECS) | Estado | Situación |
|---|---|---|---|---|
| RF-001 | Alta | SCI-BE-001, SCI-BE-009, SCI-FE-001, SCI-DB-001 | Activo | Entregado |
| RF-002 | Alta | SCI-BE-004, SCI-FE-002, SCI-DB-001 | Activo | Entregado |
| RF-003 | Media | SCI-BE-008, SCI-INF-002 | Activo | Entregado |
| RF-004 | Media | SCI-BE-008, SCI-INF-002 | Activo | Entregado |
| RF-005 | Media | SCI-BE-008 | Activo | Entregado |
| RF-006 | Alta | SCI-BE-001, SCI-BE-010, SCI-FE-009, SCI-DB-001 | Activo | Entregado |
| RF-007 | Media | SCI-BE-007, SCI-FE-005, SCI-FE-002 | Activo | Entregado |
| RF-008 | Alta | SCI-BE-005, SCI-FE-006, SCI-FE-011 | Activo | Entregado |
| RF-009 | Alta | SCI-BE-002, SCI-BE-004 | Activo | Entregado |
| RF-010 | Baja | SCI-BE-007, SCI-FE-012 | Activo | Entregado |
| RF-011 | Alta | SCI-BE-010, SCI-BE-011, SCI-FE-009 | Activo | Entregado |
| RF-012 | Baja | SCI-BE-013 | Activo | Entregado |
| RF-013 | Media | SCI-FE-012, SCI-BE-013 | Activo | Entregado |
| RF-014 | Media | SCI-FE-012, SCI-BE-012 | Activo | Entregado |
| RF-015 | Media | SCI-FE-012, SCI-BE-013 | Activo | Entregado |
| RF-016 | Alta | SCI-BE-004, SCI-BE-006, SCI-DB-001 | Activo | En espera |
| RF-017 | Alta | SCI-BE-006, SCI-DB-001 | Activo | En espera |
| RF-018 | Media | SCI-BE-013, SCI-FE-012 | Activo | En espera |
| RNF-001 | Alta | SCI-FE-001 al SCI-FE-012, SCI-FE-010 | Activo | Entregado |
| RNF-002 | Alta | SCI-FE-* (arquitectura frontend) | Activo | Entregado |
| RNF-003 | Alta | SCI-BE-005, SCI-FE-011 | Activo | Entregado |
| RNF-004 | Alta | SCI-BE-006 | Activo | Entregado |
| RNF-005 | Media | SCI-BE-006, SCI-INF-005 | Activo | Aceptado |
| RNF-006 | Alta | SCI-DB-001, SCI-DB-002 | Activo | Entregado |
| RNF-007 | Media | SCI-BE-008 | Activo | Entregado |
| RNF-008 | Alta | SCI-INF-001 | Activo | Entregado |
| RNF-009 | Media | SCI-BE-008 | Activo | Entregado |
