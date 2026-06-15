# Análisis de Calidad con SonarQube — PatitasSanas

## Requisitos previos

Instalar lo siguiente antes de correr el análisis por primera vez:

| Herramienta | Versión mínima | Descarga |
|---|---|---|
| Docker Desktop | cualquiera reciente | https://www.docker.com/products/docker-desktop |
| sonar-scanner CLI | 5.x | https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/ |
| Python | 3.11 | ya instalado si levantaste el backend |
| Node / npm | 18+ | ya instalado si levantaste el frontend |

> **sonar-scanner** debe estar en el PATH del sistema. Verificar con `sonar-scanner --version` en la terminal.

El entorno virtual de Python (`Backend/venv`) debe estar activado antes de correr el script.

---

## Cómo correr el análisis

### 1. Obtener el token de SonarQube (solo la primera vez)

1. Levantar SonarQube: `docker compose -f docker-compose.sonar.yml up -d`
2. Abrir `http://localhost:9000` y entrar con `admin` / `admin`
3. Ir a **My Account > Security > Generate Token**
4. Copiar el token generado (empieza con `sqp_...`)

### 2. Ejecutar el script

```powershell
# Activar el venv del backend primero
cd Backend
.\.venv\Scripts\Activate.ps1   # o .\venv\Scripts\Activate.ps1 según cómo lo tengas
cd ..

# Correr el análisis completo
.\run-analysis.ps1
# El script pedirá el token si no se pasa como parámetro

# O pasándolo directo:
.\run-analysis.ps1 -Token sqp_xxxxxxxxxxxxxxxx
```

El script hace todo solo:
1. Levanta SonarQube con Docker
2. Configura el Quality Gate del proyecto automáticamente
3. Corre los tests del backend con cobertura (`pytest`)
4. Corre los tests del frontend con cobertura (`vitest`)
5. Sube todo al servidor con `sonar-scanner`

Demora aproximadamente **2–4 minutos** la primera vez.

### 3. Ver los resultados

Abrir en el navegador:

```
http://localhost:9000/dashboard?id=patitassanas
```

---

## Quality Gate — Umbrales del proyecto

El script configura automáticamente el gate **"PatitasSanas Gate"** con estos umbrales:

| Métrica | Condición | Justificación |
|---|---|---|
| Bugs | ≤ 15 | Permite margen razonable para un sprint |
| Vulnerabilidades | ≤ 5 | Solo bloquea si hay algo realmente grave |
| Cobertura de tests | ≥ 30% | Realista dado el tiempo disponible |
| Duplicación de código | ≤ 20% | Los code smells menores no bloquean |

**Verde (Passed):** el código cumple los umbrales, listo para entregar.  
**Rojo (Failed):** alguna métrica los supera, revisar qué falló en el dashboard.

> Los code smells aparecen en el dashboard pero **no bloquean** el Quality Gate. Son informativos.

---

## Cuándo correr el análisis

- **Al final de cada sprint**, cuando el código esté integrado en la rama `develop`.
- Opcionalmente a mitad del sprint para detectar problemas temprano.
- No es necesario correrlo en cada commit; con una vez por sprint es suficiente.

---

## Apagar SonarQube cuando no se use

```powershell
docker compose -f docker-compose.sonar.yml down
```

Los datos quedan guardados en volúmenes de Docker, así que el historial no se pierde.
