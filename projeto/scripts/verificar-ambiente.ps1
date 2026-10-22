. "$PSScriptRoot/comum.ps1"
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Start-Transcript -Path "resultados/logs/diagnostico-$stamp.txt"
try {
    $osInfo=Get-CimInstance Win32_OperatingSystem
    $cpuInfo=Get-CimInstance Win32_Processor
    $sysInfo=Get-CimInstance Win32_ComputerSystem
    $data=[ordered]@{Data=(Get-Date -Format o);OS=$osInfo.Caption;Versao=$osInfo.Version;Arquitetura=$osInfo.OSArchitecture;CPU=$cpuInfo.Name;CPUsLogicas=$sysInfo.NumberOfLogicalProcessors;RAM_GB=[math]::Round($sysInfo.TotalPhysicalMemory/1GB,2);Virtualizacao=$cpuInfo.VirtualizationFirmwareEnabled;Hypervisor=$sysInfo.HypervisorPresent;Admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator);Discos=@(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID,@{n='LivreGB';e={[math]::Round($_.FreeSpace/1GB,2)}});PATH=$env:PATH;DOCKER_HOST=$env:DOCKER_HOST;KUBECONFIG=$env:KUBECONFIG;Ferramentas=@()}
    foreach($tool in @('docker','kubectl','minikube','python','git','winget','wsl')) {
        $found=Get-Command $tool -ErrorAction SilentlyContinue
        $data.Ferramentas += [pscustomobject]@{Nome=$tool;Caminho=$found.Source}
    }
    $data | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath 'resultados/evidencias/diagnostico.json' -Encoding utf8
    foreach($check in @(@('docker','version'),@('docker','info'),@('kubectl','version','--client'),@('minikube','version'),@('python','--version'),@('git','--version'),@('winget','--version'),@('wsl','--status'),@('wsl','--list','--verbose'))) {
        try { Run $check[0] $check[1..($check.Count-1)] } catch { Write-Warning $_ }
    }
    $network=foreach($url in @('https://download.docker.com','https://dl.k8s.io/release/stable.txt','https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe','https://github.com/microsoft/WSL')) {
        try { $r=Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 15; [pscustomobject]@{URL=$url;HTTP=[int]$r.StatusCode;Erro=$null} } catch { [pscustomobject]@{URL=$url;HTTP=$null;Erro=$_.Exception.Message} }
    }
    $network | ConvertTo-Json | Set-Content 'resultados/evidencias/conectividade.json' -Encoding utf8
} finally { Stop-Transcript }
