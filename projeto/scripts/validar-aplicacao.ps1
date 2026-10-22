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
