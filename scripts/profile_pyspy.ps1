<#
.SYNOPSIS
  Профилирование приложения с помощью py-spy и генерация flamegraph (SVG).

.DESCRIPTION
  Скрипт может запустить `python run.py` в фоне, выполнить небольшую нагрузку на
  endpoint `/clients/`, затем записать профиль с помощью `py-spy` (attach по PID)
  и сохранить результат как `flame_YYYYMMDD_HHMMSS.svg` в текущей папке.

.PARAMETER Duration
  Длительность записи профиля в секундах (по умолчанию 15).

.PARAMETER Requests
  Количество HTTP-запросов для генерации нагрузки перед записью (по умолчанию 50).

.PARAMETER StartServer
  Если указан, скрипт запустит `python run.py` в фоне и будет профилировать этот процесс.

.PARAMETER Pid
  PID существующего Python-процесса для attach. Если не указан, скрипт попытается найти
  процесс с `run.py` в командной строке.

Примеры:
  # Запустить сервер, сделать нагрузку и записать 20 секунд
  .\profile_pyspy.ps1 -StartServer -Duration 20 -Requests 100

  # Присоединиться к уже запущенному процессу 12345 и записать 15 секунд
  .\profile_pyspy.ps1 -Pid 12345
#>

param(
    [int]$Duration = 15,
    [int]$Requests = 50,
    [switch]$StartServer,
    [int]$Pid
)

function Check-PySpy {
    try { 
        & py-spy --version > $null 2>&1
        return $true
    } catch {
        return $false
    }
}

if (-not (Check-PySpy)) {
    Write-Host 'py-spy not found in PATH. Install with: pip install py-spy or download a binary from https://github.com/benfred/py-spy/releases' -ForegroundColor Yellow
    exit 1
}

$started = $false
try {
    if ($StartServer) {
        $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $pythonCmd) { Write-Error "Исполняемый python не найден в PATH."; exit 1 }

        Write-Host "Запускаю сервер: python run.py ..."
        $proc = Start-Process -FilePath $pythonCmd -ArgumentList 'run.py' -PassThru
        $Pid = $proc.Id
        $started = $true
        Write-Host "Сервер запущен (PID=$Pid). Жду 2 сек для старта..."
        Start-Sleep -Seconds 2
    }

    if (-not $Pid) {
        # Попытка найти процесс с run.py в командной строке
        $candidates = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and ($_.CommandLine -match 'run.py' -or $_.CommandLine -match 'flask') }
        if ($candidates -and $candidates.Count -ge 1) {
            $Pid = $candidates[0].ProcessId
            Write-Host ('Found run.py process, PID=' + $Pid)
        } else {
            Write-Error 'Не найден процесс run.py. Укажите -Pid или используйте -StartServer.'; exit 1
        }
    }

    # Генерируем простую нагрузку
    $url = 'http://127.0.0.1:5000/clients/'
    Write-Host ("Generating $Requests requests to $url")
    for ($i = 0; $i -lt $Requests; $i++) {
        try { Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 5 > $null } catch { }
    }

    $stamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
    $out = "flame_$stamp.svg"
    Write-Host ("Recording profile for PID=$Pid for $Duration seconds -> $out")
    & py-spy record --pid $Pid --duration $Duration -o $out

    if (Test-Path $out) {
        Write-Host ('Done. File: ' + $out) -ForegroundColor Green
    } else {
        Write-Error 'py-spy did not create the output file. Check previous output for errors.'
    }

} finally {
    if ($started -and $Pid) {
        Write-Host ("Stopping started server PID=$Pid")
        try { Stop-Process -Id $Pid -Force } catch { }
    }
}
