# Implementação passo a passo

Atualizado em 21/10/2026. Fonte principal: Guia_Atividade.pdf, na pasta acima. Fundamentação: Aula_Kubernetes.pdf.

Os comandos abaixo pressupõem contexto ops-lab e namespace ops-lab. Os scripts passam ambos explicitamente para reduzir enganos. O resultado esperado nunca substitui a evidência observada.

## Grupo 0: Ferramentas

**Origem:** Guia, pp. 4.

**Objetivo e conceito:** Separar falhas de instalação das falhas da aplicação.

```powershell
docker version
kubectl version --client
minikube version
python --version
```

**Significado e ordem:** Cada version verifica o executável. Docker também consulta o servidor, que deve responder. Python local apoia a validação, mas o runtime do contêiner continua 3.12.

**Resultado esperado / critério para avançar:** Três ferramentas operacionais e terminal na pasta projeto.

**Resultado observado:** Docker Desktop 4.96.0 e Engine 29.9.1, kubectl 1.37.1 e Minikube 1.39.0 responderam após o reinício. O daemon Linux ficou acessível. Python 3.14.5 e Git 2.54.0 já estavam presentes.

**Arquivos e evidência:** resultados/logs/diagnostico-*.txt. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 1: Cluster e contexto

**Origem:** Guia, pp. 5–7.

**Objetivo e conceito:** Criar a infraestrutura e confirmar o alvo antes das alterações.

```powershell
minikube start -p ops-lab --driver=docker --cpus=3 --memory=3072
minikube profile ops-lab
kubectl config get-contexts
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
kubectl get pods -A
kubectl apply -f k8s/namespace.yaml
kubectl get namespaces
kubectl config set-context --current --namespace=ops-lab
minikube addons enable metrics-server
```

**Significado e ordem:** start cria o nó com recursos fixos. profile escolhe o perfil. config confirma cluster e namespace. cluster-info valida API. nodes mostra Ready. pods -A revela o control plane. apply cria namespace. metrics-server alimenta top.

**Resultado esperado / critério para avançar:** Nó Ready, contexto ops-lab e namespace ops-lab.

**Resultado observado:** Perfil ops-lab criado com Kubernetes 1.37.0 e containerd 2.3.4. O nó passou de NotReady inicial para Ready; namespace ops-lab Active e metrics-server habilitado.

**Arquivos e evidência:** resultados/logs/cluster-*.txt. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 2: Imagem Docker

**Origem:** Guia, pp. 8–9.

**Objetivo e conceito:** Testar o pacote antes de adicionar Kubernetes ao diagnóstico.

```powershell
docker build -t rotas:1.0 .
docker image ls rotas
docker run -d --rm -p 127.0.0.1:8000:8000 --name rotas-teste rotas:1.0
curl.exe http://localhost:8000/healthz
curl.exe http://localhost:8000/readyz
curl.exe "http://localhost:8000/api/rota?paradas=9"
docker logs rotas-teste
docker stop rotas-teste
minikube image load rotas:1.0
minikube image ls
```

**Significado e ordem:** build empacota a fonte. run inicia o processo e publica a porta somente no loopback, refinamento opcional de exposição local. curl verifica HTTP e JSON. logs mostra aceitos. stop encerra apenas o contêiner de teste criado pelo script. image load copia ao nó, sem registry.

**Resultado esperado / critério para avançar:** HTTP 200 e rota válida; contêiner de teste parado; imagem disponível no nó.

**Resultado observado:** Imagem rotas:1.0 construída, quatro endpoints retornaram HTTP 200 no contêiner de teste. A rota de nove entregas teve distância 299,03 unidades. O contêiner de teste foi parado e a imagem apareceu no armazenamento do nó.

**Arquivos e evidência:** resultados/logs/publicacao-*.txt. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 3: Deployment em duas versões

**Origem:** Guia, pp. 10–13 e 30.

**Objetivo e conceito:** Demonstrar reconciliação e depois uma atualização gradual com recursos e probes.

```powershell
kubectl apply -f k8s/versoes/deployment-inicial.yaml
kubectl rollout status deployment/rotas
kubectl get deployment,replicaset,pods
kubectl get pods -o wide --show-labels
kubectl describe pod -l app=rotas
kubectl logs deployment/rotas
kubectl delete pod -l app=rotas
kubectl get pods -o wide
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/rotas
kubectl rollout history deployment/rotas
kubectl get replicaset
```

**Significado e ordem:** apply registra o desejado; rollout aguarda o observado. Deployment mantém ReplicaSet, que repõe Pods. delete provoca recuperação com novo UID/IP. A versão final acrescenta probes, resources e securityContext. A estratégia RollingUpdate padrão do guia permanece: maxSurge e maxUnavailable de 25%, arredondados para 1 e 0 com uma réplica.

**Resultado esperado / critério para avançar:** Um Pod pronto, UID diferente após exclusão, histórico com duas revisões, QoS Burstable.

**Resultado observado:** A versão mínima subiu, o Pod excluído foi substituído e a segunda versão foi publicada. O histórico inicialmente mostrou revisões 1 e 2; probes, recursos e segurança aparecem no describe salvo.

**Arquivos e evidência:** resultados/evidencias/pod-antes-recriacao.json e pod-depois-recriacao.json. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 4: Service

**Origem:** Guia, pp. 14–16.

**Objetivo e conceito:** Oferecer DNS estável e validar a comunicação por dentro do cluster.

```powershell
kubectl apply -f k8s/service.yaml
kubectl get service rotas
kubectl get endpointslices -l kubernetes.io/service-name=rotas
kubectl get pods -o wide
kubectl run teste --rm -it --restart=Never --image=busybox:1.36 -- wget -qO- http://rotas:8000/healthz
kubectl port-forward service/rotas 8080:8000
```

**Significado e ordem:** Service seleciona app=rotas. EndpointSlices devem listar IPs prontos. O Pod busybox verifica DNS, porta e resposta dentro da rede. Port-forward abre inspeção local em um Pod escolhido, sem balanceamento.

**Resultado esperado / critério para avançar:** Destinos corretos, healthz ok de dentro e interface calculando no navegador.

**Resultado observado:** O teste interno recebeu JSON de saúde e rota válida. O navegador calculou nove entregas pelo túnel e a captura registra distância, tempo e Pod atendente.

**Arquivos e evidência:** resultados/evidencias/service.txt e endpointslices.json. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 5: Incidente e rollback

**Origem:** Guia, pp. 17–18.

**Objetivo e conceito:** Provocar falha de imagem e comprovar disponibilidade e recuperação.

```powershell
kubectl set image deployment/rotas rotas=rotas:1.1
kubectl rollout status deployment/rotas --timeout=60s
kubectl get pods
kubectl describe pod -l app=rotas
kubectl get events --sort-by=.lastTimestamp
kubectl rollout undo deployment/rotas
kubectl rollout status deployment/rotas
kubectl rollout history deployment/rotas
```

**Significado e ordem:** set image muda o template para tag ausente. O timeout é esperado, mas precisa ser acompanhado de eventos de pull e teste HTTP. O Pod antigo permanece devido à estratégia de atualização. undo restaura a revisão anterior sem reconstruir imagem.

**Resultado esperado / critério para avançar:** Falha diagnosticada, serviço atendendo durante a falha, apenas versão 1.0 pronta depois do undo.

**Resultado observado:** A tag 1.1 causou ErrImagePull/ImagePullBackOff e timeout do rollout. O teste interno respondeu pelo Pod 1.0 durante a falha. O undo concluiu e a captura recuperada referencia rotas:1.0.

**Arquivos e evidência:** resultados/logs/rollback-*.txt e resultados/evidencias/rollback-*. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 6: k6 e calibração

**Origem:** Guia, pp. 19–23.

**Objetivo e conceito:** Escolher demanda informativa em teste piloto e fixar condições.

```powershell
kubectl create configmap carga-script --from-file=carga.js --dry-run=client -o yaml
kubectl apply -f k8s/job-carga.yaml
kubectl wait --for=condition=Ready pod -l job-name=carga --timeout=180s
kubectl logs -f job/carga
kubectl get job carga
kubectl logs job/carga > resultados/piloto.txt
kubectl delete job carga
```

**Significado e ordem:** ConfigMap monta carga.js em /scripts. Job usa grafana/k6:1.0.0, backoffLimit 0 e deadline 240 s. TAXA inicial 6 é ponto inicial do guia, não taxa final presumida. Calibrar com uma réplica: aumentar se quase tudo tem sucesso; reduzir se quase nenhum sucesso e descartes. Conservar falhas e sucessos informativos.

**Resultado esperado / critério para avançar:** Piloto completo salvo, justificativa e taxa fixadas antes da série.

**Resultado observado:** Piloto piloto: taxa 6/s, 120 rotas, 66.75% de falhas, p95 436.19 ms e 0 descartes. A justificativa e os hashes estão em calibracao.json.

**Arquivos e evidência:** resultados/logs/piloto*.txt e resultados/calibracao.json. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 7: Nove medições

**Origem:** Guia, pp. 24–25.

**Objetivo e conceito:** Comparar somente réplicas, controlando ordem e estabilidade.

```powershell
kubectl scale deployment/rotas --replicas=3
kubectl rollout status deployment/rotas
kubectl get endpointslices -l kubernetes.io/service-name=rotas
kubectl logs -l app=rotas --prefix --tail=1
kubectl top pods
```

**Significado e ordem:** Repita o ciclo do Grupo 6 após convergência de Pods e endpoints. Leia contadores antes e depois, amostre CPU/memória a cada 15 s e guarde logs antes de excluir Job. Ordem A: 3,1,2; B: 2,3,1; C: 1,2,3. Sucessos/s=rotas_ok/60, não o /s do resumo total. Os deltas dos Pods incluem aquecimento.

**Resultado esperado / critério para avançar:** Nove logs completos, mesmos parâmetros, sem reinício/troca de Pods durante cada medição.

**Resultado observado:** 9 de nove medições completas registradas, com logs e objetos identificados por rodada. Consulte o relatório 05 para tabela, medianas e interpretação.

**Arquivos e evidência:** resultados/comparativo.csv e resultados/evidencias/<rotulo>/. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.

## Grupo 8: Capacidade e decisão

**Origem:** Guia, pp. 26–28.

**Objetivo e conceito:** Observar agendamento por requests e sustentar decisão em medianas.

```powershell
kubectl scale deployment/rotas --replicas=6
kubectl get pods
kubectl describe pod -l app=rotas
kubectl describe node ops-lab
kubectl get events --sort-by=.lastTimestamp
kubectl scale deployment/rotas --replicas=1
kubectl delete namespace ops-lab
minikube stop -p ops-lab
```

**Significado e ordem:** Seis Pods pedem 3 CPUs além do control plane. Insufficient cpu é limitação de requests, mesmo com CPU ociosa. Restaure uma réplica. Calcule mediana das três repetições por métrica. A limpeza final remove namespace após salvar as evidências e stop libera recursos preservando o perfil.

**Resultado esperado / critério para avançar:** Evidência de scheduler, estado restaurado, análise com decisão e custos; limpeza quando a demonstração terminar.

**Resultado observado:** Exercício de seis réplicas registrado; estado restaurado para uma. O relatório 05 descreve o agendamento real e a diferença entre quota Docker e allocatable. Namespace removido e perfil parado após preservar as evidências.

**Arquivos e evidência:** resultados/evidencias/seis-replicas-* e documentacao/05-relatorio-experimentos.md. Os manifestos citados ficam em k8s/ e a automação correspondente em scripts/.

**Problemas e soluções:** se o critério falhar, interrompa as etapas dependentes e use o documento 09. Salve o erro antes de corrigir.
