param(
    [ValidateSet('Piloto','Serie')][string]$Modo='Piloto',
    [ValidateRange(1,1000)][int]$Taxa=6,
    [string]$Rotulo='piloto',
    [string]$Justificativa=''
)
. "$PSScriptRoot/comum.ps1"
Check-Cluster
if($Rotulo -notmatch '^[a-z0-9-]+$'){throw 'Rotulo deve conter apenas letras minusculas, numeros e hifen.'}
$lockPath=Join-Path $LabRoot 'resultados/execucao.lock'
try{$lock=[IO.File]::Open($lockPath,'OpenOrCreate','ReadWrite','None')}catch{throw 'Outro teste esta em execucao.'}
function Read-JsonK([string[]]$Arguments){
    $raw=& kubectl --context=ops-lab -n ops-lab @Arguments
    if($LASTEXITCODE -ne 0){throw ('Falha: kubectl '+($Arguments -join ' '))}
    return ($raw | ConvertFrom-Json)
}
function Measure-Lab([string]$Label,[int]$Replicas,[string]$Round){
    $dir=Join-Path $LabRoot "resultados/evidencias/$Label"
    if(Test-Path -LiteralPath $dir){throw "Evidencias $Label ja existem. Use outro rotulo para repeticao."}
    $existing=Read-JsonK @('get','jobs','-o','json')
    if(@($existing.items | Where-Object {$_.metadata.name -eq 'carga'}).Count){throw 'Job carga preexistente. Salve seus logs e remova-o antes de continuar.'}
    New-Item -ItemType Directory -Path $dir | Out-Null
    K @('scale','deployment/rotas',"--replicas=$Replicas")
    K @('rollout','status','deployment/rotas','--timeout=180s')
    $converged=$false
    for($i=0;$i -lt 60;$i++){
        $pods=Read-JsonK @('get','pods','-l','app=rotas','-o','json')
        $live=@($pods.items | Where-Object {!$_.metadata.deletionTimestamp})
        $slices=Read-JsonK @('get','endpointslices','-l','kubernetes.io/service-name=rotas','-o','json')
        $readyEndpoints=@($slices.items | ForEach-Object {$_.endpoints} | Where-Object {$_.conditions.ready -and !$_.conditions.terminating})
        if($live.Count -eq $Replicas -and $readyEndpoints.Count -eq $Replicas){$converged=$true;break}
        Start-Sleep -Seconds 2
    }
    if(!$converged){throw 'EndpointSlices nao convergiram para a quantidade pedida.'}
    $pods | ConvertTo-Json -Depth 30 | Set-Content "$dir/pods-antes.json" -Encoding utf8
    $slices | ConvertTo-Json -Depth 30 | Set-Content "$dir/endpointslices.json" -Encoding utf8
    $before=& kubectl --context=ops-lab -n ops-lab logs -l app=rotas --prefix --tail=1
    if($LASTEXITCODE -ne 0){throw 'Contadores antes indisponiveis'}
    $before | Set-Content "$dir/contadores-antes.txt" -Encoding utf8
    # A unica alteracao no Job e a TAXA calibrada. Recursos, imagem e duracao ficam iguais.
    # Substituicao com avaliador evita ambiguidade entre $1 e o numero da taxa.
    $jobText=[regex]::Replace((Get-Content 'k8s/job-carga.yaml' -Raw),'(name: TAXA\s+value: ")[^"]+(\")',{param($m) $m.Groups[1].Value + $Taxa + $m.Groups[2].Value})
    $jobText | Set-Content "$dir/job.yaml" -Encoding utf8
    K @('apply','-f',"$dir/job.yaml")
    $started=Get-Date
    $lastSample=Get-Date '2000-01-01'
    $terminated=$false
    while(((Get-Date)-$started).TotalSeconds -lt 300){
        $jp=Read-JsonK @('get','pods','-l','job-name=carga','-o','json')
        if(((Get-Date)-$lastSample).TotalSeconds -ge 15){
            ('--- '+(Get-Date -Format o)) | Add-Content "$dir/recursos.txt" -Encoding utf8
            & kubectl --context=ops-lab -n ops-lab top pods 2>&1 | Add-Content "$dir/recursos.txt" -Encoding utf8
            $lastSample=Get-Date
        }
        if($jp.items.Count -gt 0){
            $cs=@($jp.items[0].status.containerStatuses)
            if($cs.Count -gt 0 -and $cs[0].state.terminated){$terminated=$true;break}
        }
        Start-Sleep -Seconds 3
    }
    # Evidencias sao coletadas mesmo se o Job falhar ou exceder o tempo.
    $log=& kubectl --context=ops-lab -n ops-lab logs job/carga 2>&1
    $log | Set-Content "resultados/logs/$Label.txt" -Encoding utf8
    $jp | ConvertTo-Json -Depth 40 | Set-Content "$dir/job-pods.json" -Encoding utf8
    & kubectl --context=ops-lab -n ops-lab get job carga -o json | Set-Content "$dir/job-status.json" -Encoding utf8
    & kubectl --context=ops-lab -n ops-lab get events --sort-by=.lastTimestamp | Set-Content "$dir/eventos.txt" -Encoding utf8
    $after=& kubectl --context=ops-lab -n ops-lab logs -l app=rotas --prefix --tail=1
    if($LASTEXITCODE -ne 0){throw 'Contadores depois indisponiveis. Job preservado.'}
    $after | Set-Content "$dir/contadores-depois.txt" -Encoding utf8
    & kubectl --context=ops-lab -n ops-lab get pods -l app=rotas -o json | Set-Content "$dir/pods-depois.json" -Encoding utf8
    if(!$terminated){throw 'Job nao terminou no prazo. Evidencias salvas, Job preservado. Nao e medicao.'}
    Run $LabPython @('scripts/consolidar-resultados.py','--importar',$Label,'--rodada',$Round,'--replicas',"$Replicas",'--taxa',"$Taxa")
    K @('delete','job','carga','--wait=true')
}
try{
    $configPath='resultados/calibracao.json'
    if($Modo -eq 'Piloto'){
        Measure-Lab $Rotulo 1 'calibracao'
        Write-Host 'Piloto salvo. Examine falhas, sucessos e dropped_iterations. Execute outro piloto com -Rotulo piloto2 e outra -Taxa se necessario.'
        Write-Host 'Para fixar a taxa, execute a Serie com -Justificativa explicando a escolha a partir dos pilotos.'
    }else{
        if(!(Test-Path $configPath)){
            if([string]::IsNullOrWhiteSpace($Justificativa)){throw 'Justifique a taxa com base nos pilotos completos.'}
            $rows=Import-Csv 'resultados/comparativo.csv' -Delimiter ';'
            $pilot=@($rows | Where-Object {$_.rodada -eq 'calibracao' -and $_.taxa -eq "$Taxa" -and $_.rotas_ok -ne '' -and $_.dropped_iterations_medicao -eq '0'})
            if(!$pilot.Count){throw 'Falta piloto completo desta taxa, sem iteracoes descartadas.'}
            @{taxa=$Taxa;paradas=9;duracao=60;justificativa=$Justificativa;data=(Get-Date -Format o);hash_app=(Get-FileHash app.py).Hash;hash_carga=(Get-FileHash carga.js).Hash;hash_deployment=(Get-FileHash k8s/deployment.yaml).Hash;hash_job=(Get-FileHash k8s/job-carga.yaml).Hash} | ConvertTo-Json | Set-Content $configPath -Encoding utf8
        }
        $cfg=Get-Content $configPath -Raw | ConvertFrom-Json
        if($cfg.taxa -ne $Taxa -or $cfg.hash_app -ne (Get-FileHash app.py).Hash -or $cfg.hash_carga -ne (Get-FileHash carga.js).Hash -or $cfg.hash_deployment -ne (Get-FileHash k8s/deployment.yaml).Hash -or $cfg.hash_job -ne (Get-FileHash k8s/job-carga.yaml).Hash){throw 'Parametros ou fontes mudaram depois de fixar a serie.'}
        foreach($run in @(@('3pods-a',3,'A'),@('1pod-a',1,'A'),@('2pods-a',2,'A'),@('2pods-b',2,'B'),@('3pods-b',3,'B'),@('1pod-b',1,'B'),@('1pod-c',1,'C'),@('2pods-c',2,'C'),@('3pods-c',3,'C'))){
            $done=Import-Csv 'resultados/comparativo.csv' -Delimiter ';' | Where-Object {$_.rotulo -eq $run[0] -and $_.rotas_ok -ne ''}
            if($done){Write-Host "Preservando medicao concluida: $($run[0])";continue}
            Measure-Lab $run[0] $run[1] $run[2]
        }
        Run $LabPython @('scripts/consolidar-resultados.py')
    }
}finally{$lock.Dispose()}
