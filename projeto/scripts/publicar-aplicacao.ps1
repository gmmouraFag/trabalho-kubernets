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
