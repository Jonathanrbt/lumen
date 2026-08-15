# Arranque del entorno de desarrollo de Lumen.
#
# Correlo una vez despues de clonar. Deja el entorno virtual, las dependencias,
# el .env y el hook anti-secretos listos, y te dice que falta.
#
#   pwsh scripts/setup-dev.ps1
#
# En Mac o Linux los pasos equivalentes estan en docs/PLAN.md.

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host ""
Write-Host "=== Lumen: preparando entorno ===" -ForegroundColor Cyan
Write-Host ""

# 1. Hook anti-secretos. Primero, porque el repo es publico.
git config core.hooksPath .githooks
Write-Host "[ok] Hook anti-secretos activado (.githooks)" -ForegroundColor Green

# 2. Entorno virtual
if (-not (Test-Path ".venv")) {
    Write-Host "[..] Creando entorno virtual..." -ForegroundColor DarkGray
    python -m venv .venv
}
Write-Host "[ok] Entorno virtual en .venv" -ForegroundColor Green

# 3. Dependencias
Write-Host "[..] Instalando dependencias (tarda un par de minutos)..." -ForegroundColor DarkGray
& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& .\.venv\Scripts\python.exe -m pip install -r api/requirements.txt --quiet
Write-Host "[ok] Dependencias instaladas" -ForegroundColor Green

# 4. Archivo de entorno
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "[!!] Se creo .env desde la plantilla. PEGA LOS VALORES del chat privado." -ForegroundColor Yellow
} else {
    Write-Host "[ok] Ya tienes .env" -ForegroundColor Green
}

# 5. Pruebas de humo
Write-Host "[..] Corriendo pruebas..." -ForegroundColor DarkGray
& .\.venv\Scripts\python.exe -m pytest -q

Write-Host ""
Write-Host "=== Listo ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Levanta la API:" -ForegroundColor White
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uvicorn lumen.main:app --reload --app-dir api"
Write-Host ""
Write-Host "Y comprueba estas dos, en este orden:" -ForegroundColor White
Write-Host "  http://127.0.0.1:8000/health         -> debe decir ok"
Write-Host "  http://127.0.0.1:8000/health/croma   -> llamada REAL a Croma; confirma tu token"
Write-Host "  http://127.0.0.1:8000/docs           -> los nueve endpoints del contrato"
Write-Host ""
Write-Host "Si /health/croma no esta en verde, no empieces a codear: revisa CROMA_API_KEY." -ForegroundColor Yellow
Write-Host ""
