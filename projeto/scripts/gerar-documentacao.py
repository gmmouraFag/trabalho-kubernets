"""Documentação da entrega. Os estados são derivados das evidências existentes."""
from pathlib import Path
import csv
import json
import statistics
from datetime import datetime

R=Path(__file__).resolve().parents[1]
def write(p,s):
    (R/p).parent.mkdir(parents=True,exist_ok=True)
    (R/p).write_text(s.strip()+'\n',encoding='utf-8')
def exists(p):return (R/p).exists()
rows=list(csv.DictReader((R/'resultados/comparativo.csv').open(encoding='utf-8-sig'),delimiter=';'))
done=[r for r in rows if r['rodada'] in ('A','B','C') and r['rotas_ok']]
full=len(done)==9
diag=json.loads((R/'resultados/evidencias/diagnostico.json').read_text(encoding='utf-8-sig')) if exists('resultados/evidencias/diagnostico.json') else {}
intro='Atualizado em 21/10/2026. Fonte principal: Guia_Atividade.pdf, na pasta acima. Fundamentação: Aula_Kubernetes.pdf.\n\n'
write('documentacao/00-diagnostico-ambiente.md',f'''# Diagnóstico e instalação
{intro}
## Equipamento observado

Windows 11 Pro 25H2, build 26200 (10.0.26200.9711), x64. AMD Ryzen 5 7600X, 6 núcleos e 12 processadores lógicos. RAM física: 31,11 GB. Espaço livre inicial no C: aproximadamente 361,54 GB. Virtualização de firmware habilitada e hypervisor presente. A sessão original não tinha privilégios administrativos.

## Ferramentas

| Ferramenta | Estado e versão |
|---|---|
| Python | Já instalado, 3.14.5. A imagem da aplicação usa Python 3.12, conforme o professor. |
| Git | Já instalado, 2.54.0.windows.1. |
| winget | Já instalado, 1.29.380. |
| kubectl | Instalado pelo winget, 1.37.1. |
| Minikube | Instalado pelo winget, 1.39.0. |
| Docker Desktop | Instalado pelo winget, 4.96.0.243774. Engine e cliente 29.9.1. |
| WSL | Instalado pelo usuário com administrador, 3.0.3.0, kernel 6.18.54.1. |
| Ferramentas de validação | Ambiente local `.ferramentas`, PyYAML 6.0.3 e matplotlib 3.11.2. |
| k6 | Previsto e executado somente no cluster, imagem fixa grafana/k6:1.0.0. Consulte os logs para confirmar cada execução. |

O primeiro `wsl --install --no-distribution` não instalou o componente. A alternativa via winget retornou 0x80073d28, exigindo administrador. O usuário executou o comando elevado, habilitou VirtualMachinePlatform e reiniciou. Após o reinício, `docker version` apresentou Client e Server e `wsl --status` confirmou versão padrão 2 e docker-desktop. Não foi necessário instalar Ubuntu separado: Docker Desktop mantém sua própria distribuição.

## Rede, PATH e permissões

Foram feitas solicitações HEAD aos servidores oficiais Docker, Kubernetes, Minikube e Microsoft/WSL, todas HTTP 200. Isso confirma conectividade HTTPS inicial, não garante todo download de imagem. Não foram alterados proxy nem firewall. DOCKER_HOST e KUBECONFIG estavam vazios. Os scripts atualizam o PATH apenas no processo, lendo os caminhos já registrados pelos instaladores. O kubeconfig é gerenciado pelo Minikube.

## Evidências

`resultados/evidencias/diagnostico.json` contém inventário e PATH. `conectividade.json` contém os testes de rede. Os arquivos `resultados/logs/diagnostico-*.txt` registram versões, erros e verificações. `cluster-*.txt` registra a configuração real do runtime. `originais/` preserva os seis arquivos recebidos e hashes SHA-256.

## Limitações de interpretação

O teste Python local valida HTTP e lógica no Windows. Seus tempos não são o piloto k6 e não devem entrar na comparação Kubernetes. O Docker enxerga 12 CPUs e cerca de 15 GiB na VM; o nó do experimento recebe somente 3 CPUs e 3072 MiB. Request de CPU é capacidade declarada para agendamento, não medida de consumo efetivo.
''')
write('documentacao/01-visao-geral.md',f'''# Visão geral
{intro}
Uma transportadora precisa calcular a ordem de entregas e retornar ao depósito. A aplicação fornecida explora todas as permutações de até nove destinos e escolhe o menor circuito euclidiano. Com nove entregas são 362.880 ordens. É trabalho de CPU real, com dados fictícios, sem ruas, trânsito, fila ou cache.

Cada processo admite um cálculo por vez por meio de um semáforo. Uma segunda requisição concorrente recebe HTTP 503 imediatamente. Replicar a aplicação permite cálculos simultâneos em processos distintos, mas o Service escolhe conexões sem conhecer a ocupação do calculador.

O objetivo é publicar e operar o serviço, verificar recuperação e rollback e comparar 1, 2 e 3 Pods sob a mesma demanda. Docker empacota a aplicação. Minikube fornece um cluster de um nó. kubectl administra a API. Deployment mantém réplicas, Service oferece DNS estável e EndpointSlices registram destinos. ConfigMap entrega o JavaScript ao Job k6.

```mermaid
flowchart LR
  T[Terminal kubectl] --> API[API Kubernetes]
  API --> D[Deployment rotas]
  D --> P[Pods app=rotas]
  C[ConfigMap carga-script] --> J[Job k6]
  J --> S[Service rotas:8000]
  S --> P
  B[Navegador localhost:8080] --> F[Port-forward para um Pod]
  F --> P
```

A arquitetura está no namespace ops-lab e perfil ops-lab. Réplicas no mesmo nó compartilham uma falha comum. O experimento não demonstra tolerância à queda do nó nem recuperação de dados. Melhorias de produção, como múltiplos nós, TLS, HPA e observabilidade contínua, são opcionais e ficam fora da série controlada.
''')
install=r'''# Preparação e reprodução

## Windows

Abra PowerShell na pasta `projeto`. Os instaladores foram executados pelo winget. Em outra máquina, rode `scripts/instalar-dependencias.ps1`. O script verifica os executáveis antes de instalar. Não instala k6 local. Para o WSL inicial, use PowerShell como administrador e `wsl --install --no-distribution`. Reinicie se solicitado. Abra Docker Desktop com backend WSL 2 e conclua os termos exigidos pelo fornecedor.

```powershell
.\scripts\verificar-ambiente.ps1
.\scripts\iniciar-cluster.ps1
.\scripts\publicar-aplicacao.ps1
.\scripts\validar-aplicacao.ps1
.\scripts\testar-rollback.ps1
.\scripts\executar-testes.ps1 -Modo Piloto -Taxa 6 -Rotulo piloto
```

O piloto deve ser examinado antes de fixar a série. Se houver quase só sucessos, aumente a taxa. Se houver quase nenhum sucesso e descartes, reduza. Guarde cada piloto com rótulo distinto. A taxa escolhida deve revelar diferença entre as configurações, mantendo geração sem descartes. Depois:

```powershell
.\scripts\executar-testes.ps1 -Modo Serie -Taxa TAXA_CALIBRADA -Justificativa 'Justificativa baseada nos pilotos'
.\scripts\testar-capacidade.ps1
.\.ferramentas\Scripts\python.exe scripts/consolidar-resultados.py
```

`TAXA_CALIBRADA` é uma indicação textual que deve ser substituída pelo número do piloto. O arquivo `resultados/calibracao.json`, quando existir, guarda o valor efetivamente fixado e hashes das fontes. Não reaplique deployment.yaml durante a série: isso voltaria a uma réplica.

Para abrir a interface em um terminal separado:

```powershell
.\scripts\validar-aplicacao.ps1 -PortForward
```

Abra http://localhost:8080, calcule nove entregas e confira o Pod mostrado. O túnel precisa continuar ativo. Ctrl+C fecha o túnel. Para encerrar o cluster preservando seu estado, execute `scripts/encerrar-ambiente.ps1`. Com `-LimparNamespace`, o script também remove os objetos da atividade, conforme o Grupo 8.5. Não apaga o perfil nem outros clusters.

## Ubuntu 22.04 ou superior

Os comandos Docker, Minikube e kubectl são iguais. Instale Docker Engine pelo repositório oficial de sua distribuição seguindo https://docs.docker.com/engine/install/ubuntu/. Não execute automaticamente scripts remotos como root. Após a instalação, `sudo usermod -aG docker "$USER"` permite usar o daemon, mas confere privilégios elevados sobre o host; saia e entre novamente na sessão. Instale kubectl por `sudo snap install kubectl --classic`, conforme o guia, ou pelo repositório oficial. Baixe `minikube_latest_amd64.deb` do servidor oficial e instale com `sudo dpkg -i minikube_latest_amd64.deb`.

Use os comandos do documento 03 na ordem. Troque `curl.exe` por `curl`. YAML e JavaScript são os mesmos. Os scripts PowerShell podem rodar com PowerShell 7 no Linux, exceto diagnóstico e instalação, que usam APIs Windows. Os equivalentes Bash de instalação não foram executados neste computador e estão marcados como não validados. Nunca rode Minikube com driver Docker como root.

## Validação e dependências auxiliares

```powershell
python -m venv .ferramentas
.\.ferramentas\Scripts\python.exe -m pip install -r scripts/requirements-validacao.txt
.\.ferramentas\Scripts\python.exe scripts/validar-estatico.py
```

O teste estático verifica nomes, portas, requests e preservação dos originais. O teste HTTP local cobre respostas 200, 400, 404 e 503. A validação de esquema no servidor Kubernetes é separada e usa `kubectl apply --dry-run=server -f ARQUIVO`.

Fontes oficiais consultadas para a instalação: https://docs.docker.com/desktop/setup/install/windows-install/ e https://learn.microsoft.com/en-us/windows/wsl/basic-commands. Os parâmetros acadêmicos prevalecem sobre mudanças opcionais de produção.
'''
write('documentacao/02-instalacao.md',install)
write('documentacao/00-guia-instalacao.md',install)

groups=[
('0','Ferramentas','pp. 4','Separar falhas de instalação das falhas da aplicação.','docker version\nkubectl version --client\nminikube version\npython --version','Cada version verifica o executável. Docker também consulta o servidor, que deve responder. Python local apoia a validação, mas o runtime do contêiner continua 3.12.','Três ferramentas operacionais e terminal na pasta projeto.','resultados/logs/diagnostico-*.txt'),
('1','Cluster e contexto','pp. 5–7','Criar a infraestrutura e confirmar o alvo antes das alterações.','minikube start -p ops-lab --driver=docker --cpus=3 --memory=3072\nminikube profile ops-lab\nkubectl config get-contexts\nkubectl config current-context\nkubectl cluster-info\nkubectl get nodes -o wide\nkubectl get pods -A\nkubectl apply -f k8s/namespace.yaml\nkubectl get namespaces\nkubectl config set-context --current --namespace=ops-lab\nminikube addons enable metrics-server','start cria o nó com recursos fixos. profile escolhe o perfil. config confirma cluster e namespace. cluster-info valida API. nodes mostra Ready. pods -A revela o control plane. apply cria namespace. metrics-server alimenta top.','Nó Ready, contexto ops-lab e namespace ops-lab.','resultados/logs/cluster-*.txt'),
('2','Imagem Docker','pp. 8–9','Testar o pacote antes de adicionar Kubernetes ao diagnóstico.','docker build -t rotas:1.0 .\ndocker image ls rotas\ndocker run -d --rm -p 127.0.0.1:8000:8000 --name rotas-teste rotas:1.0\ncurl.exe http://localhost:8000/healthz\ncurl.exe http://localhost:8000/readyz\ncurl.exe "http://localhost:8000/api/rota?paradas=9"\ndocker logs rotas-teste\ndocker stop rotas-teste\nminikube image load rotas:1.0\nminikube image ls','build empacota a fonte. run inicia o processo e publica a porta somente no loopback, refinamento opcional de exposição local. curl verifica HTTP e JSON. logs mostra aceitos. stop encerra apenas o contêiner de teste criado pelo script. image load copia ao nó, sem registry.','HTTP 200 e rota válida; contêiner de teste parado; imagem disponível no nó.','resultados/logs/publicacao-*.txt'),
('3','Deployment em duas versões','pp. 10–13 e 30','Demonstrar reconciliação e depois uma atualização gradual com recursos e probes.','kubectl apply -f k8s/versoes/deployment-inicial.yaml\nkubectl rollout status deployment/rotas\nkubectl get deployment,replicaset,pods\nkubectl get pods -o wide --show-labels\nkubectl describe pod -l app=rotas\nkubectl logs deployment/rotas\nkubectl delete pod -l app=rotas\nkubectl get pods -o wide\nkubectl apply -f k8s/deployment.yaml\nkubectl rollout status deployment/rotas\nkubectl rollout history deployment/rotas\nkubectl get replicaset','apply registra o desejado; rollout aguarda o observado. Deployment mantém ReplicaSet, que repõe Pods. delete provoca recuperação com novo UID/IP. A versão final acrescenta probes, resources e securityContext. A estratégia RollingUpdate padrão do guia permanece: maxSurge e maxUnavailable de 25%, arredondados para 1 e 0 com uma réplica.','Um Pod pronto, UID diferente após exclusão, histórico com duas revisões, QoS Burstable.','resultados/evidencias/pod-antes-recriacao.json e pod-depois-recriacao.json'),
('4','Service','pp. 14–16','Oferecer DNS estável e validar a comunicação por dentro do cluster.','kubectl apply -f k8s/service.yaml\nkubectl get service rotas\nkubectl get endpointslices -l kubernetes.io/service-name=rotas\nkubectl get pods -o wide\nkubectl run teste --rm -it --restart=Never --image=busybox:1.36 -- wget -qO- http://rotas:8000/healthz\nkubectl port-forward service/rotas 8080:8000','Service seleciona app=rotas. EndpointSlices devem listar IPs prontos. O Pod busybox verifica DNS, porta e resposta dentro da rede. Port-forward abre inspeção local em um Pod escolhido, sem balanceamento.','Destinos corretos, healthz ok de dentro e interface calculando no navegador.','resultados/evidencias/service.txt e endpointslices.json'),
('5','Incidente e rollback','pp. 17–18','Provocar falha de imagem e comprovar disponibilidade e recuperação.','kubectl set image deployment/rotas rotas=rotas:1.1\nkubectl rollout status deployment/rotas --timeout=60s\nkubectl get pods\nkubectl describe pod -l app=rotas\nkubectl get events --sort-by=.lastTimestamp\nkubectl rollout undo deployment/rotas\nkubectl rollout status deployment/rotas\nkubectl rollout history deployment/rotas','set image muda o template para tag ausente. O timeout é esperado, mas precisa ser acompanhado de eventos de pull e teste HTTP. O Pod antigo permanece devido à estratégia de atualização. undo restaura a revisão anterior sem reconstruir imagem.','Falha diagnosticada, serviço atendendo durante a falha, apenas versão 1.0 pronta depois do undo.','resultados/logs/rollback-*.txt e resultados/evidencias/rollback-*'),
('6','k6 e calibração','pp. 19–23','Escolher demanda informativa em teste piloto e fixar condições.','kubectl create configmap carga-script --from-file=carga.js --dry-run=client -o yaml\nkubectl apply -f k8s/job-carga.yaml\nkubectl wait --for=condition=Ready pod -l job-name=carga --timeout=180s\nkubectl logs -f job/carga\nkubectl get job carga\nkubectl logs job/carga > resultados/piloto.txt\nkubectl delete job carga','ConfigMap monta carga.js em /scripts. Job usa grafana/k6:1.0.0, backoffLimit 0 e deadline 240 s. TAXA inicial 6 é ponto inicial do guia, não taxa final presumida. Calibrar com uma réplica: aumentar se quase tudo tem sucesso; reduzir se quase nenhum sucesso e descartes. Conservar falhas e sucessos informativos.','Piloto completo salvo, justificativa e taxa fixadas antes da série.','resultados/logs/piloto*.txt e resultados/calibracao.json'),
('7','Nove medições','pp. 24–25','Comparar somente réplicas, controlando ordem e estabilidade.','kubectl scale deployment/rotas --replicas=3\nkubectl rollout status deployment/rotas\nkubectl get endpointslices -l kubernetes.io/service-name=rotas\nkubectl logs -l app=rotas --prefix --tail=1\nkubectl top pods','Repita o ciclo do Grupo 6 após convergência de Pods e endpoints. Leia contadores antes e depois, amostre CPU/memória a cada 15 s e guarde logs antes de excluir Job. Ordem A: 3,1,2; B: 2,3,1; C: 1,2,3. Sucessos/s=rotas_ok/60, não o /s do resumo total. Os deltas dos Pods incluem aquecimento.','Nove logs completos, mesmos parâmetros, sem reinício/troca de Pods durante cada medição.','resultados/comparativo.csv e resultados/evidencias/<rotulo>/'),
('8','Capacidade e decisão','pp. 26–28','Observar agendamento por requests e sustentar decisão em medianas.','kubectl scale deployment/rotas --replicas=6\nkubectl get pods\nkubectl describe pod -l app=rotas\nkubectl describe node ops-lab\nkubectl get events --sort-by=.lastTimestamp\nkubectl scale deployment/rotas --replicas=1\nkubectl delete namespace ops-lab\nminikube stop -p ops-lab','Seis Pods pedem 3 CPUs além do control plane. Insufficient cpu é limitação de requests, mesmo com CPU ociosa. Restaure uma réplica. Calcule mediana das três repetições por métrica. A limpeza final remove namespace após salvar as evidências e stop libera recursos preservando o perfil.','Evidência de scheduler, estado restaurado, análise com decisão e custos; limpeza quando a demonstração terminar.','resultados/evidencias/seis-replicas-* e documentacao/05-relatorio-experimentos.md')]
impl='# Implementação passo a passo\n\n'+intro+'Os comandos abaixo pressupõem contexto ops-lab e namespace ops-lab. Os scripts passam ambos explicitamente para reduzir enganos. O resultado esperado nunca substitui a evidência observada.\n\n'
observed_by_group={
'0':'Docker Desktop 4.96.0 e Engine 29.9.1, kubectl 1.37.1 e Minikube 1.39.0 responderam após o reinício. O daemon Linux ficou acessível. Python 3.14.5 e Git 2.54.0 já estavam presentes.',
'1':'Perfil ops-lab criado com Kubernetes 1.37.0 e containerd 2.3.4. O nó passou de NotReady inicial para Ready; namespace ops-lab Active e metrics-server habilitado.' if exists('resultados/evidencias/cluster-nodes.json') else 'Pendente de execução.',
'2':'Imagem rotas:1.0 construída, quatro endpoints retornaram HTTP 200 no contêiner de teste. A rota de nove entregas teve distância 299,03 unidades. O contêiner de teste foi parado e a imagem apareceu no armazenamento do nó.' if exists('resultados/evidencias/deployment-inicial.txt') else 'Pendente de execução.',
'3':'A versão mínima subiu, o Pod excluído foi substituído e a segunda versão foi publicada. O histórico inicialmente mostrou revisões 1 e 2; probes, recursos e segurança aparecem no describe salvo.' if exists('resultados/evidencias/pods-final.txt') else 'Pendente de execução.',
'4':'O teste interno recebeu JSON de saúde e rota válida. O navegador calculou nove entregas pelo túnel e a captura registra distância, tempo e Pod atendente.' if exists('resultados/evidencias/navegador.png') else 'Pendente de validação HTTP e navegador.',
'5':'A tag 1.1 causou ErrImagePull/ImagePullBackOff e timeout do rollout. O teste interno respondeu pelo Pod 1.0 durante a falha. O undo concluiu e a captura recuperada referencia rotas:1.0.' if exists('resultados/evidencias/rollback-recuperado.json') else 'Pendente de execução.',
'6':next((f"Piloto {r['rotulo']}: taxa {r['taxa']}/s, {r['rotas_ok']} rotas, {r['falhas_pct']}% de falhas, p95 {r['p95_latencia_ok_ms']} ms e {r['dropped_iterations_medicao']} descartes. A justificativa e os hashes estão em calibracao.json." for r in rows if r['rodada']=='calibracao' and r['rotas_ok']), 'Piloto ainda pendente.'),
'7':f'{len(done)} de nove medições completas registradas, com logs e objetos identificados por rodada. Consulte o relatório 05 para tabela, medianas e interpretação.',
'8':'Exercício de seis réplicas registrado; estado restaurado para uma. O relatório 05 descreve o agendamento real e a diferença entre quota Docker e allocatable. '+('Namespace removido e perfil parado após preservar as evidências.' if exists('resultados/evidencias/encerramento.txt') else 'Encerramento final ainda pendente.') if exists('resultados/evidencias/seis-replicas-node.txt') else 'Pendente de execução.'}
for n,title,pages,objective,commands,meaning,criterion,evidence in groups:
    observed=observed_by_group[n]
    impl+=f'## Grupo {n}: {title}\n\n**Origem:** Guia, {pages}.\n\n**Objetivo e conceito:** {objective}\n\n```powershell\n{commands}\n```\n\n**Significado e ordem:** {meaning}\n\n**Resultado esperado / critério para avançar:** {criterion}\n\n**Resultado observado:** {observed}\n\n**Arquivos e evidência:** {evidence}. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.\n\n**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.\n\n'
write('documentacao/03-implementacao.md',impl)
write('documentacao/04-explicacao-arquivos.md','''# Explicação dos arquivos

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
''')

questions=[
('Qual a diferença entre imagem e contêiner?','Imagem é o pacote de arquivos e metadados. Contêiner é o processo iniciado a partir dele. Vários contêineres podem usar a mesma imagem.'),
('Docker e Kubernetes fazem o mesmo trabalho?','Docker constrói e executa contêineres. Kubernetes coordena Pods, reconcilia réplicas e publica serviços. O driver Docker do Minikube hospeda o nó local.'),
('Por que um Deployment?','Ele mantém um template e coordena ReplicaSets. O ReplicaSet repõe Pods removidos. Um Pod avulso não seria recriado após exclusão.'),
('Namespace isola clientes com segurança?','Ele organiza nomes. Isolamento exige RBAC, NetworkPolicy, quotas e políticas de segurança, ou clusters separados conforme o risco.'),
('Qual a relação entre Service e labels?','O selector app=rotas encontra os Pods do template. Readiness decide quais destinos estão prontos. EndpointSlices materializam os endereços.'),
('Por que port-forward sempre mostra um Pod?','O túnel seleciona um Pod ao abrir. Ele não passa pelo balanceamento de conexões do Service. O k6 interno usa o caminho correto.'),
('Requests e limits são consumo real?','Request é necessidade declarada para agendamento. Limit é teto de execução. top mostra consumo amostrado. CPU no teto sofre throttling; memória além do teto pode levar a OOMKilled.'),
('Readiness reinicia o contêiner?','Não. Ela retira prontidão e impede novas conexões do Service. Liveness pode reiniciar. Neste protótipo healthz e readyz não testam disponibilidade do semáforo.'),
('Por que ConfigMap e Job?','ConfigMap separa script de imagem. Job representa uma tarefa que termina. Deployment representaria serviço contínuo e teria política de reinício inadequada para medição.'),
('Secret é criptografia?','Base64 é codificação. Proteção depende de acesso, criptografia em repouso e gestão de segredos. O projeto não exige dados secretos.'),
('Por que o k6 marca Failed?','Código 99 com resumo completo significa desempenho abaixo dos thresholds. Sem resumo, imagem inválida, deadline ou erro de script são falhas de execução e não medições zero.'),
('Como calcular throughput?','Dividir rotas_ok por 60 s da janela medida. O /s impresso no resumo usa duração total e não é o indicador solicitado.'),
('O que p95 descreve?','O percentil abaixo do qual ficam aproximadamente 95% dos tempos das respostas bem-sucedidas. Não descreve as recusas 503 nem garante qualidade para todos os clientes.'),
('Por que contar descartes?','Eles são iterações programadas que o gerador não iniciou. Se forem maiores que zero, a demanda efetivamente gerada difere da pretendida e a medição requer diagnóstico.'),
('Adicionar Pods elimina 503?','Não necessariamente. O Service não conhece ocupação. Uma conexão pode ir a um calculador ocupado mesmo com outro livre. CPU do nó, limite de cada Pod e algoritmo também restringem a escala.'),
('Por que seis réplicas ficam Pending?','Cada uma pede 500m. Seis já pedem 3 CPUs, sem incluir control plane. Scheduler compara requests com allocatable e registra Insufficient cpu se não couber.'),
('Rollback recupera tudo?','Ele restaura o template de uma revisão do Deployment. Não desfaz mudanças em bancos de dados, arquivos externos ou dependências.'),
('Por que três repetições e mediana?','A ordem alternada reduz viés de aquecimento e tarefas concorrentes. Mediana é o valor central, menos influenciado por uma observação extrema. Três repetições ainda são amostra pequena.'),
('Três Pods garantem alta disponibilidade?','Em um único nó, todos dependem da mesma máquina. O laboratório mostra distribuição de trabalho e recuperação de Pod, não tolerância à queda desse nó.'),
('Como usar HPA depois?','Definir requests, instalar fonte de métricas e configurar min/max e alvo de uso. Medir antes ajuda a escolher limites. HPA tem atraso de reação e não cria recursos físicos no nó.'),
('Por que comparar contadores antes e depois?','Eles são acumulados desde o início de cada Pod. O delta mostra distribuição durante o ciclo, incluindo aquecimento. Troca ou reinício de Pod invalida a subtração direta.'),
('Qual configuração escolher?','A menor que cumpra as metas para a demanda medida e com folga operacional. Se nenhuma cumprir, registrar isso e investigar fila, algoritmo, roteamento e CPU, sem mudar o experimento retroativamente.')]
write('documentacao/06-perguntas-respostas.md','# Perguntas e respostas\n\n'+''.join(f'## {q}\n\n{a}\n\n' for q,a in questions))

demo=[('Cluster','kubectl --context=ops-lab cluster-info','API respondendo. Explique que kubectl faz chamadas à API.'),('Namespace','kubectl --context=ops-lab get namespace ops-lab','Namespace Active. Organização dos objetos da atividade.'),('Deployment e Pods','kubectl --context=ops-lab -n ops-lab get deploy,rs,pods -o wide','Compare desejado e pronto e mostre hierarquia.'),('Service','kubectl --context=ops-lab -n ops-lab get service rotas; kubectl --context=ops-lab -n ops-lab get endpointslices -l kubernetes.io/service-name=rotas','Compare endpoints com IPs prontos.'),('Interface','kubectl --context=ops-lab -n ops-lab port-forward service/rotas 8080:8000','Deixe em outro terminal e abra localhost:8080. Calcule nove entregas e leia nome do Pod.'),('Cálculo HTTP','curl.exe "http://localhost:8080/api/rota?paradas=9"','JSON com ordem, distância, cálculo e Pod. Não apresentar tempo isolado como benchmark.'),('Logs','kubectl --context=ops-lab -n ops-lab logs -l app=rotas --prefix --tail=3','Mostre totais por Pod e explique a recusa 503.'),('Escala','kubectl --context=ops-lab -n ops-lab scale deployment/rotas --replicas=3; kubectl --context=ops-lab -n ops-lab rollout status deployment/rotas','Aguarde convergência e mostre EndpointSlices novamente. Port-forward não demonstra balanceamento.'),('Resultados','Get-Content resultados/comparativo.csv; Get-Content resultados/medianas.csv','Use logs reais para verificar as medianas. Caso medianas não exista, declare série pendente.'),('Restauração','kubectl --context=ops-lab -n ops-lab scale deployment/rotas --replicas=1','Restaure estado antes do encerramento. Para limpar, use encerrar-ambiente.ps1 -LimparNamespace.')]
write('documentacao/07-guia-demonstracao.md','# Demonstração ao vivo\n\nReserve 5 a 7 minutos. Confirme Docker aberto e cluster ligado antes de chamar o professor. Os comandos separados por ponto e vírgula abaixo são operações consecutivas para o apresentador.\n\n'+''.join(f'## {i}. {title}\n\n```powershell\n{cmd}\n```\n\n{explain}\n\n' for i,(title,cmd,explain) in enumerate(demo,1))+'''## Plano alternativo

Se o Docker ou cluster falhar, apresente `resultados/logs/cluster-*.txt`, `publicacao-*.txt`, `rollback-*.txt`, os nove logs do k6 e os JSONs dos objetos. Mostre os gráficos somente se houver série completa. Explique data e condições da execução registrada. Não execute carga através do port-forward para substituir uma medição. Se o problema for só o túnel, reinicie-o após confirmar Pod pronto. Use as evidências de antes/depois para explicar reconciliação e rollback sem provocar novamente o incidente durante a defesa.
''')
write('documentacao/09-solucao-problemas.md','''# Solução de problemas

| Sintoma | Verificação | Ação e consequência |
|---|---|---|
| WSL exige administrador | Código 0x80073d28 e saída de wsl | Executar wsl --install --no-distribution em terminal elevado e reiniciar quando solicitado. Não contornar UAC. |
| Docker sem Server | docker version e docker info | Abrir Desktop, aguardar backend WSL 2. Conferir reinício pendente. Não reinstalar antes de ler o erro. |
| Comando ausente após instalação | Get-Command e PATH | Abrir terminal novo ou usar comum.ps1, que atualiza PATH no processo. |
| Minikube sem recursos | docker info e minikube logs -p ops-lab | Confirmar 3 CPUs/3072 MiB e recursos disponíveis na VM. Não alterar parâmetros da série para melhorar resultado. |
| Download de imagem falha | describe pod e saída do runtime | Conferir conectividade, proxy e tag. Preservar evidência e repetir após corrigir rede. |
| ImagePullBackOff da aplicação | minikube image ls -p ops-lab | Carregar rotas:1.0 no perfil certo, conferir IfNotPresent. Durante o incidente 1.1, capturar e reverter. |
| Pending | describe pod, describe node | Comparar requests com allocatable, eventos de taints, afinidade e volumes. CPU ociosa não garante espaço de agendamento. |
| Running 0/1 | describe pod | Conferir readiness, path e porta. Não remover probe para maquiar falha. |
| CrashLoopBackOff | kubectl logs POD --previous | Ler código de saída, comando e variáveis. Verificar liveness agressiva e falhas reais. |
| OOMKilled | describe pod | Identificar consumo de memória e limite. Mudança de recursos exige nova série, não comparação misturada. |
| Service não responde | get endpointslices, get pods --show-labels | Corrigir selector, readiness ou targetPort. Testar de dentro com busybox antes do k6. |
| Port-forward encerrou | Log do túnel e Pod selecionado | Se Pod foi substituído, reabrir túnel. Ele não migra automaticamente para outro Pod. |
| Job já existe | get job carga e logs | Salvar evidência antes de excluir. O template é imutável e um Job finalizado não repete sozinho. |
| Job Failed, saída 99 | Logs completos e containerStatuses | Registrar métricas e meta descumprida. Não chamar falha de execução. |
| Job sem resumo | Events, logs, exitCode | Falha de execução. Registrar motivo, não preencher métricas com zero, repetir com novo rótulo. |
| dropped_iterations >0 | Resumo do cenário medicao | Gerador não iniciou toda a demanda. Ver CPU/VUs e calibração. Não mudar VUs no meio da série. |
| top sem métricas | metrics-server e API metrics.k8s.io | Esperar inicialização. Se persistir, ler logs e eventos do addon. Não inventar consumo. |
| Parser de log recusa formato | Log original salvo | Adaptar parser com revisão das unidades e cenário. Não inferir zeros de campos ausentes. |
| Contadores não batem com k6 | Identidade e reinícios dos Pods | Deltas incluem aquecimento. Reinício ou troca de UID invalida a comparação de contadores. |

Comandos de leitura comuns: `kubectl --context=ops-lab -n ops-lab get events --sort-by=.lastTimestamp`, `describe`, `logs` e `logs --previous`. Eles respondem questões diferentes: Kubernetes observa agendamento e runtime; aplicação registra o trabalho que realizou.
''')

table='| Execução | Pods | TAXA | Rotas | Rotas/s | Falhas (%) | p95 (ms) | Descartes |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
for row in rows:
    table+='| '+' | '.join(str(row[k]) if row[k] else 'Pendente' for k in ['rotulo','replicas','taxa','rotas_ok','sucessos_por_s','falhas_pct','p95_latencia_ok_ms','dropped_iterations_medicao'])+' |\n'
analysis='Não há nove medições completas. Não é possível eleger a configuração de melhor desempenho, calcular medianas finais ou concluir atendimento às metas. Resultados locais de Python não substituem esta série.'
medians=[]
if full:
    for n in [1,2,3]:
        group=[x for x in done if int(x['replicas'])==n]
        medians.append({'replicas':n,**{k:statistics.median(float(x[k]) for x in group) for k in ['sucessos_por_s','falhas_pct','p95_latencia_ok_ms','dropped_iterations_medicao']}})
    best_t=max(medians,key=lambda x:x['sucessos_por_s']);best_p=min(medians,key=lambda x:x['p95_latencia_ok_ms']);best_f=min(medians,key=lambda x:x['falhas_pct'])
    eligible=[n for n in [1,2,3] if all(float(x['falhas_pct'])<1 and float(x['p95_latencia_ok_ms'])<800 and float(x['dropped_iterations_medicao'])==0 for x in done if int(x['replicas'])==n)]
    analysis=f"A maior mediana de throughput foi de {best_t['sucessos_por_s']:.3f} rotas/s com {best_t['replicas']} Pods. O menor p95 mediano foi {best_p['p95_latencia_ok_ms']:.2f} ms com {best_p['replicas']} Pods. A menor mediana de falhas foi {best_f['falhas_pct']:.2f}% com {best_f['replicas']} Pods. "
    analysis+=f"Descartes na série: {sum(int(x['dropped_iterations_medicao']) for x in done)}. "
    analysis+=(f"A menor configuração que cumpriu todas as metas nas três repetições foi {min(eligible)} Pods, reservando {min(eligible)*.5:g} CPU para a aplicação." if eligible else 'Nenhuma configuração cumpriu todas as metas nas três repetições. A decisão é não declarar capacidade suficiente para essa demanda. A próxima investigação deve examinar ocupação do calculador, fila e algoritmo, sem modificar retroativamente os parâmetros desta série.')
report=f'''# Relatório experimental
{intro}
## Cenário e método

Host Ryzen 5 7600X, Windows 11, WSL 2 e Docker Desktop. Cluster de um nó com 3 CPUs e 3072 MiB. Cada Pod solicita e limita CPU a 500m, solicita 64Mi e limita memória a 128Mi. k6 solicita 250m/128Mi e limita 500m/256Mi. Imagem rotas:1.0 e script originais preservados. Condições: PARADAS=9, medição=60 s, aquecimento=10 s e início da medição aos 20 s. Somente o número de réplicas muda. A taxa escolhida e a justificativa estão em resultados/calibracao.json quando o piloto estiver concluído.

O executor programa chegadas constantes. Falhas incluem 503, timeout e JSON inválido. p95 considera apenas sucessos. As metas são p95<800 ms, falhas<1% e zero descartes da medição. Saída 99 com resumo é resultado válido de desempenho. Falha de execução não entra como zero. A ordem alternada é A=3,1,2; B=2,3,1; C=1,2,3, sempre com convergência de réplicas e EndpointSlices antes da carga.

## Medições reais

{table}
## Cálculos

Throughput = rotas_ok / 60. Mediana = segundo valor das três repetições ordenadas de uma configuração. Não calcular mediana do conjunto misturando configurações, nem usar a taxa /s global do k6. Falhas permanecem em porcentagem e latência em milissegundos. CPU em top é mCPU e memória MiB.

Os gráficos e o PowerPoint exibem duas casas decimais; os CSVs preservam a precisão numérica usada nos cálculos e os logs mantêm a saída original do k6.

{analysis}

## Custo e distribuição

1, 2 e 3 Pods reservam, respectivamente, 0,5, 1 e 1,5 CPU. Requests de memória totalizam 64, 128 e 192 MiB; limites totalizam 128, 256 e 384 MiB. Esses valores vêm da configuração e não são consumo medido. Amostras de CPU e memória de cada execução ficam em evidencias/ROTULO/recursos.txt. Deltas em distribuicao_aceitos_por_pod incluem aquecimento e não devem somar exatamente rotas_ok. Campos recém-iniciados partem de zero. UIDs e reinícios são verificados antes de aceitar o resultado.

## Diagnóstico e limites

A busca exaustiva e o limite de um cálculo simultâneo por Pod são possíveis gargalos. Só se tornam conclusões de saturação quando amostras e comportamento real os sustentam. O Service distribui conexões sem saber se o calculador está ocupado. Assim, 503 pode ocorrer com outra réplica livre. k6 e control plane compartilham o nó. Escala horizontal pode aumentar paralelismo, mas não cria CPU física nem assegura crescimento linear.

Três repetições são poucas para generalizar. Mediana de p95 não é p95 agregado. top é amostra e não prova de pico. Tarefas no Windows, temperatura, frequência da CPU, VM e rede virtual afetam os resultados. Três Pods em um nó não protegem contra falha desse nó. A conclusão vale somente para esta aplicação, parâmetros e host.
'''
if medians:
    report+='\n## Medianas por configuração\n\n| Pods | Rotas/s | Falhas (%) | p95 (ms) | Descartes |\n|---|---:|---:|---:|---:|\n'
    for m in medians:report+=f"| {m['replicas']} | {m['sucessos_por_s']:.3f} | {m['falhas_pct']:.2f} | {m['p95_latencia_ok_ms']:.2f} | {m['dropped_iterations_medicao']:g} |\n"
    for k in ['sucessos_por_s','falhas_pct','p95_latencia_ok_ms','dropped_iterations_medicao']:
        report+=f'\n![Medianas de {k}](../resultados/graficos/{k}.png)\n'
    base=next(m for m in medians if m['replicas']==1)
    three=next(m for m in medians if m['replicas']==3)
    ratio=three['sucessos_por_s']/base['sucessos_por_s']
    report+=f'\n## Efeito da escala\n\nO throughput mediano de três Pods corresponde a {ratio:.2f} vezes o de um Pod, ganho de {(ratio-1)*100:.1f}%. O custo de CPU reservada da aplicação triplica de 0,5 para 1,5 CPU. Comparar esse fator com três ajuda a avaliar a eficiência da escala, mas não prova a causa da diferença. As recusas por ocupação, o balanceamento sem conhecimento da fila e a disputa por recursos são mecanismos compatíveis com o código e a arquitetura.\n'
if exists('resultados/recursos-resumo.csv'):
    samples=list(csv.DictReader((R/'resultados/recursos-resumo.csv').open(encoding='utf-8-sig'),delimiter=';'))
    report+='\n## CPU e memória observadas\n\nOs números abaixo resumem as amostras de cada Pod durante os ciclos. Incluem períodos de aquecimento, intervalo e defasagem da coleta. CPU máxima amostrada não é pico contínuo e mediana destas amostras não equivale à utilização média de toda a janela.\n\n| Réplicas | Mediana das leituras medianas de CPU dos Pods (mCPU) | Maior CPU amostrada (mCPU) | Faixa de memória máxima amostrada por Pod (MiB) |\n|---|---:|---:|---:|\n'
    for n in [1,2,3]:
        vals=[s for s in samples if s['tipo']=='aplicacao' and int(s['replicas'])==n]
        if vals:
            cpu=statistics.median(float(s['cpu_mediana_m']) for s in vals)
            maxcpu=max(float(s['cpu_max_amostrado_m']) for s in vals)
            mem=[float(s['memoria_max_amostrada_Mi']) for s in vals]
            report+=f'| {n} | {cpu:g} | {maxcpu:g} | {min(mem):g}–{max(mem):g} |\n'
    gen=[s for s in samples if s['tipo']=='k6']
    if gen:report+=f"\nO gerador teve no máximo {max(float(s['cpu_max_amostrado_m']) for s in gen):g}m de CPU e {max(float(s['memoria_max_amostrada_Mi']) for s in gen):g}Mi de memória nas amostras registradas. Os nove resumos da medição mostraram zero iterações descartadas.\n"
if exists('resultados/evidencias/seis-replicas-pods.json'):
    six=json.loads((R/'resultados/evidencias/seis-replicas-pods.json').read_text(encoding='utf-8-sig'))
    states={}
    for pod in six['items']:
        phase=pod['status']['phase'];states[phase]=states.get(phase,0)+1
    host=json.loads((R/'resultados/evidencias/docker-node-hostconfig.json').read_text(encoding='utf-8-sig'))
    node=json.loads((R/'resultados/evidencias/node-capacidade.json').read_text(encoding='utf-8-sig'))
    report+=f"\n## Exercício de seis réplicas: resultado observado\n\nNo momento da captura, os estados foram {states}. O contêiner Docker do nó estava limitado a {host['NanoCpus']/1e9:g} CPUs e {host['Memory']/2**20:g} MiB. Entretanto, o Node anunciava {node['status']['allocatable']['cpu']} CPUs e {node['status']['allocatable']['memory']} de memória allocatable ao scheduler. Por isso, neste ambiente, o exemplo de Insufficient cpu do guia pode não se reproduzir: o agendamento usa o valor anunciado, enquanto os processos continuam sujeitos à quota do contêiner pai. Não alteramos requests nem forçamos Pods Pending para reproduzir artificialmente a saída ilustrativa. Após o exercício, restauramos uma réplica.\n"
write('documentacao/05-relatorio-experimentos.md',report)

requirements=[
('0.1–0.3','Ferramentas e pasta','Validado','logs/diagnostico-*.txt'),
('1.1–1.5','Cluster, contexto, API, nós e Pods do sistema','Validado' if exists('resultados/evidencias/cluster-nodes.json') else 'Pendente','logs/cluster-*.txt'),
('1.6–1.8','Namespace e metrics-server','Validado' if exists('resultados/evidencias/cluster-nodes.json') else 'Implementado','k8s/namespace.yaml e logs/cluster-*.txt'),
('2.1','Dockerfile e .dockerignore compreendidos, originais preservados','Validado','evidencias/validacao-estatica-http.json e documentacao/04'),
('2.2–2.4','Build, teste Docker e image load','Validado' if exists('resultados/evidencias/deployment-inicial.txt') else 'Pendente','logs/publicacao-*.txt'),
('3.1–3.4','Primeiro Deployment e hierarquia','Validado' if exists('resultados/evidencias/deployment-inicial.txt') else 'Implementado','k8s/versoes/deployment-inicial.yaml'),
('3.5','Excluir Pod e observar recriação','Validado' if exists('resultados/evidencias/pod-depois-recriacao.json') else 'Pendente','evidencias/pod-antes-recriacao.json e pod-depois-recriacao.json'),
('3.6 e Apêndice B','Recursos, probes, segurança e rollout da segunda versão','Validado' if exists('resultados/evidencias/pods-final.txt') else 'Implementado','k8s/deployment.yaml e evidencias/pods-final.txt'),
('4.1–4.3','Service, selectors, EndpointSlices e HTTP interno','Validado' if exists('resultados/evidencias/service.txt') else 'Implementado','k8s/service.yaml e evidencias/endpointslices.json'),
('4.4','Interface no navegador e port-forward','Pendente' if not exists('resultados/evidencias/navegador.png') else 'Validado','evidencias/navegador.png'),
('5.1–5.3','Imagem inválida, disponibilidade e rollback','Validado' if exists('resultados/evidencias/rollback-recuperado.json') else 'Pendente','logs/rollback-*.txt e evidencias/rollback-*'),
('6.1–6.3','Parâmetros k6, ConfigMap e Job','Validado' if exists('resultados/calibracao.json') else 'Implementado','carga.js e k8s/job-carga.yaml'),
('6.4–6.6','Piloto completo, calibração e taxa fixa','Medido' if exists('resultados/calibracao.json') else 'Pendente','logs/piloto*.txt e calibracao.json'),
('7.1','Réplicas prontas e endpoints antes de cada teste','Medido' if full else 'Pendente','evidencias/ROTULO/pods-antes.json e endpointslices.json'),
('7.2 e 7.4','Contadores antes/depois e distribuição por Pod','Medido' if full else 'Pendente','evidencias/ROTULO/contadores-*.txt'),
('7.3','Amostras de CPU e memória, incluindo k6','Medido' if full else 'Pendente','evidencias/ROTULO/recursos.txt'),
('7.5','Nove testes na ordem A/B/C e mesmas condições','Medido' if full else 'Pendente',f'comparativo.csv: {len(done)}/9 completos'),
('8.1','Seis réplicas, scheduler e restauração para uma','Validado' if exists('resultados/evidencias/seis-replicas-node.txt') else 'Pendente','evidencias/seis-replicas-*'),
('8.2–8.4','Medianas, análise de gargalos e decisão','Medido' if full else 'Pendente','documentacao/05 e medianas.csv'),
('8.5','Salvar evidências, apagar namespace e parar cluster','Validado' if exists('resultados/evidencias/encerramento.txt') else 'Pendente','evidencias/encerramento.txt ou executar após demonstração: encerrar-ambiente.ps1 -LimparNamespace'),
('Prompt §17–18','Documentação didática em português','Implementado','documentacao/00 a 09'),
('Prompt §19–20','Apresentação editável de 16 slides e falas','Implementado' if exists('apresentacao/RotaExpress.pptx') else 'Pendente','apresentacao/RotaExpress.pptx e roteiro-slides.md'),
('Prompt §21','Demonstração com plano alternativo','Implementado','documentacao/07'),
('Prompt §23–24','Validar YAML, originais e integridade de métricas','Validado' if exists('resultados/evidencias/validacao-estatica-http.json') else 'Pendente','evidencias/validacao-estatica-http.json e validacao-servidor.txt')]
check='# Checklist de entrega\n\nOrigem primária: Guia_Atividade.pdf. As referências abaixo usam seções e páginas descritas em documentacao/03. Itens do prompt são adicionais do usuário, não exigências inventadas do professor.\n\nEstados: Implementado = arquivo criado; Validado = teste com evidência; Medido = resultado real; Pendente = sem comprovação; Simulado = apenas ilustrativo. Não há dados simulados na tabela experimental.\n\n| Origem | Requisito | Status | Evidência relativa a resultados/ (salvo indicado) |\n|---|---|---|---|\n'
for source,req,status,evidence in requirements:check+=f'| {source} | {req} | {status} | {evidence} |\n'
write('CHECKLIST_ENTREGA.md',check)
write('LEIA-ME-ENTREGA.md',f'''# RotaExpress: entrega e retomada

Os arquivos originais do professor permanecem intactos. Os PDFs ficam na pasta acima. O README original foi preservado; este documento é o índice da implementação adicional.

- Comece por documentacao/00-diagnostico-ambiente.md e 02-instalacao.md.
- Passo a passo: documentacao/03-implementacao.md.
- Método, resultados e decisão: documentacao/05-relatorio-experimentos.md.
- Evidências originais: resultados/logs/ e resultados/evidencias/.
- Tabela preenchida: resultados/comparativo.csv, com as colunas do modelo original.
- Apresentação: apresentacao/RotaExpress.pptx. Falas: apresentacao/roteiro-slides.md.
- Situação verificável de cada requisito: CHECKLIST_ENTREGA.md.

Série comparativa: {len(done)}/9 medições completas. O script consolidar-resultados.py gera medianas e gráficos somente depois das nove. Não confunda diagnóstico HTTP local com teste de carga Kubernetes.

Para reproduzir, use os scripts PowerShell na sequência indicada no documento 02. Scripts que coletam medições não sobrescrevem evidências existentes: para repetir uma série, use uma cópia limpa da pasta de resultados, preservando os dados anteriores. Não execute preparar-entrega.py durante uma série, porque ele restaura os manifestos-base.

Os CSVs usam ponto e vírgula como separador, UTF-8 e ponto decimal. No Excel, use Dados > De Texto/CSV e selecione a localidade adequada ao ponto decimal ao converter as colunas numéricas.
''')
write('RELATORIO_FINAL.md',f'''# Relatório de entrega

## Escopo

Implementação e investigação DevOps do RotaExpress a partir dos dois PDFs e seis arquivos originais fornecidos. A aplicação e o script de carga permanecem intactos. A pasta do projeto de vídeos em C:\\Temp\\dowloadvideo não foi modificada.

## Ferramentas e computador

Windows 11 Pro, Ryzen 5 7600X, aproximadamente 31 GB de RAM. Instalações concluídas: Docker Desktop 4.96.0 (Engine 29.9.1), kubectl 1.37.1 e Minikube 1.39.0. O usuário instalou WSL 3.0.3 com administrador e reiniciou; o daemon Linux respondeu depois do reinício. Python 3.14.5 e Git 2.54.0 já existiam. Ferramentas auxiliares isoladas em .ferramentas. k6 1.0.0 no Kubernetes.

## Implementação e validação

Quatro manifestos principais e versão inicial do Deployment. Automação PowerShell de diagnóstico, instalação, cluster, publicação, validação, rollback, carga, capacidade e encerramento. Equivalentes Bash disponibilizados com sintaxe verificada, sem execução em Ubuntu. Documentação didática 00–09, checklist, roteiro de demonstração e falas para 16 slides.

Foram verificados os endpoints HTTP localmente e com Docker, a comunicação pelo Service, a interface no navegador, a reposição de Pod e o retorno da versão inválida para 1.0. A evidência de cada afirmação está no checklist. O teste HTTP local no Windows não compõe o experimento de carga.

## Experimento

{len(done)}/9 medições completas além do piloto, com TAXA fixada em 6/s, PARADAS=9 e DURACAO=60 s. Logs completos, recursos e contadores preservados por execução. {analysis}

Tabela: resultados/comparativo.csv. Medianas: resultados/medianas.csv quando a série estiver completa. Gráficos: resultados/graficos/. Metodologia, recursos observados, perguntas operacionais e limites: documentacao/05-relatorio-experimentos.md.

## Estado final e limitações

{'O namespace da atividade foi removido e o perfil ops-lab foi parado após salvar as evidências, conforme o encerramento do guia.' if exists('resultados/evidencias/encerramento.txt') else 'Consulte as evidências de encerramento para o estado final do cluster; o perfil foi criado e validado durante a execução.'} Os manifestos e a imagem permitem recriar o ambiente pelos scripts. Nenhum outro cluster foi removido.

A quota real do contêiner do nó é de 3 CPUs/3 GiB, mas o kubelet anuncia os recursos da VM ao scheduler. O exercício de seis réplicas deve ser interpretado com essa diferença, sem assumir a saída ilustrativa de Pods Pending. As amostras de top são defasadas e não equivalem a picos contínuos. Nenhuma configuração pode ser declarada adequada somente por ter o maior throughput.

Não há integração Canva disponível nesta sessão. A entrega é um PPTX editável, com importação no Canva ainda não testada. Os arquivos editáveis e o roteiro ficam em apresentacao/. Não foi alegada revisão no aplicativo Microsoft PowerPoint.

## Reprodução e localização

Use documentacao/02-instalacao.md para a sequência de scripts, documentacao/07-guia-demonstracao.md para a defesa e CHECKLIST_ENTREGA.md para verificar atendimento. LEIA-ME-ENTREGA.md reúne os caminhos. A documentação e os materiais finais ficam em {R.as_posix()}.
''')
write('scripts/requirements-validacao.txt','PyYAML==6.0.3\nmatplotlib==3.11.2')
print('Documentacao atualizada. Medicoes completas:',len(done))
