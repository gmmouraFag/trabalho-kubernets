# Perguntas e respostas

## Qual a diferença entre imagem e contêiner?

Imagem é o pacote de arquivos e metadados. Contêiner é o processo iniciado a partir dele. Vários contêineres podem usar a mesma imagem.

## Docker e Kubernetes fazem o mesmo trabalho?

Docker constrói e executa contêineres. Kubernetes coordena Pods, reconcilia réplicas e publica serviços. O driver Docker do Minikube hospeda o nó local.

## Por que um Deployment?

Ele mantém um template e coordena ReplicaSets. O ReplicaSet repõe Pods removidos. Um Pod avulso não seria recriado após exclusão.

## Namespace isola clientes com segurança?

Ele organiza nomes. Isolamento exige RBAC, NetworkPolicy, quotas e políticas de segurança, ou clusters separados conforme o risco.

## Qual a relação entre Service e labels?

O selector app=rotas encontra os Pods do template. Readiness decide quais destinos estão prontos. EndpointSlices materializam os endereços.

## Por que port-forward sempre mostra um Pod?

O túnel seleciona um Pod ao abrir. Ele não passa pelo balanceamento de conexões do Service. O k6 interno usa o caminho correto.

## Requests e limits são consumo real?

Request é necessidade declarada para agendamento. Limit é teto de execução. top mostra consumo amostrado. CPU no teto sofre throttling; memória além do teto pode levar a OOMKilled.

## Readiness reinicia o contêiner?

Não. Ela retira prontidão e impede novas conexões do Service. Liveness pode reiniciar. Neste protótipo healthz e readyz não testam disponibilidade do semáforo.

## Por que ConfigMap e Job?

ConfigMap separa script de imagem. Job representa uma tarefa que termina. Deployment representaria serviço contínuo e teria política de reinício inadequada para medição.

## Secret é criptografia?

Base64 é codificação. Proteção depende de acesso, criptografia em repouso e gestão de segredos. O projeto não exige dados secretos.

## Por que o k6 marca Failed?

Código 99 com resumo completo significa desempenho abaixo dos thresholds. Sem resumo, imagem inválida, deadline ou erro de script são falhas de execução e não medições zero.

## Como calcular throughput?

Dividir rotas_ok por 60 s da janela medida. O /s impresso no resumo usa duração total e não é o indicador solicitado.

## O que p95 descreve?

O percentil abaixo do qual ficam aproximadamente 95% dos tempos das respostas bem-sucedidas. Não descreve as recusas 503 nem garante qualidade para todos os clientes.

## Por que contar descartes?

Eles são iterações programadas que o gerador não iniciou. Se forem maiores que zero, a demanda efetivamente gerada difere da pretendida e a medição requer diagnóstico.

## Adicionar Pods elimina 503?

Não necessariamente. O Service não conhece ocupação. Uma conexão pode ir a um calculador ocupado mesmo com outro livre. CPU do nó, limite de cada Pod e algoritmo também restringem a escala.

## Por que seis réplicas ficam Pending?

Cada uma pede 500m. Seis já pedem 3 CPUs, sem incluir control plane. Scheduler compara requests com allocatable e registra Insufficient cpu se não couber.

## Rollback recupera tudo?

Ele restaura o template de uma revisão do Deployment. Não desfaz mudanças em bancos de dados, arquivos externos ou dependências.

## Por que três repetições e mediana?

A ordem alternada reduz viés de aquecimento e tarefas concorrentes. Mediana é o valor central, menos influenciado por uma observação extrema. Três repetições ainda são amostra pequena.

## Três Pods garantem alta disponibilidade?

Em um único nó, todos dependem da mesma máquina. O laboratório mostra distribuição de trabalho e recuperação de Pod, não tolerância à queda desse nó.

## Como usar HPA depois?

Definir requests, instalar fonte de métricas e configurar min/max e alvo de uso. Medir antes ajuda a escolher limites. HPA tem atraso de reação e não cria recursos físicos no nó.

## Por que comparar contadores antes e depois?

Eles são acumulados desde o início de cada Pod. O delta mostra distribuição durante o ciclo, incluindo aquecimento. Troca ou reinício de Pod invalida a subtração direta.

## Qual configuração escolher?

A menor que cumpra as metas para a demanda medida e com folga operacional. Se nenhuma cumprir, registrar isso e investigar fila, algoritmo, roteamento e CPU, sem mudar o experimento retroativamente.
