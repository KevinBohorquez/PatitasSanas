# Métricas de SonarQube — Guía para el equipo

## Las tres categorías principales

Desde siempre, SonarQube organiza los problemas del código en tres categorías. En versiones anteriores (< 10) se llamaban directamente **Bugs**, **Vulnerabilidades** y **Code Smells**. En SonarQube 10+ se agrupan bajo **Reliability**, **Security** y **Maintainability**, pero el concepto es idéntico.

---

### Reliability (antes: Bugs)

Problemas que hacen que el código se comporte de manera incorrecta o inesperada en tiempo de ejecución.

**Ejemplos típicos:**
- Usar una variable antes de inicializarla
- Dividir sin verificar que el divisor no sea cero
- Comparar objetos con `==` en vez de `.equals()` (en Java)
- Código que nunca se ejecuta (unreachable code)

**¿Por qué importa?** Un bug detectado aquí es un fallo potencial en producción. No es un "podría mejorar", es algo que probablemente rompa el sistema.

**Calificación A–E:**
| Grado | Significado |
|-------|-------------|
| A | 0 bugs |
| B | Al menos 1 bug menor |
| C | Al menos 1 bug mayor |
| D | Al menos 1 bug crítico  |
| E | Al menos 1 bug bloqueante |

---

### Security (antes: Vulnerabilidades)

Problemas que podrían ser explotados por un atacante para comprometer el sistema.

**Ejemplos típicos:**
- Contraseñas o tokens hardcodeados en el código
- Consultas SQL construidas con concatenación de strings (SQL injection)
- No validar la entrada del usuario antes de usarla
- Exponer stack traces en respuestas de error

**¿Por qué importa?** Una vulnerabilidad puede comprometer datos de usuarios o dar acceso no autorizado al sistema.

> **Security Hotspots** es una subcategoría aparte: son fragmentos que *podrían* ser un riesgo pero necesitan revisión manual para confirmar si realmente lo son. No cuentan como vulnerabilidades hasta que un humano las clasifica.

**Calificación A–E:** igual que Reliability, basada en severidad.

---

### Maintainability (antes: Code Smells)

Problemas que no rompen el código pero lo hacen difícil de entender, modificar o extender.

**Ejemplos típicos:**
- Funciones demasiado largas o con demasiados parámetros
- Código duplicado
- Variables con nombres sin sentido
- Comentarios que no aportan nada
- Campos opcionales en Pydantic sin valor por defecto

**¿Por qué importa?** No falla hoy, pero hace que agregar funcionalidad o corregir bugs sea más lento y propenso a errores. La deuda técnica se acumula.

> El número de code smells suele ser alto (el Sprint 4 arrojó 987). Eso es normal; son informativos y **no bloquean el Quality Gate** en la configuración del proyecto.

**Calificación A–E:** basada en el porcentaje de deuda técnica respecto al tamaño del proyecto.

---

## Otras métricas que aparecen en el dashboard

### Coverage (Cobertura de tests)

Porcentaje de líneas de código que los tests automatizados realmente ejecutan.

- **Line Coverage:** % de líneas ejecutadas por al menos un test
- **Lines to Cover:** total de líneas que podrían cubrirse
- **Uncovered Lines:** líneas que ningún test toca

**¿Por qué importa?** Un coverage bajo significa que podemos romper el código sin que ningún test lo detecte. El umbral del proyecto es **≥ 30%** — bajo pero realista para el tiempo disponible.

> **Nota Sprint 4:** el coverage salió 0.0% porque `pytest-cov` no estaba instalado en el venv al correr el análisis. No significa que no haya tests — significa que no se generó el reporte de cobertura.

---

### Duplications (Duplicación de código)

Porcentaje de bloques de código que aparecen repetidos en más de un lugar.

- **Density:** % de líneas duplicadas respecto al total
- **Duplicated Blocks:** número de bloques repetidos
- **Duplicated Files:** archivos que contienen duplicaciones

**¿Por qué importa?** El código duplicado es un multiplicador de bugs: si hay un error en un bloque y está copiado en 5 lugares, hay que corregirlo en los 5. El umbral del proyecto es **≤ 20%**.

---

## Cómo se decide si el proyecto "pasa" o "falla": el Quality Gate

El **Quality Gate** es un conjunto de umbrales que el equipo define. Si todas las métricas están dentro del rango, el resultado es **Passed**; si alguna lo supera, es **Failed**.

### Quality Gate "PatitasSanas Gate"

| Métrica | Condición | Justificación |
|---------|-----------|---------------|
| Bugs | ≤ 15 | Margen razonable para un sprint universitario |
| Vulnerabilidades | ≤ 5 | Solo bloquea si hay algo realmente grave |
| Cobertura | ≥ 30% | Realista con el tiempo disponible |
| Duplicación | ≤ 20% | Los code smells menores no bloquean |

> Los **code smells** (Maintainability) **no tienen umbral en nuestro gate** — aparecen en el dashboard como información pero no pueden bloquear la entrega.

---

## Métricas extra — no están en el Quality Gate pero vale la pena conocerlas

### Technical Debt (Deuda técnica)

Estimación del tiempo que tomaría corregir todos los code smells del proyecto. SonarQube lo calcula sumando el esfuerzo de cada issue de Maintainability.

**¿Por qué importa?** No bloquea nada, pero es un indicador de cuánto "trabajo pendiente invisible" hay acumulado. Si la deuda sube sprint a sprint sin que nadie la atienda, eventualmente ralentiza al equipo.

**Ejemplo:** el Sprint 4 mostró varios días de deuda técnica en el gráfico de riesgo — significa que si el equipo dedicara ese tiempo exclusivamente a limpiar el código, quedaría sin code smells.

---

### Complexity (Complejidad ciclomática)

Mide cuántos caminos de ejecución distintos tiene una función. Cada `if`, `for`, `while`, `except` suma +1 al contador.

**¿Por qué importa?** Una función con complejidad alta es más difícil de testear (necesita más casos de prueba para cubrirla) y más propensa a bugs. SonarQube marca como problemáticas las funciones que superan cierto umbral (normalmente 10–15).

**Ejemplo:** una función con 3 `if` anidados y un `for` tiene complejidad 5. Una función con 20 condiciones tiene complejidad 20 y debería dividirse.

---

### Security Hotspots

Fragmentos de código que *podrían* representar un riesgo de seguridad, pero que requieren revisión humana para confirmar si realmente lo son. Son distintos de las Vulnerabilidades.

**Diferencia clave:**
- **Vulnerabilidad** → SonarQube está seguro de que es un problema real
- **Security Hotspot** → SonarQube dice "revisa esto manualmente, puede o no ser un problema"

**Ejemplos típicos de hotspots:**
- Uso de funciones criptográficas (¿se está usando bien?)
- Lectura de variables de entorno (¿se valida el valor?)
- Peticiones HTTP salientes (¿se valida el certificado SSL?)

**¿Qué hacer con ellos?** Un humano debe revisarlos y marcarlos como "Safe" (no es riesgo) o "To Review / Acknowledged" (sí es riesgo, hay que corregir). El Sprint 4 mostró 5 hotspots con calificación E — conviene que alguien del equipo los revise en la web de SonarQube.

---

### Test Failures / Test Errors

- **Test Failures:** tests que se ejecutaron pero el resultado no fue el esperado (assertion falló)
- **Test Errors:** tests que no pudieron ejecutarse por un error de código (excepción no controlada)

**¿Por qué importa?** Si hay test failures, el coverage que reporta SonarQube puede ser engañoso — algunas líneas se "cubrieron" pero el comportamiento es incorrecto.

---

### Comment Density

Porcentaje de líneas del código que son comentarios. SonarQube no tiene un umbral fijo — solo lo reporta como dato.

**¿Por qué importa?** Un valor muy bajo puede indicar código difícil de entender; un valor muy alto puede indicar código que necesita demasiada explicación (señal de que el código en sí podría estar mal estructurado). En proyectos universitarios suele ser bajo y no es prioridad.

---

## Resumen rápido para recordar

```
Reliability  → ¿el código funciona correctamente?        (ex-Bugs)
Security     → ¿el código es seguro contra ataques?      (ex-Vulnerabilidades)
Maintainability → ¿el código es fácil de mantener?       (ex-Code Smells)
Coverage     → ¿los tests ejercitan suficiente código?
Duplications → ¿cuánto código está copiado y pegado?
Quality Gate → semáforo rojo/verde que resume todo lo anterior
```
