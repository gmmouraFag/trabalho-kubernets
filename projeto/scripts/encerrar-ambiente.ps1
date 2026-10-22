param([switch]$LimparNamespace)
. "$PSScriptRoot/comum.ps1"
Check-Cluster
if($LimparNamespace){K @('delete','namespace','ops-lab')}
Run 'minikube' @('stop','-p','ops-lab')
Write-Host 'Cluster parado. O perfil foi preservado. Use iniciar-cluster.ps1 para retomar.'
