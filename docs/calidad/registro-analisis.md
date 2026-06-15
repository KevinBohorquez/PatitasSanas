# Registro de Análisis de Calidad — PatitasSanas

Cada vez que se corra el análisis SonarQube al cierre de un sprint, completar una fila en la tabla y adjuntar las capturas en `docs/calidad/evidencias/`.

---

## Historial de análisis

| Sprint | Fecha | Rama analizada | Ejecutó | Bugs | Vulnerabilidades | Cobertura | Duplicación | Quality Gate | Capturas |
|--------|-------|----------------|---------|------|------------------|-----------|-------------|--------------|----------|
| Sprint 1 | — | develop | — | — | — | — | — | — | — |
| Sprint 2 | — | develop | — | — | — | — | — | — | — |
| Sprint 3 | — | develop | — | — | — | — | — | — | — |
| Sprint 4 | 2026-06-15 | develop | Gerardo | 229 reliability issues (gate: pasó)¹ | 1 | 0.0%² | 4.0% | **PASSED** (con advertencias) | sprint4-dashboard.png, sprint4-issues.png, sprint4-metricas.png |

> Completar la columna **Capturas** con el nombre del archivo guardado, por ejemplo: `sprint1-dashboard.png`

**Notas Sprint 4:**
> ¹ SonarQube 10+ unifica bugs y otros issues bajo "Reliability issues". La métrica interna `bugs` que evalúa el Quality Gate es distinta del número visible en la UI (229). El gate pasó, lo que confirma que los bugs en sentido estricto están dentro del umbral ≤ 15.
> ² Cobertura 0.0% porque `pytest-cov` no estaba instalado en el venv al momento del análisis → no se generó `coverage.xml`. Ver nota en sección Cambios de umbrales.

---

## Cómo completar el registro

1. Correr el análisis siguiendo `docs/calidad/sonarqube-analisis.md`
2. Anotar los valores que muestra el dashboard en `http://localhost:9000/dashboard?id=patitassanas`
3. Tomar dos capturas:
   - Vista general del dashboard → `docs/calidad/evidencias/sprintN-dashboard.png`
   - Sección Quality Gate (passed/failed) → `docs/calidad/evidencias/sprintN-quality-gate.png`
4. Completar la fila correspondiente en la tabla de arriba
5. Hacer commit incluyendo este archivo y las capturas:
   ```
   chore: analisis sonarqube sprint N - quality gate PASSED/FAILED
   ```

---

## (Quality Gate "PatitasSanas Gate")

| Métrica | Umbral |
|---------|--------|
| Bugs | ≤ 15 |
| Vulnerabilidades | ≤ 5 |
| Cobertura de tests | ≥ 30% |
| Duplicación de código | ≤ 20% |

> Si se decide ajustar algún umbral durante el proyecto, registrar el cambio aquí con fecha y motivo.
