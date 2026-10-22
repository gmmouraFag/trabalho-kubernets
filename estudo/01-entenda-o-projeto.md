# Entenda o projeto inteiro

Leia na ordem. Ao terminar uma seção, explique a ideia sem olhar. Os números apresentados como resultados vêm dos arquivos medidos em `projeto/resultados/`; os exemplos de explicação não são novas medições.

## 1. Qual problema estamos investigando?

Uma transportadora precisa visitar entregas e voltar ao depósito pela menor distância. A aplicação recebida calcula uma rota para pontos fictícios, em linha reta. O problema operacional é descobrir o que acontece quando várias pessoas pedem cálculos ao mesmo tempo.

A pergunta do trabalho é: mantendo a mesma demanda, aumentar de um para dois e três Pods melhora quantas rotas são concluídas? Como ficam a demora, as falhas e o custo em recursos?

Desenvolver a aplicação e operá-la são trabalhos relacionados. Neste projeto, o código já foi fornecido. Nosso foco é empacotar, publicar, verificar, recuperar, medir e interpretar. Uma aplicação abrir no navegador não prova que aguenta vários usuários.

**Explique com suas palavras:** qual é a diferença entre “calcular a rota certa” e “conseguir atender os pedidos no horário de pico”?

## 2. O caminho de um pedido

Você clica em Calcular rota. O navegador faz uma requisição HTTP para `/api/rota?paradas=9`. A aplicação calcula, monta um JSON e devolve a resposta. O JavaScript da página usa os dados para desenhar o circuito.

| Termo | Significado neste projeto |
|---|---|
| Cliente | Quem pede o serviço: navegador ou k6 |
| Servidor | Processo que recebe e responde às requisições |
| API | Interface usada por um programa para pedir uma operação a outro |
| Endpoint | Um caminho disponível na API, como /api/rota |
| HTTP | Protocolo dos pedidos e das respostas |
| JSON | Formato de dados com campos como ordem, distancia e pod |
| Porta | Número que identifica o serviço de rede no ambiente, aqui 8000 |

`/` entrega a interface. `/healthz` informa saúde. `/readyz` informa prontidão. `/api/rota` calcula. Os códigos HTTP também contam uma história:

- 200: pedido atendido.
- 400: parâmetro inválido, como número de paradas fora do intervalo aceito.
- 404: caminho desconhecido.
- 503: neste código, o calculador está ocupado e recusou outro cálculo.

HTTP 503 neste experimento não significa necessariamente que o processo morreu. Ele pode continuar respondendo às verificações de saúde.

## 3. Por que o cálculo pesa?

`app.py` enumera as ordens possíveis de visita e escolhe a de menor distância. Para nove entregas, são 9! = 362.880 ordens. O símbolo ! significa fatorial: 9 × 8 × 7 × ... × 1.

Cada cálculo refaz esse trabalho. Não há cache guardando a resposta pronta. A carga é principalmente de CPU. Os pontos são pequenos e fictícios; a atividade não representa um roteirizador comercial com mapas, trânsito e ruas.

Não devemos trocar o algoritmo para melhorar os números durante a comparação: isso mudaria outra variável além da quantidade de Pods.

## 4. Por que aparecem tantas falhas?

O código usa `BoundedSemaphore(1)`. Pense em uma vaga para cálculo: quem encontra a vaga livre começa; quem chega enquanto está ocupada recebe 503. Não existe fila de espera.

O servidor HTTP usa threads, mas o semáforo continua permitindo um cálculo por processo. Abrir várias threads não transforma esse código em vários calculadores simultâneos.

Uma réplica extra é outro processo com sua própria vaga. Portanto, mais réplicas podem atender cálculos ao mesmo tempo. Isso ainda não garante que cada pedido chegue a uma vaga livre.

## 5. Código, imagem e contêiner

O código é a receita escrita em Python. A imagem Docker é um pacote preparado com Python, código e instrução de execução. O contêiner é a execução daquele pacote.

| Elemento | Exemplo |
|---|---|
| Código | app.py |
| Receita de construção | Dockerfile |
| Imagem | rotas:1.0 |
| Contêiner local temporário | rotas-teste |

O Dockerfile original parte de `python:3.12-slim`, usa `/app`, copia `app.py`, configura logs imediatos, evita bytecode, usa usuário `10001:10001` e inicia `python app.py`.

`EXPOSE 8000` documenta a porta, mas não cria acesso no Windows. O `docker run -p` faz o mapeamento de porta. Em `127.0.0.1:8000:8000`, o lado esquerdo é a porta local e o direito é a porta do contêiner; o endereço restringe o acesso ao próprio computador.

`.dockerignore` controla os arquivos que entram no contexto de build. Aqui ele exclui tudo, exceto a aplicação e o Dockerfile. Evidências, PDFs e ambientes virtuais não vão para a imagem.

Por que testar a imagem antes do Kubernetes? Se ela já falha sozinha, investigamos código ou empacotamento antes de acrescentar as camadas de cluster e rede.

## 6. O que o Windows precisa?

Os contêineres da atividade são Linux. No Windows, o Docker Desktop usa o backend WSL 2 para executá-los. WSL é a camada que permite executar esse ambiente Linux.

Neste computador, não foi necessária uma distribuição Ubuntu separada: o Docker criou `docker-desktop`. A instalação inicial do WSL exigiu administrador e reinício. Docker e Ubuntu não são a mesma coisa, e não é obrigatório instalar ambos como aplicativos independentes para seguir este caminho.

Docker foi retirado da inicialização automática a pedido do usuário. Portanto, abra o Docker Desktop manualmente antes de iniciar o laboratório. Instalar o executável não basta: o daemon, isto é, o serviço que executa os contêineres, precisa responder. `docker version` deve mostrar Client e Server.

## 7. Por que Kubernetes e Minikube?

Kubernetes coordena cargas em contêineres. Nós descrevemos o estado desejado e seus componentes tentam aproximar o estado observado desse objetivo.

Minikube cria o cluster local usado no laboratório. Cluster é o conjunto coordenado; nó é uma máquina participante. Aqui temos um nó dentro de um contêiner Docker. O perfil se chama `ops-lab`.

O comando do professor limita esse contêiner a três CPUs e 3072 MiB. Minikube não é sinônimo de Kubernetes: é uma forma de criar um cluster Kubernetes local.

`kubectl` é o cliente da API Kubernetes. Ao rodar `kubectl apply`, ele envia um pedido à API. Controladores, scheduler e kubelet fazem o trabalho de manter e executar os objetos. kubectl não é o processo da aplicação.

## 8. As peças do cluster

| Peça | Responsabilidade |
|---|---|
| API server | Recebe e valida pedidos de administração |
| etcd | Guarda o estado do cluster |
| Controladores | Comparam o desejado com o observado e reagem |
| Scheduler | Escolhe o nó para o Pod, considerando recursos e regras |
| Kubelet | Agente do nó que acompanha a execução dos Pods |
| Runtime | Executa os contêineres no nó |
| CoreDNS | Resolve nomes dos serviços |
| kube-proxy | Implementa encaminhamento dos Services no ambiente do laboratório |

Você não precisa decorar todos os processos. Precisa entender que existe uma cadeia entre declarar uma configuração e ter um processo pronto atendendo.

Contexto é a combinação de cluster e identidade no kubeconfig, com namespace opcional. Namespace organiza os objetos dentro do cluster. Ambos se chamam ops-lab aqui, mas são coisas diferentes. Confira o contexto antes de alterar ou apagar recursos.

Namespace não é, sozinho, uma barreira completa de segurança. Não adicionamos mecanismos de isolamento de produção a esse laboratório didático.

## 9. Pod, ReplicaSet e Deployment

Pod é a menor unidade implantável do Kubernetes. Pode conter mais de um contêiner; neste projeto, cada Pod da aplicação contém um contêiner Python.

Deployment define o modelo dos Pods e a quantidade pretendida. ReplicaSet mantém a quantidade correspondente a um modelo. A relação é Deployment → ReplicaSet → Pods.

Se excluímos um Pod, o número observado fica menor que o desejado. O controlador cria outro. O novo Pod tem outro UID e pode ter outro nome e IP. A mesma instância não “ressuscitou”: outra foi criada para cumprir o objetivo.

Quando muda o template, como ao acrescentar probes, o Deployment cria outra revisão e outro ReplicaSet. Escalar a quantidade, por sua vez, não exige mudar o código da aplicação.

## 10. Service, labels e EndpointSlices

Os endereços individuais dos Pods mudam. O Service oferece nome estável: `rotas`, na porta 8000. Ele encontra os Pods pelas labels. O selector do Service é `app=rotas`, igual às labels do template do Deployment.

EndpointSlices listam os endereços selecionados e suas condições de prontidão. Se o Service existe e não funciona, confira os endpoints, labels, readiness e targetPort.

O Service do projeto é ClusterIP: seu endereço é interno. Dentro do namespace, o k6 usa `http://rotas:8000`. O gerador tem label diferente, `app=gerador-carga`, para não ser selecionado como se fosse a aplicação.

**Ponto central:** o Service distribui conexões, sem saber se o semáforo de um Pod está ocupado. Um pedido pode receber 503 mesmo havendo outro Pod livre. O encaminhamento não garante uma divisão exatamente igual.

O `port-forward` é um túnel para inspeção local. Ao abrir um túnel para o Service, kubectl escolhe um Pod e fica ligado nele. Recarregar a página não demonstra distribuição entre réplicas. Por isso o teste de carga roda dentro do cluster, acessando o Service diretamente.

## 11. Como ler YAML sem decorar

YAML representa uma hierarquia por indentação com espaços. `apiVersion` indica a API, `kind` o tipo, `metadata` a identidade e `spec` o desejado. Kubernetes devolve `status` com o observado.

No Deployment, `spec.replicas: 1` pede uma réplica. `spec.template` descreve cada Pod. `containers` fica dentro do spec desse template. Selector e labels precisam combinar.

`apply -f` aplica a descrição. `get` mostra resumo. `describe` mostra detalhes e eventos. `logs` lê o que o processo escreveu. `rollout status` espera a publicação convergir. Um apply aceito não prova que a aplicação está pronta.

Escalar com `kubectl scale` muda a quantidade diretamente na API. Aplicar depois um manifesto que pede uma réplica pode desfazer a escala manual. Durante a série, não reaplique o Deployment.

## 12. Requests e limits

Cada Pod da aplicação solicita 500m de CPU e 64Mi de memória e limita CPU a 500m e memória a 128Mi. `500m` é meia CPU. `Mi` usa unidade binária de memória.

Request orienta o agendamento. Limit restringe a execução. CPU acima do teto sofre desaceleração, chamada throttling. Excesso de memória pode levar a OOMKilled. Request não significa uso real permanente e limit não significa que aquele consumo foi medido.

Uma, duas e três réplicas reservam 0,5, 1 e 1,5 CPU para a aplicação. O control plane e o k6 também consomem recursos. Aumentar réplicas não cria capacidade física.

O exercício de seis réplicas deveria mostrar a restrição do scheduler no cenário ilustrativo do guia. Neste computador, seis Pods ficaram Running porque o nó anunciou 12 CPUs, embora seu contêiner estivesse limitado a três. Registramos essa diferença em vez de inventar Pods Pending. No outro notebook, o comportamento precisa ser observado novamente.

## 13. Saúde e segurança

Readiness pergunta se o Pod está pronto para receber tráfego do Service. Sua falha retira prontidão, sem reiniciar automaticamente o processo. Liveness pergunta se o contêiner deve ser reiniciado após falhas consecutivas.

Aqui readiness consulta `/readyz` a cada cinco segundos. Liveness consulta `/healthz` a cada dez segundos, iniciando depois de dez segundos. Os caminhos são leves. Estar saudável não significa ter a vaga de cálculo disponível.

O securityContext exige usuário não root, impede escalada de privilégios e deixa a raiz somente leitura. Isso funciona porque a aplicação não precisa gravar dados. São restrições úteis, mas não tornam um servidor didático adequado a qualquer produção.

## 14. A falha e o rollback

Publicamos intencionalmente `rotas:1.1`, uma imagem indisponível. O novo Pod falhou ao obtê-la. O rollout não terminou no prazo. Eventos mostraram ErrImagePull/ImagePullBackOff.

Com uma réplica, a estratégia padrão RollingUpdate permite um Pod extra e não permite remover o único disponível antes de o novo ficar pronto. Por isso o Pod antigo de rotas:1.0 continuou atendendo. Testamos o HTTP durante a falha.

`rollout undo` restaurou o template anterior. Rollback não reconstrói a imagem e não desfaz mudanças em bancos ou serviços externos. A evidência é a combinação de imagem, status, eventos e atendimento, não apenas um comando com mensagem de sucesso.

## 15. O teste k6

O k6 é um cliente automático que gera demanda. Ele executa como Job: uma tarefa que termina. ConfigMap guarda o arquivo `carga.js` e o monta no contêiner k6, separado da imagem.

| Parâmetro | Valor da série e significado |
|---|---|
| TAXA | 6 pedidos iniciados por segundo |
| PARADAS | 9 entregas em cada cálculo |
| DURACAO | 60 segundos de medição |
| URL | Service interno http://rotas:8000 |

O executor constant-arrival-rate programa novas iterações sem esperar as anteriores terminarem. O aquecimento dura dez segundos. Há intervalo até o segundo vinte, quando começa a janela medida. Conexões novas permitem novas escolhas pelo Service.

Threshold é uma meta. O projeto exige falhas abaixo de 1%, p95 abaixo de 800 ms e nenhum descarte da medição. O k6 pode terminar com código 99 quando uma meta falha. O Job aparece Failed, mas o resumo completo continua sendo resultado válido de desempenho.

Job sem resumo, imagem que não iniciou ou deadline excedido é outra situação: falha de execução. Não preencha a tabela com zeros nesse caso.

## 16. Métricas que você precisa dominar

`rotas_ok` conta rotas válidas na janela medida. Throughput é a quantidade de trabalho concluído por segundo: rotas_ok dividido por 60. O /s global do resumo do k6 inclui outros períodos e não é a fórmula pedida.

`falhas` é a fração das tentativas que não produziram uma rota válida. `latencia_ok` registra tempos HTTP dos sucessos. p95 é o percentil abaixo do qual ficam aproximadamente 95% desses tempos. Não é a média e não descreve quem recebeu erro.

`dropped_iterations{scenario:medicao}` conta iterações programadas que o gerador não conseguiu iniciar. Isso é diferente de 503: o 503 veio da aplicação após uma requisição; o descarte significa demanda que nem foi iniciada pelo gerador.

CPU e memória foram amostradas com top. Essas leituras têm atraso e não provam picos contínuos. Depois de reduzir réplicas, a API pode mostrar brevemente métricas em cache de Pods removidos. A análise filtra os nomes usando os Pods reais daquele teste e preserva a saída bruta.

## 17. Por que piloto e nove execuções?

O piloto usa uma réplica para encontrar uma demanda informativa. Quase só sucessos pode significar demanda pequena. Quase nenhum sucesso junto com descartes pode significar demanda excessiva para o gerador. O piloto a 6/s teve 120 rotas válidas, 66,75% de falhas, p95 436,19 ms e zero descartes, justificando manter essa taxa para comparar réplicas.

Depois da calibração, mudamos apenas o número de réplicas. Imagem, recursos, paradas, duração e configuração k6 ficam iguais. A ordem foi A: 3,1,2; B: 2,3,1; C: 1,2,3. A alternância ajuda a reduzir o efeito de sempre medir a mesma configuração primeiro.

Antes de cada execução, esperamos réplicas e endpoints prontos. Guardamos contadores antes/depois, recursos, objetos e logs. Os contadores dos Pods incluem aquecimento; não devem ser somados e confundidos com rotas_ok da janela medida.

## 18. Refaça uma conta real

No teste `3pods-c`, ocorreram 244 rotas válidas em 60 s: 244 ÷ 60 = 4,0666... rotas/s. A apresentação arredonda para 4,07. É diferente de dizer que todos os seis pedidos/s tiveram sucesso.

Para três Pods, os throughputs das repetições foram aproximadamente 3,9833, 4,2667 e 4,0667. Ordene: 3,9833; 4,0667; 4,2667. O valor do meio, 4,0667, é a mediana.

Calcule a mediana separadamente para throughput, falhas e p95 de cada configuração. A mediana dos três p95 não é o p95 de todas as requisições reunidas. Com três repetições, a análise é descritiva e limitada.

## 19. Qual é a conclusão correta?

As medianas foram 2,23, 3,53 e 4,07 rotas/s. As falhas medianas caíram de 62,88% para 41,27% e 32,40%. Os p95 ficaram em 387,96, 382,28 e 380,58 ms. Nenhuma medição descartou iterações.

Três Pods aumentaram o throughput em aproximadamente 82,1% em relação a um, reservando três vezes a CPU da aplicação. A melhora não foi linear. Três Pods tiveram o melhor atendimento entre os cenários, mas nenhuma configuração cumpriu a meta de falhas abaixo de 1%.

A conclusão não é “Kubernetes falhou”. A aplicação tem um calculador por Pod e recusa concorrentes; o Service não consulta ocupação. Fila, algoritmo mais eficiente e estratégia de encaminhamento são investigações futuras, não alterações retroativas do experimento.

Um único nó também é uma falha comum para todas as réplicas. Este trabalho não comprova tolerância à queda do notebook. Resultados do computador original não se tornam resultados do outro notebook só porque os arquivos foram copiados.

## 20. Como apresentar em dois minutos

“Recebemos uma aplicação que calcula rotas por força bruta e aceita um cálculo por Pod de cada vez. Empacotamos a aplicação com Docker e publicamos no Minikube. O Deployment mantém as réplicas e o Service oferece um endereço estável. Validamos os endpoints, a reposição de um Pod excluído e o rollback de uma imagem inválida. Depois executamos k6 dentro do cluster, mantendo demanda e recursos por Pod fixos, com três repetições de cada configuração. Três Pods tiveram a maior mediana, 4,07 rotas/s, mas ainda apresentaram 32,40% de falhas. Portanto, replicar melhorou o atendimento, mas não atingiu todas as metas. Registramos os limites da aplicação e do ambiente e preservamos os logs que sustentam essa conclusão.”

Use a fala como apoio. Para defender o projeto, você precisa entender o motivo de cada afirmação e localizar sua evidência.
