# =====================================================================
# run-analysis.ps1 — Analisis SonarQube completo para PatitasSanas
#
# Requisitos previos:
#   - Docker Desktop en ejecucion
#   - sonar-scanner instalado (https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/)
#   - Python venv activo con dependencias instaladas (Backend/)
#   - Node + npm instalado (Frontend/)
#
# Uso:
#   .\run-analysis.ps1               <- usa token interactivo
#   .\run-analysis.ps1 -Token sqp_xxx
# =====================================================================

param(
    [string]$Token = ""
)

$ErrorActionPreference = "Stop"
$RootDir = $PSScriptRoot

function Write-Step($msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

function Write-Success($msg) {
    Write-Host "    [OK] $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "    [ERROR] $msg" -ForegroundColor Red
}

# ---- 0. Token ----
if (-not $Token) {
    $Token = Read-Host "Introduce el token de SonarQube (My Account > Security > Generate Token)"
}
if (-not $Token) {
    Write-Fail "Token vacio. Abortando."
    exit 1
}

# ---- 1. Levantar SonarQube ----
Write-Step "Levantando SonarQube con Docker..."
docker compose -f "$RootDir\docker-compose.sonar.yml" up -d

Write-Host "    Esperando a que SonarQube este listo (puede tardar ~60 s)..." -ForegroundColor Yellow
$maxWait = 120
$elapsed  = 0
$ready    = $false
while ($elapsed -lt $maxWait) {
    try {
        $status = (Invoke-RestMethod "http://localhost:9000/api/system/status" -TimeoutSec 3).status
        if ($status -eq "UP") { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 5
    $elapsed += 5
    Write-Host "    ... $elapsed s" -ForegroundColor DarkGray
}
if (-not $ready) {
    Write-Fail "SonarQube no respondio en $maxWait s. Revisa: docker compose -f docker-compose.sonar.yml logs"
    exit 1
}
Write-Success "SonarQube disponible en http://localhost:9000"

# ---- 2. Configurar Quality Gate (umbrales) ----
Write-Step "Configurando Quality Gate 'PatitasSanas Gate'..."
$sonarBase = "http://localhost:9000"
$adminCred  = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin"))
$authHeader = @{ Authorization = "Basic $adminCred" }

try {
    # Crear el Quality Gate (ignorar error si ya existe)
    $gateResp = Invoke-RestMethod "$sonarBase/api/qualitygates/create" `
        -Method Post -Headers $authHeader `
        -Body "name=PatitasSanas+Gate" `
        -ContentType "application/x-www-form-urlencoded" `
        -ErrorAction SilentlyContinue
    $gateId = $gateResp.id

    if (-not $gateId) {
        # Ya existe — obtener su id
        $gates   = Invoke-RestMethod "$sonarBase/api/qualitygates/list" -Headers $authHeader
        $gateId  = ($gates.qualitygates | Where-Object { $_.name -eq "PatitasSanas Gate" }).id
    }

    if ($gateId) {
        # Limpiar condiciones anteriores para no duplicar
        $existing = (Invoke-RestMethod "$sonarBase/api/qualitygates/show?id=$gateId" -Headers $authHeader).conditions
        foreach ($c in $existing) {
            Invoke-RestMethod "$sonarBase/api/qualitygates/delete_condition" `
                -Method Post -Headers $authHeader `
                -Body "id=$($c.id)" `
                -ContentType "application/x-www-form-urlencoded" | Out-Null
        }

        # Umbrales relajados para proyecto universitario
        $conditions = @(
            @{ metric="bugs";                     op="GT"; error="15" },  # <= 15 bugs
            @{ metric="vulnerabilities";           op="GT"; error="5"  },  # <= 5 vulnerabilidades
            @{ metric="coverage";                  op="LT"; error="30" },  # >= 30% cobertura
            @{ metric="duplicated_lines_density";  op="GT"; error="20" }   # <= 20% duplicacion
        )
        foreach ($c in $conditions) {
            Invoke-RestMethod "$sonarBase/api/qualitygates/create_condition" `
                -Method Post -Headers $authHeader `
                -Body "gateId=$gateId&metric=$($c.metric)&op=$($c.op)&error=$($c.error)" `
                -ContentType "application/x-www-form-urlencoded" | Out-Null
        }

        # Aplicar el gate al proyecto
        Invoke-RestMethod "$sonarBase/api/qualitygates/select" `
            -Method Post -Headers $authHeader `
            -Body "gateId=$gateId&projectKey=patitassanas" `
            -ContentType "application/x-www-form-urlencoded" | Out-Null

        Write-Success "Quality Gate aplicado al proyecto (umbrales relajados)"
    } else {
        Write-Host "    [WARN] No se pudo crear/encontrar el Quality Gate. Se usara el gate por defecto." -ForegroundColor Yellow
    }
} catch {
    Write-Host "    [WARN] Error configurando Quality Gate: $_" -ForegroundColor Yellow
}

# ---- 4. Cobertura Backend (pytest-cov) ----
Write-Step "Ejecutando tests Python con cobertura..."
Push-Location "$RootDir\Backend"
try {
    python -m pytest --cov=app --cov-report=xml:coverage.xml --cov-report=term-missing -q
    Write-Success "coverage.xml generado en Backend/"
} catch {
    Write-Host "    [WARN] Tests fallaron o no existen aun. Se continua sin cobertura Python." -ForegroundColor Yellow
} finally {
    Pop-Location
}

# ---- 5. Cobertura Frontend (vitest) ----
Write-Step "Ejecutando tests JavaScript con cobertura..."
Push-Location "$RootDir\Frontend"
try {
    npm run test:coverage
    Write-Success "lcov.info generado en Frontend/coverage/"
} catch {
    Write-Host "    [WARN] Tests fallaron o no existen aun. Se continua sin cobertura JS." -ForegroundColor Yellow
} finally {
    Pop-Location
}

# ---- 6. Ejecutar sonar-scanner ----
Write-Step "Ejecutando sonar-scanner..."
Push-Location $RootDir
try {
    sonar-scanner "-Dsonar.token=$Token"
    Write-Success "Analisis enviado a SonarQube"
} catch {
    Write-Fail "sonar-scanner no encontrado. Instalalo desde:"
    Write-Host "    https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/" -ForegroundColor Yellow
    Pop-Location
    exit 1
}
Pop-Location

# ---- 7. Resultado ----
Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  Analisis completado." -ForegroundColor Green
Write-Host "  Ver resultados en: http://localhost:9000/dashboard?id=patitassanas" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Green
