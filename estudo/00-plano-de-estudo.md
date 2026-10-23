# Seu plano de estudo: uma etapa de cada vez

## O que você precisa conseguir fazer

Você não precisa decorar Kubernetes inteiro. Ao terminar este plano, precisa explicar a aplicação, o papel de cada ferramenta, como publicar e demonstrar o serviço e o que os resultados permitem concluir.

A atividade do professor pede os manifestos, os logs, a tabela comparativa e uma análise que sustente uma decisão. A apresentação ajuda a explicar isso. Os testes já realizados são evidências do computador original; o outro notebook precisa de seu próprio ambiente para a demonstração ao vivo.

## Como estudar sem se perder

Se sua prioridade é explicar o código ao professor, siga o [guia do código para a defesa](05-codigo-explicado-para-defesa.md), com o arquivo original aberto ao lado. Ele contém um plano de três dias, explicações por função, perguntas com respostas e um roteiro de apresentação.

Separe sete sessões de aproximadamente uma hora. Se tiver pouco tempo, faça duas por dia com uma pausa. Leia apenas os trechos indicados. Depois feche o texto e explique em voz alta. Ao executar comandos, observe a saída antes de passar ao próximo. Marque os critérios somente quando conseguir mostrar ou explicar o resultado.

| Sessão | Tempo | Você estuda | Você pratica | Critério para seguir |
|---|---|---|---|---|
| 1. Problema e aplicação | 45–60 min | Explicação completa, seções 1–4 | Desenhar navegador, aplicação e resposta; explicar 200 e 503 | Explicar em 2 min o que a aplicação faz e por que recusa pedidos |
| 2. Docker e WSL | 45–60 min | Seções 5–6 e Dockerfile | Identificar imagem, contêiner e porta | Explicar imagem versus contêiner e para que serve WSL no Windows |
| 3. Kubernetes | 60–75 min | Seções 7–10 | Relacionar Namespace, Deployment, ReplicaSet, Pod e Service | Desenhar o caminho de uma requisição e o caminho de controle |
| 4. Publicação e saúde | 60–90 min | Seções 11–13 e laboratório 1–5 | Subir a aplicação na pasta de demonstração e abrir o navegador | Mostrar Pod pronto, endpoint, interface e logs |
| 5. Falha e recuperação | 45–60 min | Seção 14 e laboratório 6–7 | Mostrar recriação; estudar as evidências de rollback | Explicar por que o Pod antigo continuou atendendo |
| 6. Experimento e resultados | 60–75 min | Seções 15–19 | Recalcular throughput e mediana com a tabela real | Explicar 4,07 rotas/s, 32,40% de falhas e zero descartes sem confundir as métricas |
| 7. Defesa e ensaio | 60 min | Revisão e roteiro dos slides | Apresentar e demonstrar cronometrando | Fazer a apresentação sem ler parágrafos inteiros e responder às perguntas essenciais |

## Antes de cada sessão

- Escreva: “Hoje vou entender ___”.
- Anote três palavras desconhecidas e procure-as no glossário da explicação completa.
- Depois da leitura, escreva três frases com suas próprias palavras.
- Execute apenas os comandos daquela etapa e registre qualquer dúvida.

## Checklist pessoal

- [ ] Sei explicar o problema da transportadora.
- [ ] Sei por que um Pod recusa um segundo cálculo.
- [ ] Sei diferenciar código, imagem, contêiner e Pod.
- [ ] Sei diferenciar Deployment e Service.
- [ ] Sei conferir contexto e namespace antes de mudar algo.
- [ ] Sei abrir a aplicação e mostrar o Pod que respondeu.
- [ ] Sei explicar requests, limits, readiness e liveness.
- [ ] Sei explicar recriação e rollback.
- [ ] Sei explicar TAXA, aquecimento, janela medida e thresholds.
- [ ] Sei calcular rotas/s e mediana.
- [ ] Sei dizer por que três Pods melhoraram o throughput sem cumprir a meta de falhas.
- [ ] Sei explicar por que o exercício de seis réplicas teve resultado diferente do exemplo.
- [ ] Preparei o outro notebook e ensaiei antes da apresentação.

## O que não precisa fazer agora

Não mude o algoritmo, não acrescente HPA e não altere os recursos para tentar “consertar” a nota do teste. O objetivo é compreender e analisar o cenário recebido. Também não precisa repetir a série só para ler os resultados. Se houver exigência de novas medições no outro notebook, faça um experimento novo, separado e recalibrado.

Próxima leitura: [entenda o projeto](01-entenda-o-projeto.md).
