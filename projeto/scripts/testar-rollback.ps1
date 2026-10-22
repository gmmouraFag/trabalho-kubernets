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
