# Explicação dos arquivos

## Código e imagem

`app.py` usa só biblioteca padrão: http.server cria ThreadingHTTPServer, urllib interpreta parâmetros, itertools enumera permutações, math calcula distância euclidiana e threading controla concorrência e contadores. O semáforo VAGA de capacidade 1 recusa concorrentes com 503. TRAVA_CONTAGEM protege totais nos logs. GET / serve HTML e SVG, /api/rota retorna JSON, /healthz e /readyz retornam status ok, rotas desconhecidas dão 404 e parâmetros inválidos dão 400. X-Pod e o campo pod identificam quem atendeu. A resposta fecha a conexão. Dados e cálculos são didáticos e não persistem em disco.

`Dockerfile`: FROM python:3.12-slim define base; WORKDIR /app define diretório; COPY leva app.py; PYTHONUNBUFFERED faz os logs aparecerem imediatamente e PYTHONDONTWRITEBYTECODE evita pyc; USER 10001:10001 remove root; EXPOSE documenta 8000, mas não publica porta; CMD mantém python como processo principal. `.dockerignore` exclui tudo, exceto app.py e Dockerfile, impedindo cópia de evidências e ferramentas locais.

## Manifestos

Todo YAML declara apiVersion, kind e metadata. namespace.yaml usa v1/Namespace e cria ops-lab. Deployment usa apps/v1, nome rotas, namespace explícito, uma réplica e selector app=rotas igual às labels do template. template.spec.containers define imagem e porta. IfNotPresent permite a imagem carregada no nó. ContainerPort não abre porta no host.

deployment-inicial.yaml preserva a primeira versão exigida pelo guia. deployment.yaml é a segunda. Requests: 500m CPU e 64Mi memória orientam scheduler. Limits: 500m e 128Mi restringem execução; CPU excedida provoca throttling, memória excedida pode causar OOMKilled. Como memória solicitada e limitada diferem, o QoS esperado é Burstable. Readiness GET /readyz:8000 a cada 5 s controla participação no Service. Liveness GET /healthz:8000 inicia após 10 s e repete a cada 10 s, reiniciando após falhas consecutivas. Readiness pronta não significa calculador desocupado.

SecurityContext exige usuário não root, impede escalada e torna raiz somente leitura. A aplicação não grava arquivos. A estratégia de rollout é a padrão do guia, RollingUpdate 25%/25%. Com uma réplica, maxSurge arredonda para 1 e maxUnavailable para 0, mantendo o Pod antigo durante imagem inválida. Não foram adicionados HPA, requests diferentes ou probes com parâmetros arbitrários.

Service usa v1/ClusterIP, rotas, namespace ops-lab, selector app=rotas, port 8000 e targetPort 8000. O controlador mantém EndpointSlices. kube-proxy encaminha conexões a destinos prontos. DNS curto funciona no mesmo namespace. Não existe garantia de partilha exata ou escolha do Pod menos ocupado. Port-forward escolhe um Pod para o túnel e não mede esse balanceamento.

Job usa batch/v1, carga, namespace ops-lab, backoffLimit 0 para evitar repetição automática e activeDeadlineSeconds 240 para limitar execução. restartPolicy Never deixa o resultado explícito. Sua label app=gerador-carga mantém o k6 fora do Service. A imagem grafana/k6:1.0.0 executa /scripts/carga.js. Requests de 250m/128Mi e limits 500m/256Mi limitam competição com a aplicação. Volume script vem do ConfigMap carga-script e é montado somente para leitura em /scripts.

## Carga e interpretação

TAXA é a quantidade de iterações iniciadas por segundo, PARADAS fica 9, DURACAO fica 60 e URL padrão é http://rotas:8000. constant-arrival-rate é modelo aberto: não espera uma resposta acabar para programar a próxima. Usa 40 VUs pré-alocados e máximos. Se faltam VUs, dropped_iterations cresce. noConnectionReuse abre conexão nova e permite nova escolha do Service.

Aquecimento: 10 s, sem métricas próprias. A medição começa aos 20 s, dando 10 s para pedidos pendentes do aquecimento terminarem, dura 60 s e admite gracefulStop 10 s. Métricas HTTP globais incluem outros períodos e não substituem métricas próprias. rotas_ok conta status 200 com ordem em array; falhas mede tentativas inválidas; latencia_ok registra apenas sucessos. Metas: falhas <1%, p95 <800 ms e dropped_iterations{scenario:medicao}=0. O p95 de sucessos deve ser lido junto com falhas. Saída 99 indica thresholds não atendidos, não falha do executor.

## Evidências e automação

CSV fornecido permanece intacto; resultados/comparativo.csv usa as mesmas 13 colunas. logs/ guarda saída bruta. evidencias/ guarda objetos, eventos, amostras de recursos e contadores. graficos/ contém somente gráficos derivados de série real completa. originais/ preserva os arquivos recebidos.

comum.ps1 centraliza verificações e contexto explícito. verificar-ambiente coleta diagnóstico. instalar-dependencias verifica ferramentas. iniciar-cluster cria infraestrutura. publicar-aplicacao faz Docker, duas versões e recriação. validar-aplicacao testa o Service. testar-rollback captura incidente e reverte em finally. executar-testes exige piloto antes da série, usa bloqueio de arquivo, não sobrescreve medições e preserva evidência de falha. consolidar-resultados.py recusa resumo incompleto e alteração/reinício de Pods, calcula medianas e gráficos. testar-capacidade pede seis e restaura uma réplica em finally. encerrar-ambiente para apenas o perfil do projeto. Scripts não transformam lacunas em zero.
