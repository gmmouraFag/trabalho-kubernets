# Revisão: descubra o que você já consegue explicar

Responda primeiro sem olhar o gabarito. Se travar, volte à seção correspondente da explicação completa. Não tente memorizar as palavras exatas.

## Perguntas essenciais

1. O que a aplicação calcula e o que torna esse cálculo custoso?
2. Por que um pedido pode receber 503 com a aplicação saudável?
3. Qual é a diferença entre imagem, contêiner e Pod?
4. Por que usar Deployment em vez de um Pod avulso?
5. Para que serve o Service se já temos IPs dos Pods?
6. Como selector e labels ligam o Service à aplicação?
7. Por que recarregar a página pelo port-forward não prova balanceamento?
8. Qual é a diferença entre request e limit?
9. Readiness e liveness fazem a mesma coisa?
10. Por que a imagem 1.1 falhou sem interromper o Pod antigo?
11. Qual é a função do ConfigMap e qual é a do Job?
12. O que TAXA=6 significa? Significa seis sucessos por segundo?
13. Quais períodos entram nas métricas próprias do k6?
14. O que p95 descreve e o que ele não descreve?
15. Qual a diferença entre uma resposta 503 e uma iteração descartada?
16. Como calcular throughput e mediana?
17. Por que a ordem dos testes muda entre as rodadas?
18. Por que três Pods tiveram mais throughput, mas ainda muitas falhas?
19. Por que os seis Pods ficaram Running neste computador?
20. Os resultados existentes podem ser atribuídos ao notebook da apresentação?

## Gabarito comentado

1. Menor circuito euclidiano entre depósito e entregas. Para nove entregas, enumera 362.880 ordens e repete o cálculo em cada pedido.
2. Há uma vaga por processo, sem fila. Ocupação do calculador causa recusa, sem implicar que o processo morreu.
3. Imagem é o pacote; contêiner é sua execução; Pod é a unidade Kubernetes que contém o contêiner da aplicação neste projeto.
4. O Deployment coordena ReplicaSets, que mantêm a quantidade de Pods, além de oferecer revisões e rollout.
5. IPs de Pods mudam. O Service oferece nome/endereço estável e encaminha conexões aos destinos prontos.
6. O selector app=rotas encontra as labels iguais nos Pods. Prontidão e EndpointSlices completam o caminho.
7. O túnel escolhe um Pod e fica ligado nele. O teste k6 usa o Service por dentro do cluster.
8. Request orienta agendamento; limit restringe execução. São diferentes de consumo amostrado.
9. Readiness controla prontidão para tráfego. Liveness pode provocar reinício após falhas repetidas.
10. O Pod novo não obteve a imagem e não ficou pronto. A estratégia com uma réplica manteve o antigo disponível até haver substituto pronto.
11. ConfigMap entrega configuração/script. Job representa uma tarefa que termina, aqui o teste de carga.
12. Programa aproximadamente seis inícios de iteração por segundo. Parte pode falhar; não significa seis rotas concluídas.
13. Aquecimento de dez segundos fica fora. A janela própria começa no segundo vinte e dura sessenta.
14. Resume a distribuição dos tempos HTTP dos sucessos. Não mede o sofrimento de quem recebeu erro nem equivale à média.
15. 503 é resposta da aplicação. Descarte significa que o gerador não iniciou uma iteração programada.
16. Throughput = rotas_ok/60. Mediana de três repetições é o valor central depois de ordená-las, por configuração e por métrica.
17. Para reduzir o viés de sempre medir a mesma configuração antes das outras, com diferentes estados do computador.
18. Há mais calculadores, mas o Service não conhece ocupação. A conexão pode cair em um calculador ocupado mesmo com outro livre.
19. O scheduler usou a capacidade anunciada de 12 CPUs, maior que a quota de três CPUs do contêiner do nó. Não devemos inventar Pending.
20. Não. São resultados do computador e das condições descritos no relatório. No outro notebook, demonstre a aplicação ou faça um experimento novo e identificado.

## Três contas para fazer no papel

**A.** No teste 3pods-c, quantas rotas/s são 244 sucessos em 60 s? Resposta: 4,0666..., exibido como 4,07.

**B.** Ordene os resultados de três Pods: 3,9833; 4,2667; 4,0667. Resposta: 3,9833; 4,0667; 4,2667. Mediana: 4,0667.

**C.** Três Pods com request de 500m reservam quanto? Resposta: 1500m = 1,5 CPU para a aplicação, sem somar k6 e componentes do cluster.

## Afirmações que você deve evitar

| Evite dizer | Diga com precisão |
|---|---|
| Três Pods resolveram o problema | Melhoraram o throughput, mas nenhuma configuração cumpriu todas as metas |
| O teste falhou porque o Job ficou Failed | O k6 executou e saiu 99 por thresholds; os logs contêm um resultado válido |
| O Service manda para o Pod livre | O Service não consulta a vaga do calculador |
| p95 baixo significa que todo mundo foi atendido | O p95 é dos sucessos e precisa ser lido com a taxa de falhas |
| Três Pods são três máquinas | Neste laboratório, são réplicas no mesmo nó |
| Os logs do GitHub são do notebook de hoje | São do computador original; a demonstração atual é outra execução |
| Usou 1,5 CPU porque havia três requests | Reservou 1,5 CPU; consumo precisa de medição |

## Roteiro curto para ensaiar a demonstração

1. Explique a pergunta e confirme o contexto ops-lab.
2. Mostre o nó Ready, o namespace e os Pods prontos.
3. Mostre o Service e compare seus endpoints com os Pods.
4. Abra a interface, calcule nove entregas e identifique quem atendeu.
5. Mostre os logs e explique os contadores.
6. Escale para três e espere convergir. Explique o papel do Deployment.
7. Mostre os resultados históricos e explique as medianas.
8. Conclua: melhor throughput com três, metas não cumpridas e limites do experimento.

Reserve aproximadamente cinco a sete minutos para essa parte. A falha de imagem pode ser explicada pelos logs salvos para evitar gastar um minuto de timeout em uma apresentação curta. Se o professor pedir execução ao vivo, use o exercício já ensaiado e restaure a versão funcional.

## Você está pronto quando...

Consegue explicar a aplicação em dois minutos, mostrar o caminho da requisição no diagrama, executar a demonstração com o roteiro ao lado e responder às perguntas essenciais. Consultar uma referência de comando é normal; chamar um resultado que não compreende de “sucesso total” é o que deve ser evitado.
