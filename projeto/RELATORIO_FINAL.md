# Relatório de entrega

## Escopo

Implementação e investigação DevOps do RotaExpress a partir dos dois PDFs e seis arquivos originais fornecidos. A aplicação e o script de carga permanecem intactos. A pasta do projeto de vídeos em C:\Temp\dowloadvideo não foi modificada.

## Ferramentas e computador

Windows 11 Pro, Ryzen 5 7600X, aproximadamente 31 GB de RAM. Instalações concluídas: Docker Desktop 4.96.0 (Engine 29.9.1), kubectl 1.37.1 e Minikube 1.39.0. O usuário instalou WSL 3.0.3 com administrador e reiniciou; o daemon Linux respondeu depois do reinício. Python 3.14.5 e Git 2.54.0 já existiam. Ferramentas auxiliares isoladas em .ferramentas. k6 1.0.0 no Kubernetes.

## Implementação e validação

Quatro manifestos principais e versão inicial do Deployment. Automação PowerShell de diagnóstico, instalação, cluster, publicação, validação, rollback, carga, capacidade e encerramento. Equivalentes Bash disponibilizados com sintaxe verificada, sem execução em Ubuntu. Documentação didática 00–09, checklist, roteiro de demonstração e falas para 16 slides.

Foram verificados os endpoints HTTP localmente e com Docker, a comunicação pelo Service, a interface no navegador, a reposição de Pod e o retorno da versão inválida para 1.0. A evidência de cada afirmação está no checklist. O teste HTTP local no Windows não compõe o experimento de carga.

## Experimento

9/9 medições completas além do piloto, com TAXA fixada em 6/s, PARADAS=9 e DURACAO=60 s. Logs completos, recursos e contadores preservados por execução. A maior mediana de throughput foi de 4.067 rotas/s com 3 Pods. O menor p95 mediano foi 380.58 ms com 3 Pods. A menor mediana de falhas foi 32.40% com 3 Pods. Descartes na série: 0. Nenhuma configuração cumpriu todas as metas nas três repetições. A decisão é não declarar capacidade suficiente para essa demanda. A próxima investigação deve examinar ocupação do calculador, fila e algoritmo, sem modificar retroativamente os parâmetros desta série.

Tabela: resultados/comparativo.csv. Medianas: resultados/medianas.csv quando a série estiver completa. Gráficos: resultados/graficos/. Metodologia, recursos observados, perguntas operacionais e limites: documentacao/05-relatorio-experimentos.md.

## Estado final e limitações

O namespace da atividade foi removido e o perfil ops-lab foi parado após salvar as evidências, conforme o encerramento do guia. Os manifestos e a imagem permitem recriar o ambiente pelos scripts. Nenhum outro cluster foi removido.

A quota real do contêiner do nó é de 3 CPUs/3 GiB, mas o kubelet anuncia os recursos da VM ao scheduler. O exercício de seis réplicas deve ser interpretado com essa diferença, sem assumir a saída ilustrativa de Pods Pending. As amostras de top são defasadas e não equivalem a picos contínuos. Nenhuma configuração pode ser declarada adequada somente por ter o maior throughput.

Não há integração Canva disponível nesta sessão. A entrega é um PPTX editável, com importação no Canva ainda não testada. Os arquivos editáveis e o roteiro ficam em apresentacao/. Não foi alegada revisão no aplicativo Microsoft PowerPoint.

## Reprodução e localização

Use documentacao/02-instalacao.md para a sequência de scripts, documentacao/07-guia-demonstracao.md para a defesa e CHECKLIST_ENTREGA.md para verificar atendimento. LEIA-ME-ENTREGA.md reúne os caminhos. A documentação e os materiais finais ficam em C:/Users/Cliente/Downloads/Atividade/RotaExpress_Kubernetes/projeto.
