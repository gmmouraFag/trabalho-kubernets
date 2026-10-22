# Checklist de entrega

Origem primária: Guia_Atividade.pdf. As referências abaixo usam seções e páginas descritas em documentacao/03. Itens do prompt são adicionais do usuário, não exigências inventadas do professor.

Estados: Implementado = arquivo criado; Validado = teste com evidência; Medido = resultado real; Pendente = sem comprovação; Simulado = apenas ilustrativo. Não há dados simulados na tabela experimental.

| Origem | Requisito | Status | Evidência relativa a resultados/ (salvo indicado) |
|---|---|---|---|
| 0.1–0.3 | Ferramentas e pasta | Validado | logs/diagnostico-*.txt |
| 1.1–1.5 | Cluster, contexto, API, nós e Pods do sistema | Validado | logs/cluster-*.txt |
| 1.6–1.8 | Namespace e metrics-server | Validado | k8s/namespace.yaml e logs/cluster-*.txt |
| 2.1 | Dockerfile e .dockerignore compreendidos, originais preservados | Validado | evidencias/validacao-estatica-http.json e documentacao/04 |
| 2.2–2.4 | Build, teste Docker e image load | Validado | logs/publicacao-*.txt |
| 3.1–3.4 | Primeiro Deployment e hierarquia | Validado | k8s/versoes/deployment-inicial.yaml |
| 3.5 | Excluir Pod e observar recriação | Validado | evidencias/pod-antes-recriacao.json e pod-depois-recriacao.json |
| 3.6 e Apêndice B | Recursos, probes, segurança e rollout da segunda versão | Validado | k8s/deployment.yaml e evidencias/pods-final.txt |
| 4.1–4.3 | Service, selectors, EndpointSlices e HTTP interno | Validado | k8s/service.yaml e evidencias/endpointslices.json |
| 4.4 | Interface no navegador e port-forward | Validado | evidencias/navegador.png |
| 5.1–5.3 | Imagem inválida, disponibilidade e rollback | Validado | logs/rollback-*.txt e evidencias/rollback-* |
| 6.1–6.3 | Parâmetros k6, ConfigMap e Job | Validado | carga.js e k8s/job-carga.yaml |
| 6.4–6.6 | Piloto completo, calibração e taxa fixa | Medido | logs/piloto*.txt e calibracao.json |
| 7.1 | Réplicas prontas e endpoints antes de cada teste | Medido | evidencias/ROTULO/pods-antes.json e endpointslices.json |
| 7.2 e 7.4 | Contadores antes/depois e distribuição por Pod | Medido | evidencias/ROTULO/contadores-*.txt |
| 7.3 | Amostras de CPU e memória, incluindo k6 | Medido | evidencias/ROTULO/recursos.txt |
| 7.5 | Nove testes na ordem A/B/C e mesmas condições | Medido | comparativo.csv: 9/9 completos |
| 8.1 | Seis réplicas, scheduler e restauração para uma | Validado | evidencias/seis-replicas-* |
| 8.2–8.4 | Medianas, análise de gargalos e decisão | Medido | documentacao/05 e medianas.csv |
| 8.5 | Salvar evidências, apagar namespace e parar cluster | Validado | evidencias/encerramento.txt ou executar após demonstração: encerrar-ambiente.ps1 -LimparNamespace |
| Prompt §17–18 | Documentação didática em português | Implementado | documentacao/00 a 09 |
| Prompt §19–20 | Apresentação editável de 16 slides e falas | Implementado | apresentacao/RotaExpress.pptx e roteiro-slides.md |
| Prompt §21 | Demonstração com plano alternativo | Implementado | documentacao/07 |
| Prompt §23–24 | Validar YAML, originais e integridade de métricas | Validado | evidencias/validacao-estatica-http.json e validacao-servidor.txt |
