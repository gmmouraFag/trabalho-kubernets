# Solução de problemas

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

## Ocorrências reais desta execução

A primeira instalação do WSL por winget exigiu administrador (0x80073d28). O usuário instalou o componente em terminal elevado e reiniciou; Docker passou a responder após isso.

A consolidação da última medição detectou uma diferença de tipos no código: a taxa recém-importada era número e as taxas lidas do CSV eram texto. A série tinha a mesma taxa 6/s. Normalizamos os tipos no consolidador e reprocessamos os logs preservados, sem repetir nem alterar as medições. A auditoria reconciliou os nove registros com as fontes.

O metrics-server manteve brevemente leituras de Pods removidos após reduzir réplicas. Filtramos os resumos pelos nomes presentes nas capturas antes de cada teste e pelo Pod real do Job. Os arquivos recursos.txt conservam integralmente as leituras originais, incluindo essas entradas em cache.

No exercício de seis réplicas, os seis Pods ficaram Running. A quota Docker de 3 CPUs e 3072 MiB não coincidiu com as 12 CPUs e a memória maior anunciadas pelo kubelet. Portanto, não observamos a falta de CPU do exemplo do professor nesse ambiente. A configuração foi restaurada para uma réplica e o desvio ficou registrado no relatório.
