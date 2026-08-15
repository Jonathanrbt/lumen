# Escaneo de secretos previo al commit.
#
# El repo de Lumen es publico desde el primer commit y manejamos un token de
# Croma, una API key de Cursor y las llaves de Supabase. Un secreto que entra
# al historial no se borra con un commit de arreglo: hay que reescribir el
# historial o rotar la credencial. Por eso esto corre ANTES, no despues.
#
# Uso manual:  pwsh scripts/check-secrets.ps1
# Automatico:  se ejecuta desde .githooks/pre-commit

$ErrorActionPreference = "Stop"

$patrones = @(
    @{ nombre = "Token de Croma";            regex = "croma_live_[A-Za-z0-9]{8,}" },
    @{ nombre = "API key de Render";         regex = "rnd_[A-Za-z0-9]{16,}" },
    @{ nombre = "API key de Cursor";         regex = "key_[a-f0-9]{32,}" },
    @{ nombre = "Auth token de Twilio";      regex = "SK[a-f0-9]{32}" },
    @{ nombre = "Account SID de Twilio";     regex = "AC[a-f0-9]{32}" },
    @{ nombre = "JWT (Supabase anon/service)"; regex = "eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}" },
    @{ nombre = "Clave de servicio de Supabase"; regex = "sbp_[a-f0-9]{40,}" },
    @{ nombre = "API key de OpenAI/Anthropic"; regex = "sk-[A-Za-z0-9_-]{20,}" },
    @{ nombre = "Cadena de conexion Postgres con clave"; regex = "postgres(ql)?://[^:\s]+:[^@\s]+@" }
)

# Solo miramos lo que esta en el stage: lo que realmente va a entrar al commit.
$archivos = git diff --cached --name-only --diff-filter=ACM
if (-not $archivos) {
    Write-Host "check-secrets: no hay nada en el stage." -ForegroundColor DarkGray
    exit 0
}

$hallazgos = @()

foreach ($archivo in $archivos) {
    # .env.example es plantilla: lleva las llaves sin valores, a proposito.
    if ($archivo -eq ".env.example") { continue }
    if ($archivo -eq "scripts/check-secrets.ps1") { continue }
    if (-not (Test-Path $archivo)) { continue }

    $contenido = git show ":$archivo" 2>$null
    if (-not $contenido) { continue }

    foreach ($p in $patrones) {
        $m = [regex]::Matches($contenido, $p.regex)
        if ($m.Count -gt 0) {
            $hallazgos += "  $archivo  ->  $($p.nombre)"
        }
    }
}

if ($hallazgos.Count -gt 0) {
    Write-Host ""
    Write-Host "COMMIT BLOQUEADO: parece haber secretos en el stage." -ForegroundColor Red
    Write-Host ""
    $hallazgos | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "Sacalo del stage (git restore --staged <archivo>), muevelo a .env" -ForegroundColor Red
    Write-Host "y avisa en el chat del equipo. Si ya lo pusheaste: rota la credencial." -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "check-secrets: limpio." -ForegroundColor Green
exit 0
