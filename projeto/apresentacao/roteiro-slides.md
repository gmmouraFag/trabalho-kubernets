# Roteiro de apresentação

Tempo sugerido: 16 a 20 minutos de fala, mais 5 a 7 minutos de demonstração. Fontes nas notas de cada slide.

## Slide 1: RotaExpress

Objetivo: Delimitar o problema e o alcance do trabalho.

Conceitos: Publicação, recuperação e escala de uma aplicação de rotas

Fala sugerida: Nosso trabalho investiga a operação de uma aplicação pronta. Publicamos o mesmo pacote no Kubernetes, verificamos a recuperação de falhas e comparamos quantas rotas são atendidas com uma, duas e três cópias. Os resultados representam este computador e esta demanda, não uma promessa universal de escalabilidade.

Elementos visuais: A tipografia destaca o nome do projeto e o subtítulo delimita o tema.

Tempo: 45 segundos.

Transição: a seguir, o problema da transportadora.

Pergunta possível: O que o grupo implementou?

Resposta: Infraestrutura declarativa, automação, evidências e experimento controlado. A aplicação original foi preservada.

Fonte: Guia, p. 1

## Slide 2: O problema da transportadora

Objetivo: Relacionar concorrência aos HTTP 503 do protótipo.

Conceitos: Pedidos simultâneos podem receber HTTP 503. O serviço busca a menor rota entre nove entregas fictícias.

Fala sugerida: A aplicação procura o menor circuito por força bruta. Com nove entregas, avalia 362.880 ordens. Cada processo tem um semáforo que permite um único cálculo. Se outro pedido chega enquanto está ocupado, ele recebe 503 imediatamente, sem fila. A interface desenha distâncias em linha reta entre pontos fictícios, sem trânsito ou ruas.

Elementos visuais: A captura real mostra o circuito, a distância e o Pod. O texto ao lado explica por que uma requisição concorrente pode falhar.

Tempo: 75 segundos.

Transição: a seguir, objetivos do experimento.

Pergunta possível: 503 significa que o processo caiu?

Resposta: Não. Neste código, é uma recusa explícita porque o calculador está ocupado.

Fonte: Guia, p. 3. app.py original.

## Slide 3: Objetivos do experimento

Objetivo: Apresentar a pergunta e os controles do experimento.

Conceitos: Objetivos do experimento

Fala sugerida: A pergunta central é o efeito do número de Pods sobre throughput, latência, falhas e recursos. Para responder, precisamos primeiro provar que a publicação funciona. Depois, mudamos somente réplicas e mantemos imagem, taxa, duração, recursos por Pod e script. O objetivo final é justificar uma decisão, inclusive reconhecer quando nenhuma configuração atende às metas.

Elementos visuais: As quatro linhas correspondem às entregas operacionais e experimentais.

Tempo: 75 segundos.

Transição: a seguir, tecnologias e responsabilidades.

Pergunta possível: Por que controlar as variáveis?

Resposta: Para atribuir diferenças observadas principalmente à quantidade de réplicas, reconhecendo ruído do host.

Fonte: Guia, pp. 1–3 e 28

## Slide 4: Tecnologias e responsabilidades

Objetivo: Distinguir o papel de cada ferramenta.

Conceitos: Tecnologias e responsabilidades

Fala sugerida: Docker empacota a aplicação e hospeda o nó. Minikube cria o cluster e configura o kubeconfig. kubectl envia pedidos à API Kubernetes. A aplicação usa Python 3.12 na imagem, embora o Python local usado para ferramentas seja 3.14. O k6 roda dentro do cluster, com versão fixa, para acessar o Service pelo caminho que distribui conexões.

Elementos visuais: A tabela associa cada tecnologia a uma responsabilidade específica, sem tratar Docker e Kubernetes como equivalentes.

Tempo: 75 segundos.

Transição: a seguir, arquitetura do laboratório.

Pergunta possível: Por que não instalar k6 no Windows?

Resposta: O guia exige execução interna e evita medir pelo port-forward, que escolhe um único Pod.

Fonte: Guia, pp. 4 e 8. Versões reais em documentacao/00.

## Slide 5: Arquitetura do laboratório

Objetivo: Explicar o caminho da configuração e do tráfego.

Conceitos: Arquitetura do laboratório

Fala sugerida: O Deployment mantém os Pods identificados por app=rotas. O Service oferece o nome estável rotas e porta 8000. EndpointSlices listam os destinos prontos. O Job monta o JavaScript vindo do ConfigMap e envia requisições ao Service. Todos esses objetos ficam no namespace ops-lab. O terminal administra a API e o navegador acessa um túnel separado para demonstração.

Elementos visuais: As conexões mostram o ConfigMap entregando o script ao Job, o Job enviando tráfego ao Service e o Deployment mantendo os três Pods.

Tempo: 75 segundos.

Transição: a seguir, ambiente e cluster.

Pergunta possível: O Service conhece o Pod menos ocupado?

Resposta: Não. A distribuição ocorre por conexão e não consulta o semáforo da aplicação.

Fonte: Guia, p. 2. Aula, pp. 29–32 e 42.

## Slide 6: Ambiente e cluster

Objetivo: Mostrar recursos reais e a diferença entre quota e capacidade anunciada.

Conceitos: Windows 11, Ryzen 5 7600X, WSL 2 e Docker Desktop. O scheduler anuncia recursos da VM: veja o diagnóstico de capacidade.

Fala sugerida: O host tem 12 processadores lógicos e cerca de 31 GB de RAM. O comando exigido limita o contêiner do Minikube a três CPUs e três GiB. Nesta versão, o kubelet informa ao scheduler a capacidade maior da VM, portanto quota do contêiner e capacidade anunciada não coincidem. Essa diferença é documentada e afeta a expectativa do exercício de seis réplicas. O nó ficou Ready e metrics-server foi habilitado.

Elementos visuais: Os números grandes são limites do contêiner do nó, não CPUs exclusivas. A nota esclarece a capacidade anunciada pelo kubelet.

Tempo: 75 segundos.

Transição: a seguir, a imagem docker.

Pergunta possível: 3 CPUs significa três núcleos exclusivos?

Resposta: Não. É quota do contêiner Docker. O host e a VM continuam compartilhando recursos.

Fonte: resultados/logs/cluster-*.txt e evidencias/docker-node-hostconfig.json

## Slide 7: A imagem Docker

Objetivo: Explicar como o pacote chega ao nó.

Conceitos: Build, testes HTTP fora do cluster e image load antes do Deployment

Fala sugerida: O Dockerfile define a base Python enxuta, copia somente a aplicação e usa usuário sem privilégios. EXPOSE é documentação da porta, não publicação. As variáveis de ambiente fazem logs imediatos e evitam gravação de bytecode. Primeiro construímos rotas:1.0, testamos os endpoints com Docker e encerramos o contêiner. Só então copiamos a imagem para o armazenamento separado do nó do Minikube.

Elementos visuais: O trecho do Dockerfile é resumido para explicar base, fonte, usuário e processo. O arquivo original contém também WORKDIR e ENV.

Tempo: 75 segundos.

Transição: a seguir, deployment, pods e service.

Pergunta possível: Por que image load?

Resposta: A imagem do Docker do host não está automaticamente disponível no runtime do nó.

Fonte: Dockerfile original. Guia, pp. 8–9.

## Slide 8: Deployment, Pods e Service

Objetivo: Demonstrar reconciliação e descoberta dos Pods.

Conceitos: O controlador repõe o Pod excluído. O Service mantém um endereço estável para os destinos prontos.

Fala sugerida: Aplicamos primeiro o Deployment mínimo de uma réplica. Observamos a hierarquia e excluímos o Pod. O ReplicaSet criou outro com novo UID e endereço. Depois aplicamos a segunda versão com recursos, probes e segurança, gerando uma atualização gradual. O Service usa selector app=rotas, igual às labels do template. Ele resolve a instabilidade dos endereços individuais.

Elementos visuais: A hierarquia mostra que Deployment mantém ReplicaSet e este mantém Pods. A descrição conecta isso à exclusão e reposição observadas.

Tempo: 75 segundos.

Transição: a seguir, recursos e verificações de saúde.

Pergunta possível: Um Pod criado sozinho seria reposto?

Resposta: Após exclusão, não. A reposição vem do controlador, aqui o ReplicaSet gerenciado pelo Deployment.

Fonte: Guia, pp. 10–16. evidencias/pod-antes-recriacao.json e pod-depois-recriacao.json

## Slide 9: Recursos e verificações de saúde

Objetivo: Justificar limites, probes e segurança do manifesto.

Conceitos: Recursos e verificações de saúde

Fala sugerida: Request orienta onde cabe o Pod. Limit restringe execução. CPU acima do teto sofre throttling e memória além do limite pode encerrar o processo. Readiness controla se o Service encaminha novas conexões, enquanto liveness pode reiniciar o contêiner após falhas repetidas. Essas verificações não indicam que o calculador está livre: ele pode responder saúde e recusar cálculo por ocupação. A aplicação aceita a raiz somente leitura porque não grava dados.

Elementos visuais: As linhas da tabela separam agendamento, teto, prontidão, reinício e restrições de segurança.

Tempo: 75 segundos.

Transição: a seguir, falha controlada e rollback.

Pergunta possível: Qual é a classe QoS?

Resposta: Burstable, pois request e limit de memória diferem.

Fonte: Guia, pp. 12–13 e 30. k8s/deployment.yaml.

## Slide 10: Falha controlada e rollback

Objetivo: Explicar a proteção da disponibilidade e a reversão.

Conceitos: O Pod antigo continua atendendo enquanto o novo não fica pronto

Fala sugerida: Alteramos a imagem para uma tag indisponível. O rollout expirou e os eventos mostraram falha de pull. Com uma réplica, a estratégia padrão arredonda maxUnavailable para zero e permite um Pod extra. Assim, o Pod anterior permaneceu pronto e respondeu ao teste interno. O rollout undo restaurou o template funcional. A comprovação inclui eventos, status e HTTP, não apenas o comando de undo.

Elementos visuais: As três etapas mostram a tag ausente, o rollout incompleto e o retorno à versão 1.0. O Pod antigo protege o serviço.

Tempo: 75 segundos.

Transição: a seguir, metodologia de carga.

Pergunta possível: O rollback desfaz banco de dados?

Resposta: Não. Ele restaura o template do Deployment e não reverte migrações ou estado externo.

Fonte: Guia, pp. 17–18. resultados/logs/rollback-*.txt.

## Slide 11: Metodologia de carga

Objetivo: Explicar o período medido e os thresholds.

Conceitos: Metodologia de carga

Fala sugerida: Executamos k6 como Job e acessamos http://rotas:8000. A taxa fixada na calibração é 6 pedidos por segundo. O aquecimento ocupa os primeiros dez segundos. A medição começa aos vinte e dura sessenta. O executor de chegadas constantes tenta manter a demanda independentemente da resposta. A cada requisição, abre conexão nova. p95 é só de sucessos e as metas são p95 abaixo de 800 ms, falhas abaixo de um por cento e nenhum descarte da medição.

Elementos visuais: A tabela temporal separa aquecimento, intervalo e janela medida. A linha inferior fixa demanda e metas.

Tempo: 75 segundos.

Transição: a seguir, comparação de 1, 2 e 3 pods.

Pergunta possível: Job Failed invalida a medição?

Resposta: Saída 99 com resumo completo indica thresholds não cumpridos e é resultado. Sem resumo é falha de execução.

Fonte: Guia, pp. 19–23. carga.js e resultados/calibracao.json.

## Slide 12: Comparação de 1, 2 e 3 Pods

Objetivo: Mostrar repetição e ordem alternada das configurações.

Conceitos: 9/9 medições completas. Mesma imagem, taxa, duração e recursos por Pod.

Fala sugerida: A ordem alternada reduz a chance de medir sempre a mesma configuração com o computador mais quente ou ocupado. Antes de cada teste, esperamos o Deployment e contamos endpoints prontos. Coletamos contadores antes e depois, logs completos e amostras de CPU e memória a cada quinze segundos. O throughput vem de rotas_ok dividido por sessenta. Os deltas dos Pods incluem o aquecimento e não precisam somar o total medido do k6.

Elementos visuais: Leia as linhas A, B e C na horizontal. A alternância impede que uma configuração seja sempre a primeira.

Tempo: 75 segundos.

Transição: a seguir, resultados das medições.

Pergunta possível: Por que não usar o /s mostrado pelo k6?

Resposta: Ele divide pelo tempo total, incluindo períodos fora da janela própria de medição.

Fonte: Guia, pp. 24–25. resultados/comparativo.csv.

## Slide 13: Resultados das medições

Objetivo: Comparar resultados sem ocultar falhas.

Conceitos: Mediana de três repetições por configuração. p95 somente dos sucessos.

Fala sugerida: Os gráficos apresentam apenas valores medidos. Cada coluna corresponde à mediana das três execuções da mesma configuração. Compare throughput e p95 junto com a taxa de falhas. p95 baixo, isoladamente, pode coexistir com muitas recusas. A mediana de três p95 é um resumo das execuções, e não o percentil calculado sobre todas as respostas reunidas.

Elementos visuais: O gráfico esquerdo mostra throughput em rotas/s. O direito mostra p95 em ms. As falhas medianas aparecem abaixo e precisam ser consideradas junto com as colunas.

Tempo: 75 segundos.

Transição: a seguir, diagnóstico e gargalos.

Pergunta possível: A mediana prova significância estatística?

Resposta: Não. Com três repetições, a análise é descritiva e restrita ao ambiente.

Fonte: resultados/comparativo.csv, medianas.csv e logs originais.

## Slide 14: Diagnóstico e gargalos

Objetivo: Separar observação de hipótese de gargalo.

Conceitos: Diagnóstico e gargalos

Fala sugerida: A aplicação pode recusar uma conexão mesmo havendo outra réplica livre, pois o Service não consulta a ocupação. A meia CPU de cada Pod pode aumentar a duração do cálculo por throttling. O gerador também disputa recursos do nó. No exercício de seis réplicas, comparamos o comportamento observado à capacidade anunciada e à quota real. Saturação de CPU é inferida com apoio das amostras, que não são rastreamento contínuo. Fila, algoritmo ou balanceamento informado seriam investigações futuras.

Elementos visuais: As quatro linhas identificam mecanismos que podem limitar o sistema. Diferencie o que está no código do que foi comprovado por métricas.

Tempo: 75 segundos.

Transição: a seguir, conclusão e decisão operacional.

Pergunta possível: Por que seis Pods podem rodar neste ambiente?

Resposta: O scheduler usa allocatable anunciado pela VM, maior que a quota Docker de três CPUs. Não se deve inventar Pending.

Fonte: app.py, amostras de recursos e evidencias/seis-replicas-*.

## Slide 15: Conclusão e decisão operacional

Objetivo: Justificar a decisão para a demanda medida.

Conceitos: Custo reservado: 0,5 CPU por Pod. A decisão deve considerar falhas, p95, descartes e limites do nó.

Fala sugerida: Nenhuma configuração cumpre todas as metas. Escolhemos a menor configuração que cumpra as metas em todas as repetições; se nenhuma cumprir, registramos insuficiência neste cenário e investigamos o desenho da aplicação. Acrescentar réplicas aumenta CPU reservada e paralelismo, mas não garante escala linear. Todas as réplicas estão no mesmo nó, portanto nenhuma comparação demonstra proteção contra a queda do nó.

Elementos visuais: A frase central expressa atendimento ou não das metas. O texto inferior explicita o custo de 0,5 CPU por Pod.

Tempo: 75 segundos.

Transição: a seguir, demonstração do sistema.

Pergunta possível: A maior taxa de sucesso sempre justifica mais Pods?

Resposta: É preciso avaliar metas e custo. Melhor throughput com falhas excessivas ainda pode ser inadequado.

Fonte: documentacao/05-relatorio-experimentos.md e resultados/medianas.csv.

## Slide 16: Demonstração do sistema

Objetivo: Guiar a demonstração com alternativa de evidências salvas.

Conceitos: Interface, cálculo, logs, escala e evidências dos testes

Fala sugerida: Na demonstração, mostramos cluster e namespace, o Deployment, os Pods e o Service. Abrimos a interface, calculamos uma rota e identificamos quem atendeu. Em seguida mostramos logs, alteramos réplicas e conferimos endpoints. Terminamos com a tabela, os gráficos e os logs reais do k6. Se houver falha ao vivo, usamos evidências salvas e explicamos que representam a execução anterior. Depois encerramos o namespace e paramos o perfil conforme o guia.

Elementos visuais: Os comandos mostram inspeção de objetos e o túnel local. Na demonstração, use também os comandos completos do guia 07.

Tempo: 75 segundos.

Transição: a seguir, perguntas do professor.

Pergunta possível: Como reproduzir?

Resposta: A sequência de scripts e os comandos estão no documento 02 e no guia de demonstração. Os arquivos originais e evidências permanecem disponíveis.

Fonte: documentacao/07-guia-demonstracao.md.

