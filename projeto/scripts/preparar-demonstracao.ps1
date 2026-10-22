param([Parameter(Mandatory=$true)][string]$Destino)
$ErrorActionPreference='Stop'
$sourceRoot=Split-Path -Parent $PSScriptRoot
$destinationRoot=[IO.Path]::GetFullPath($Destino)
if(Test-Path -LiteralPath $destinationRoot){throw 'Escolha uma pasta de destino que ainda nao exista. Nenhum arquivo sera sobrescrito.'}
if($destinationRoot.StartsWith($sourceRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or $destinationRoot -eq $sourceRoot){throw 'A pasta de demonstracao deve ficar fora da pasta projeto original.'}
New-Item -ItemType Directory -Path $destinationRoot | Out-Null
foreach($file in @('app.py','Dockerfile','.dockerignore','carga.js','resultados_modelo.csv','README.md')){
    Copy-Item -LiteralPath (Join-Path $sourceRoot $file) -Destination (Join-Path $destinationRoot $file)
}
foreach($folder in @('k8s','scripts','originais')){
    New-Item -ItemType Directory -Path (Join-Path $destinationRoot $folder) | Out-Null
    Get-ChildItem -LiteralPath (Join-Path $sourceRoot $folder) -Force | Where-Object {$_.Name -ne '__pycache__'} | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $destinationRoot $folder) -Recurse
    }
}
foreach($folder in @('resultados/logs','resultados/evidencias','resultados/graficos','documentacao','apresentacao')){
    New-Item -ItemType Directory -Path (Join-Path $destinationRoot $folder) -Force | Out-Null
}
Copy-Item -LiteralPath (Join-Path $sourceRoot 'resultados_modelo.csv') -Destination (Join-Path $destinationRoot 'resultados/comparativo.csv')
@"
# Pasta de demonstracao

Criada a partir de $sourceRoot. Os resultados historicos nao foram copiados.
Os scripts de publicacao e testes gravarao somente as novas evidencias nesta pasta.
O cluster/perfil continua sendo ops-lab; separar pastas nao cria um segundo cluster.
Nao execute duas copias ao mesmo tempo contra o mesmo perfil.
Para estudar os resultados originais, consulte o repositorio de origem.
Para usar os geradores de documentacao/apresentacao, prefira a copia completa do repositorio.
"@ | Set-Content -LiteralPath (Join-Path $destinationRoot 'LEIA-ME-DEMONSTRACAO.md') -Encoding utf8
Write-Host "Pasta criada em: $destinationRoot"
Write-Host 'Abra o Docker Desktop manualmente. Depois entre nesta pasta e siga o roteiro de demonstracao.'
