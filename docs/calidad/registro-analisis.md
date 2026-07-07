# Registro de Análisis de Calidad — PatitasSanas

Cada vez que se corra el análisis SonarQube al cierre de un sprint, completar una fila en la tabla y adjuntar las capturas en `docs/calidad/evidencias/`.

---

## Historial de análisis

| Sprint | Fecha | Rama analizada | Ejecutó | Bugs | Vulnerabilidades | Cobertura | Duplicación | Deuda técnica | Quality Gate | Capturas |
|--------|-------|----------------|---------|------|------------------|-----------|-------------|---------------|--------------|----------|
| Sprint 1 | — | develop | — | — | — | — | — | — | — | — |
| Sprint 2 | — | develop | — | — | — | — | — | — | — | — |
| Sprint 3 | — | develop | — | — | — | — | — | — | — | — |
| Sprint 4 | 2026-06-15 | develop | Gerardo | 229 reliability issues (gate: pasó)¹ | 1 | 0.0%² | 4.0% | — | **PASSED** (con advertencias) | sprint4-dashboard.png, sprint4-issues.png, sprint4-metricas.png |
| Sprint 5 | 2026-07-07 | develop | Gerardo | 273 reliability issues³ | 1 | 0.0%⁴ | 0.4% | 11d (rating A) | **FAILED**⁵ | sprint5_dashboard.jpg, sprint5_issues.jpg, sprint5_measures.jpg, sprint5_measures_debt.jpg |

> Completar la columna **Capturas** con el nombre del archivo guardado, por ejemplo: `sprint1-dashboard.png`

**Notas Sprint 4:**
> ¹ SonarQube 10+ unifica bugs y otros issues bajo "Reliability issues". La métrica interna `bugs` que evalúa el Quality Gate es distinta del número visible en la UI (229). El gate pasó, lo que confirma que los bugs en sentido estricto están dentro del umbral ≤ 15.
> ² Cobertura 0.0% porque `pytest-cov` no estaba instalado en el venv al momento del análisis → no se generó `coverage.xml`. Ver nota en sección Cambios de umbrales.

**Notas Sprint 5:**
> ³ Reliability issues subió de 229 (Sprint 4) a 273. El total de issues del proyecto fue **1 167** (12d de esfuerzo estimado), repartidos en 273 de Reliability, 1 de Security y ~1,1k de Maintainability. Severidad: 1 Blocker, 297 High, 491 Medium, 529 Low, 2 Info.
> ⁴ La cobertura volvió a salir 0.0% (misma situación que el Sprint 4: no se generó el reporte de cobertura). **Confirmar** que `pytest-cov` / `vitest --coverage` estén generando `coverage.xml` y `lcov.info` antes del próximo análisis.
> ⁵ El Quality Gate salió **FAILED**, pero evaluado contra las condiciones por defecto de "Sonar way" sobre *New Code* (New issues = 0 requerido → 107 encontrados; Coverage ≥ 80% → 0.0%), **no** contra el "PatitasSanas Gate" del proyecto (Bugs ≤15, Vuln ≤5, Cobertura ≥30%, Duplicación ≤20%). Hay que verificar que el gate asignado al proyecto sea el custom (el `run-analysis.ps1` debería configurarlo automáticamente). Aun bajo el gate propio, la cobertura 0.0% incumpliría el umbral ≥30%, así que **la cobertura es el punto real a resolver**.
> Deuda técnica (Maintainability): 11d en Overall Code (rating A, ratio 0.6%); 7h 56min en New Code. Vulnerabilidad de Security: 1 issue (rating B, 30min de remediación).

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
