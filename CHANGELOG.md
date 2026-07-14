Markdown
# Changelog (Registro de Cambios)
Todos los cambios notables de este proyecto serán documentados en este archivo.

## [v1.4.0] - 2026-07-07
### Añadido (Added) — SC-013
- **SCI-FE-008** – Selector de veterinario disponible en el formulario de registro de citas (`CitasManagement`). - SC-006
  - Consume el endpoint existente `GET /api/v1/veterinarios/disponibles` al abrir el modal.
  - La selección de veterinario es opcional; si no se elige, la cita queda "Sin asignar".
  - El selector muestra nombre, tipo y turno de cada veterinario con disposición "Libre".
- **SCI-FE-008** – Columna "VETERINARIO" añadida a la tabla de citas con badge visual: - SC-006
  - Verde si hay veterinario asignado.
  - Gris itálico si la cita no tiene veterinario asignado.
- **SCI-FE-008** — Visualización de veterinario asignado en urgencias aleatorias — SC-013
  - Al completarse una asignación aleatoria, el sistema muestra un modal indicando
    el nombre del veterinario seleccionado.
  - Antes el sistema solo confirmaba la acción sin especificar a quién se asignó.

- **SCI-FE-008** — Mejora de experiencia de usuario en notificaciones — SC-012
  - Reemplazo de `window.alert()` por modales con mensajes descriptivos y amigables.
  - Aplicado en formularios de registro, eliminación y actualización de registros.

- **SCI-FE-008 / SCI-BE-004** — Corrección de defectos detectados en Sprints 1–4 — SC-011
  - Corrección de componentes del dashboard BI no montados en la UI
    (ServicesBarChart, SpeciesPieChart, KPIs).
  - Verificación y ajuste de endpoints afectados.

## [v.1.3.0] - 2026-06-15
### Añadido (Added)
- Integracion de insights clave en el dashboard del administrados.
- Integracion con SonarQube.
- Resultados de calidad.
- Fix de reportes.
- Unit Test para procesos clave del backend y frontend.

## [v.1.2.0] - 2026-06-09
### Añadido (Added)
- Integracion en el proyecto de sistema de alarmas y notificaciones con el uso de la libreria SendGrid.
- Cambio en el nombre del proyecto `Colitas Felices` a `Patitas Sanas`.

## [v1.1.0] - 2026-05-19
### Añadido (Added)
- Botón y funcionalidad para exportar el reporte de Citas Diarias en formato PDF (`appointments_pdf.py`).
- Funcionalidad para exportar el Historial Clínico de las mascotas en formato PDF (`medical_history_pdf.py`).
- Integración de la librería `reportlab` para la maquetación de documentos con la identidad visual de la clínica.

## [v1.0.0] - [2026-04-26]
### Añadido (Added)
- Base inicial del proyecto.
- Módulo de Administración (CRUD de usuarios y roles).
- Módulo de Recepción (Vistas de veterinarios, citas y dashboard inicial).
