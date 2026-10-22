. "$PSScriptRoot/comum.ps1"
Check-Cluster
Start-Transcript -Path ("resultados/logs/comprovacao-final-"+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.txt')
try {
    K @('get','deployment,replicaset,pods','-o','wide')
    Save-K 'objetos-finais.json' @('get','deployment,replicaset,pods,service,configmap','-o','json')
    Save-K 'historico-final.txt' @('rollout','history','deployment/rotas')
    Save-K 'metrics-server.txt' @('get','pods','-n','kube-system','-l','k8s-app=metrics-server','-o','wide')
    $httpName='comprovacao-http-'+(Get-Date -Format 'HHmmss')
    K @('run',$httpName,'--restart=Never','--image=busybox:1.36','--','sh','-c','for path in / /healthz /readyz /api/rota?paradas=9; do echo ENDPOINT:$path; wget -S -O- http://rotas:8000$path; done')
    $completed=$false
    for($i=0;$i -lt 60;$i++){
        $pod=& kubectl --context=ops-lab -n ops-lab get pod $httpName -o json | ConvertFrom-Json
        if($LASTEXITCODE -ne 0){throw 'Falha ao consultar comprovacao HTTP'}
        if($pod.status.phase -in @('Succeeded','Failed')){$completed=$true;break}
        Start-Sleep -Seconds 1
    }
    Save-K 'http-interno-final.txt' @('logs',$httpName)
    Save-K 'http-interno-pod.json' @('get','pod',$httpName,'-o','json')
    if(!$completed -or $pod.status.phase -ne 'Succeeded'){throw 'Comprovacao HTTP interna falhou. Pod preservado.'}
    K @('delete','pod',$httpName)
    Save-K 'events-final.txt' @('get','events','--sort-by=.lastTimestamp')
    Run 'docker' @('run','-d','--rm','-p','127.0.0.1:8000:8000','--name','rotas-teste','rotas:1.0')
    try {
        $ready=$false
        for($i=0;$i -lt 30;$i++){try{Invoke-WebRequest 'http://localhost:8000/healthz' | Out-Null;$ready=$true;break}catch{Start-Sleep -Seconds 1}}
        if(!$ready){throw 'Contêiner Docker nao ficou pronto'}
        $responses=foreach($path in @('/','/healthz','/readyz','/api/rota?paradas=9')) {
            $res=Invoke-WebRequest ("http://localhost:8000"+$path) -TimeoutSec 15
            if($res.StatusCode -ne 200){throw "HTTP inesperado: $path"}
            [pscustomobject]@{Endpoint=$path;HTTP=$res.StatusCode;Body=$res.Content;Pod=$res.Headers['X-Pod']}
        }
        $responses | ConvertTo-Json -Depth 6 | Set-Content 'resultados/evidencias/http-docker.json' -Encoding utf8
        & docker logs rotas-teste | Set-Content 'resultados/evidencias/logs-docker.txt' -Encoding utf8
    } finally { Run 'docker' @('stop','rotas-teste') }
    Run 'minikube' @('image','ls','-p','ops-lab')
} finally { Stop-Transcript }
