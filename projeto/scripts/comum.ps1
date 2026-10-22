$ErrorActionPreference = 'Stop'
$LabRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $LabRoot
$LabPython = if (Test-Path -LiteralPath "$LabRoot/.ferramentas/Scripts/python.exe") { "$LabRoot/.ferramentas/Scripts/python.exe" } else { 'python' }
$env:PATH = [Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH','User') + ';' + $env:PATH
foreach ($extraPath in @("$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin",'C:\Program Files\Docker\Docker\resources\bin','C:\Program Files\Kubernetes\Minikube',"$env:LOCALAPPDATA\Microsoft\WinGet\Links")) {
    if (Test-Path -LiteralPath $extraPath) { $env:PATH = $extraPath + ';' + $env:PATH }
}
function Run([string]$Exe, [string[]]$Arguments) {
    Write-Host ('> '+$Exe+' '+($Arguments -join ' '))
    & $Exe @Arguments 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "$Exe terminou com codigo $LASTEXITCODE" }
}
function K([string[]]$Arguments) {
    Run 'kubectl' (@('--context=ops-lab','--namespace=ops-lab') + $Arguments)
}
function Check-Cluster {
    $ctx = & kubectl config view -o json | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel ler kubeconfig.' }
    $match = @($ctx.contexts | Where-Object { $_.name -eq 'ops-lab' })
    if ($match.Count -ne 1 -or $match[0].context.cluster -ne 'ops-lab') { throw 'Contexto ops-lab ausente ou aponta para outro cluster.' }
    Run 'minikube' @('status','-p','ops-lab')
}
function Save-K([string]$Name, [string[]]$Arguments) {
    $result = & kubectl --context=ops-lab --namespace=ops-lab @Arguments 2>&1
    $code = $LASTEXITCODE
    $result | Out-File -LiteralPath "resultados/evidencias/$Name" -Encoding utf8
    if ($code -ne 0) { throw "Falha ao coletar $Name. Veja a evidencia." }
}
