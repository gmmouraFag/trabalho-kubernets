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
