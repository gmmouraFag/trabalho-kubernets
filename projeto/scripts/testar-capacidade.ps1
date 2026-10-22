. "$PSScriptRoot/comum.ps1"
Check-Cluster
try {
    K @('scale','deployment/rotas','--replicas=6')
    Start-Sleep -Seconds 15
    Save-K 'seis-replicas-pods.json' @('get','pods','-l','app=rotas','-o','json')
    Save-K 'seis-replicas-describe.txt' @('describe','pods','-l','app=rotas')
    Save-K 'seis-replicas-node.txt' @('describe','node','ops-lab')
    Save-K 'seis-replicas-eventos.txt' @('get','events','--sort-by=.lastTimestamp')
} finally {
    K @('scale','deployment/rotas','--replicas=1')
    K @('rollout','status','deployment/rotas','--timeout=180s')
}
