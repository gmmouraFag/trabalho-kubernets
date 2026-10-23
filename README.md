# RotaExpress: do primeiro contato à apresentação

Este repositório reúne a aplicação fornecida pelo professor, a infraestrutura Kubernetes, as evidências de uma execução real e um roteiro de estudo para quem está começando.

**Comece por [estudo/00-plano-de-estudo.md](estudo/00-plano-de-estudo.md).** Você não precisa entender todos os arquivos de uma vez.

**Para explicar o código ao professor, abra o [guia do código para a defesa](estudo/05-codigo-explicado-para-defesa.md).** Ele acompanha as funções Python, a tela, o teste k6, Docker, os manifestos e a automação, com exemplos e perguntas respondidas.

## Caminho de leitura

1. [Plano de estudo: sete encontros](estudo/00-plano-de-estudo.md).
2. [Explicação completa, do HTTP aos resultados](estudo/01-entenda-o-projeto.md).
3. [Exercícios práticos com respostas esperadas](estudo/02-laboratorio-guiado.md).
4. [Preparação do outro notebook Windows 11](estudo/03-outro-notebook.md).
5. [Revisão e perguntas para a defesa](estudo/04-revisao-e-defesa.md).
6. [Código explicado: funções, fluxo e roteiro para a defesa](estudo/05-codigo-explicado-para-defesa.md).

## O que foi realizado

Docker Desktop, WSL, kubectl e Minikube foram preparados no computador da medição. A imagem foi testada fora do cluster, a aplicação foi publicada, um Pod foi excluído e recriado, uma imagem inválida foi revertida e o k6 executou um piloto e nove medições internas ao Kubernetes.

Os arquivos originais estão em `projeto/` e as cópias de referência em `projeto/originais/`. A lógica de `app.py` e `carga.js` foi preservada. Os PDFs do professor ficam nesta pasta; consulte principalmente o Guia_Atividade.pdf.

## Resultado medido, não promessa para qualquer computador

Demanda fixa de 6 pedidos/s, nove entregas por rota, janela de 60 s e três repetições por configuração:

| Pods | Throughput mediano (rotas/s) | Falhas medianas | p95 mediano dos sucessos |
|---|---:|---:|---:|
| 1 | 2,23 | 62,88% | 387,96 ms |
| 2 | 3,53 | 41,27% | 382,28 ms |
| 3 | 4,07 | 32,40% | 380,58 ms |

Todas as medições tiveram zero iterações descartadas. Nenhuma configuração cumpriu a meta de falhas abaixo de 1%. O aumento de réplicas melhorou o atendimento, mas não resolveu a recusa de pedidos quando o calculador escolhido estava ocupado.

O exercício de seis réplicas resultou em seis Pods Running: o kubelet anunciou 12 CPUs ao scheduler, embora o contêiner do nó tivesse quota de três CPUs. A diferença está documentada, sem forçar a saída ilustrativa do professor.

## Onde estão as entregas

| Local | Conteúdo |
|---|---|
| [projeto/k8s](projeto/k8s) | Namespace, Deployment em duas versões, Service e Job k6 |
| [projeto/scripts](projeto/scripts) | Automação e análise |
| [projeto/resultados](projeto/resultados) | CSVs, logs, evidências e gráficos medidos |
| [Relatório experimental](projeto/documentacao/05-relatorio-experimentos.md) | Método, medianas, recursos observados e conclusão |
| [Documentação](projeto/documentacao) | Instalação, implementação, perguntas e demonstração |
| [PowerPoint](projeto/apresentacao/RotaExpress.pptx) | Apresentação editável de 16 slides |
| [Roteiro das falas](projeto/apresentacao/roteiro-slides.md) | Explicações para apresentar os slides |
| [Checklist](projeto/CHECKLIST_ENTREGA.md) | Requisitos e evidências |

## Outro notebook

Copiar os arquivos não copia Docker, WSL ou o cluster. Siga o [guia do outro notebook](estudo/03-outro-notebook.md). Prepare uma pasta separada para demonstração e mantenha os resultados históricos intactos.

O cluster original foi parado e o namespace removido após a coleta. Abra o Docker manualmente para voltar a executar o laboratório. Scripts PowerShell foram executados no Windows. Os equivalentes Bash tiveram sintaxe verificada, mas não foram executados em Linux.

## Proveniência e publicação

Aplicação, script de carga e PDFs acadêmicos fornecidos pelo professor. Scripts adicionais, documentação, estudo e apresentação foram preparados com assistência de IA e precisam ser compreendidos pelo grupo antes da defesa. A autoria e os direitos dos materiais originais permanecem com seus respectivos autores; este repositório não atribui uma licença aberta a esses materiais.

Logs de diagnóstico com PATH e inventário pessoal, ambientes virtuais, configurações de autenticação e arquivos temporários foram excluídos do versionamento. As evidências de Kubernetes necessárias ao experimento permanecem disponíveis.
