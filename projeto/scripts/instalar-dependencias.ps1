param([switch]$InstalarWSL)
. "$PSScriptRoot/comum.ps1"
Start-Transcript -Path ("resultados/logs/instalacao-"+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.txt')
try {
    foreach($item in @(@('kubectl','Kubernetes.kubectl'),@('minikube','Kubernetes.minikube'),@('docker','Docker.DockerDesktop'))) {
        if (!(Get-Command $item[0] -ErrorAction SilentlyContinue)) { Run 'winget' @('install','-e','--id',$item[1],'--source','winget','--disable-interactivity') }
    }
    if ($InstalarWSL) {
        $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if (!$admin) { throw 'Para habilitar o WSL inicialmente, abra PowerShell como administrador e repita com -InstalarWSL. Pode exigir reinicio.' }
        Run 'wsl' @('--install','--no-distribution')
    }
    Write-Host 'Abra Docker Desktop e aceite pessoalmente os termos exigidos. Reinicie somente quando solicitado pelo Windows. Depois execute verificar-ambiente.ps1.'
} finally { Stop-Transcript }
