"""Gera arquivos adicionais sem modificar app.py, carga.js ou os PDFs originais."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]

def write(name, content):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')

write('k8s/namespace.yaml', '''
apiVersion: v1
kind: Namespace
metadata:
  name: ops-lab
''')
initial = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: rotas
  namespace: ops-lab
  labels:
    app: rotas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rotas
  template:
    metadata:
      labels:
        app: rotas
    spec:
      containers:
        - name: rotas
          image: rotas:1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
'''
write('k8s/versoes/deployment-inicial.yaml', initial)
write('k8s/deployment.yaml', initial + '''          resources:
            requests:
              cpu: 500m
              memory: 64Mi
            limits:
              cpu: 500m
              memory: 128Mi
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8000
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          securityContext:
            runAsNonRoot: true
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
''')
write('k8s/service.yaml', '''
apiVersion: v1
kind: Service
metadata:
  name: rotas
  namespace: ops-lab
spec:
  type: ClusterIP
  selector:
    app: rotas
  ports:
    - port: 8000
      targetPort: 8000
''')
write('k8s/job-carga.yaml', '''
apiVersion: batch/v1
kind: Job
metadata:
  name: carga
  namespace: ops-lab
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 240
  template:
    metadata:
      labels:
        app: gerador-carga
    spec:
      restartPolicy: Never
      containers:
        - name: k6
          image: grafana/k6:1.0.0
          command: ["k6", "run", "/scripts/carga.js"]
          env:
            - name: TAXA
              value: "6"
            - name: PARADAS
              value: "9"
            - name: DURACAO
              value: "60"
          resources:
            requests:
              cpu: 250m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          volumeMounts:
            - name: script
              mountPath: /scripts
              readOnly: true
      volumes:
        - name: script
          configMap:
            name: carga-script
''')
write('scripts/comum.ps1', r'''
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
''')
write('scripts/verificar-ambiente.ps1', r'''
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
''')
write('scripts/instalar-dependencias.ps1', r'''
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
''')
write('scripts/iniciar-cluster.ps1', r'''
. "$PSScriptRoot/comum.ps1"
Start-Transcript -Path ("resultados/logs/cluster-"+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.txt')
try {
    Run 'docker' @('version')
    Run 'docker' @('info')
    Run 'minikube' @('start','-p','ops-lab','--driver=docker','--cpus=3','--memory=3072')
    Run 'minikube' @('profile','ops-lab')
    if ((& kubectl config current-context) -ne 'ops-lab') { throw 'Contexto atual inesperado.' }
    Check-Cluster
    Run 'kubectl' @('config','get-contexts')
    K @('cluster-info')
    K @('get','nodes','-o','wide')
    K @('get','pods','-A')
    K @('apply','-f','k8s/namespace.yaml')
    Run 'kubectl' @('config','set-context','ops-lab','--namespace=ops-lab')
    Run 'minikube' @('addons','enable','metrics-server','-p','ops-lab')
    K @('wait','--for=condition=Ready','node/ops-lab','--timeout=180s')
    K @('get','namespace','ops-lab')
    Save-K 'cluster-nodes.json' @('get','nodes','-o','json')
} finally { Stop-Transcript }
''')
write('scripts/publicar-aplicacao.ps1', r'''
. "$PSScriptRoot/comum.ps1"
Check-Cluster
Start-Transcript -Path ("resultados/logs/publicacao-"+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.txt')
try {
    Run 'docker' @('build','-t','rotas:1.0','.')
    Run 'docker' @('image','ls','rotas')
    Run 'docker' @('run','-d','--rm','-p','127.0.0.1:8000:8000','--name','rotas-teste','rotas:1.0')
    try {
        for($i=0;$i -lt 30;$i++){try{$r=Invoke-WebRequest 'http://localhost:8000/healthz';break}catch{Start-Sleep -Seconds 1}}
        foreach($path in @('/','/healthz','/readyz','/api/rota?paradas=9')) {
            $response=Invoke-WebRequest ("http://localhost:8000"+$path) -TimeoutSec 15
            if ($response.StatusCode -ne 200){throw "HTTP inesperado: $path"}
            $response.Content
            if($path -eq '/api/rota?paradas=9' -and ($response.Content | ConvertFrom-Json).ordem.Count -ne 11){throw 'Rota invalida'}
        }
        Run 'docker' @('logs','rotas-teste')
    } finally { Run 'docker' @('stop','rotas-teste') }
    Run 'minikube' @('image','load','rotas:1.0','-p','ops-lab')
    Run 'minikube' @('image','ls','-p','ops-lab')
    K @('apply','-f','k8s/versoes/deployment-inicial.yaml')
    K @('rollout','status','deployment/rotas','--timeout=180s')
    Save-K 'deployment-inicial.txt' @('get','deployment,replicaset,pods','-o','wide')
    Save-K 'pod-antes-recriacao.json' @('get','pods','-l','app=rotas','-o','json')
    K @('delete','pod','-l','app=rotas')
    K @('rollout','status','deployment/rotas','--timeout=180s')
    Save-K 'pod-depois-recriacao.json' @('get','pods','-l','app=rotas','-o','json')
    K @('apply','-f','k8s/deployment.yaml')
    K @('rollout','status','deployment/rotas','--timeout=180s')
    K @('rollout','history','deployment/rotas')
    Save-K 'deployment-final.txt' @('describe','deployment/rotas')
    Save-K 'pods-final.txt' @('describe','pods','-l','app=rotas')
    K @('apply','-f','k8s/service.yaml')
    $cm = & kubectl --context=ops-lab -n ops-lab create configmap carga-script --from-file=carga.js --dry-run=client -o yaml
    if($LASTEXITCODE -ne 0){throw 'Falha ao gerar ConfigMap'}
    $cm | & kubectl --context=ops-lab -n ops-lab apply -f -
    if($LASTEXITCODE -ne 0){throw 'Falha ao aplicar ConfigMap'}
} finally { Stop-Transcript }
''')
write('scripts/validar-aplicacao.ps1', r'''
param([switch]$PortForward)
. "$PSScriptRoot/comum.ps1"
Check-Cluster
K @('rollout','status','deployment/rotas','--timeout=180s')
Save-K 'service.txt' @('get','service','rotas','-o','yaml')
Save-K 'endpointslices.json' @('get','endpointslices','-l','kubernetes.io/service-name=rotas','-o','json')
$name='teste-'+(Get-Date -Format 'HHmmss')
K @('run',$name,'--rm','-i','--restart=Never','--image=busybox:1.36','--','sh','-c','wget -qO- http://rotas:8000/healthz && wget -qO- http://rotas:8000/readyz && wget -qO- http://rotas:8000/api/rota?paradas=9')
Save-K 'logs-aplicacao.txt' @('logs','-l','app=rotas','--prefix','--tail=100')
if($PortForward){K @('port-forward','--address=127.0.0.1','service/rotas','8080:8000')}
''')
write('scripts/testar-rollback.ps1', r'''
. "$PSScriptRoot/comum.ps1"
Check-Cluster
Start-Transcript -Path ("resultados/logs/rollback-"+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.txt')
try {
    $dep=& kubectl --context=ops-lab -n ops-lab get deployment rotas -o json | ConvertFrom-Json
    if($dep.spec.replicas -ne 1 -or $dep.spec.template.spec.containers[0].image -ne 'rotas:1.0'){throw 'Exercicio requer 1 replica de rotas:1.0'}
    K @('set','image','deployment/rotas','rotas=rotas:1.1')
    try {
        & kubectl --context=ops-lab -n ops-lab rollout status deployment/rotas --timeout=60s
        if($LASTEXITCODE -eq 0){throw 'Imagem 1.1 existe: a falha prevista nao ocorreu.'}
        Save-K 'rollback-falha-pods.txt' @('describe','pods','-l','app=rotas')
        Save-K 'rollback-falha-deployment.json' @('get','deployment','rotas','-o','json')
        Save-K 'rollback-eventos.txt' @('get','events','--sort-by=.lastTimestamp')
        K @('run','teste-rollback','--rm','-i','--restart=Never','--image=busybox:1.36','--','wget','-qO-','http://rotas:8000/healthz')
    } finally {
        K @('rollout','undo','deployment/rotas')
        K @('rollout','status','deployment/rotas','--timeout=180s')
    }
    Save-K 'rollback-recuperado.json' @('get','deployment','rotas','-o','json')
    K @('rollout','history','deployment/rotas')
} finally { Stop-Transcript }
''')
write('scripts/encerrar-ambiente.ps1', r'''
param([switch]$LimparNamespace)
. "$PSScriptRoot/comum.ps1"
Check-Cluster
if($LimparNamespace){K @('delete','namespace','ops-lab')}
Run 'minikube' @('stop','-p','ops-lab')
Write-Host 'Cluster parado. O perfil foi preservado. Use iniciar-cluster.ps1 para retomar.'
''')

if not (ROOT/'resultados/comparativo.csv').exists():
    (ROOT/'resultados/comparativo.csv').write_bytes((ROOT/'originais/resultados_modelo.csv').read_bytes())
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'originais').iterdir() if p.name != 'SHA256.csv'}
write('originais/hashes.json',json.dumps(hashes,indent=2,ensure_ascii=False))
print('Manifestos e scripts preparados em',ROOT)
