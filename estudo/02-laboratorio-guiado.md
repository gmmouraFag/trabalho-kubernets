# Laboratório guiado: observar antes de decorar

Faça este laboratório na pasta separada de demonstração, conforme o guia do outro notebook. Os comandos alteram somente o perfil/namespace da atividade, mas duas pastas ainda podem apontar para o mesmo cluster. Não execute cópias simultâneas.

## 1. Preparar e conferir as ferramentas

Abra Docker Desktop manualmente. No PowerShell, dentro da pasta de demonstração:

```powershell
.\scripts\verificar-ambiente.ps1
```

Procure Client e Server em docker version, além das versões de kubectl e Minikube. Pergunta: por que o cliente instalado não prova que o daemon funciona? Resposta: o cliente precisa conversar com o serviço que executa os contêineres.

## 2. Iniciar o cluster

```powershell
.\scripts\iniciar-cluster.ps1
kubectl config current-context
kubectl --context=ops-lab get nodes
kubectl --context=ops-lab get namespace ops-lab
```

Espere contexto ops-lab, nó Ready e namespace Active. A primeira inicialização pode demorar por causa dos downloads. Pergunta: o que muda se o contexto estiver errado? Resposta: o comando pode atingir outro cluster. Não avance nessa situação.

## 3. Construir, testar e publicar

```powershell
.\scripts\publicar-aplicacao.ps1
```

O script constrói rotas:1.0, testa a aplicação com Docker, encerra o contêiner local e carrega a imagem no nó. Depois aplica o primeiro Deployment, exclui um Pod para observar a recriação e aplica a segunda versão, o Service e o ConfigMap.

É uma sequência longa porque contém exercícios do professor. Leia as mensagens. Se parar com erro, corrija essa etapa antes de repetir cegamente o restante. Um nome de contêiner já existente pode indicar execução anterior que precisa ser investigada.

Pergunta: por que image load vem depois do teste Docker? Resposta: primeiro validamos o pacote; depois o disponibilizamos ao runtime separado do nó.

## 4. Identificar os objetos

```powershell
kubectl --context=ops-lab -n ops-lab get deployment,replicaset,pods -o wide
kubectl --context=ops-lab -n ops-lab get service rotas
kubectl --context=ops-lab -n ops-lab get endpointslices -l kubernetes.io/service-name=rotas
```

Encontre o Deployment, o ReplicaSet atual, o Pod pronto, o ClusterIP e os endpoints. Compare IPs. Não espere os nomes exatos das evidências antigas: os sufixos e endereços podem mudar.

## 5. Abrir a interface e ler os logs

```powershell
.\scripts\validar-aplicacao.ps1 -PortForward
```

Deixe o terminal aberto e visite http://localhost:8080. Escolha nove entregas, clique em Calcular rota e leia distância, tempo e Pod. Em outro PowerShell, na mesma pasta:

```powershell
kubectl --context=ops-lab -n ops-lab logs -l app=rotas --prefix --tail=3
```

Explique os totais acumulados. O tempo de um clique não substitui o teste de carga. Ctrl+C no terminal do túnel fecha o acesso local, sem apagar a aplicação.

## 6. Observar escala e reconciliação

Primeiro feche o túnel com Ctrl+C para evitar confusão se o Pod escolhido for removido.

```powershell
kubectl --context=ops-lab -n ops-lab scale deployment/rotas --replicas=3
kubectl --context=ops-lab -n ops-lab rollout status deployment/rotas --timeout=180s
kubectl --context=ops-lab -n ops-lab get pods -o wide
kubectl --context=ops-lab -n ops-lab get endpointslices -l kubernetes.io/service-name=rotas
```

Espere três Pods prontos e três destinos. Depois selecione o nome de UM Pod mostrado e use-o no comando abaixo. `NOME_DO_POD` precisa ser substituído pelo nome real:

```powershell
kubectl --context=ops-lab -n ops-lab delete pod NOME_DO_POD
kubectl --context=ops-lab -n ops-lab rollout status deployment/rotas --timeout=180s
kubectl --context=ops-lab -n ops-lab get pods
```

Observe a reposição e compare nomes/UIDs. Pergunta: quem manteve três réplicas? Resposta: o ReplicaSet, coordenado pelo Deployment. Para voltar ao estado usado no rollback:

```powershell
kubectl --context=ops-lab -n ops-lab scale deployment/rotas --replicas=1
kubectl --context=ops-lab -n ops-lab rollout status deployment/rotas --timeout=180s
```

## 7. Entender o rollback

Antes de executar, explique a previsão: imagem inexistente, Pod novo sem prontidão, antigo atendendo e restauração da versão 1.0.

```powershell
.\scripts\testar-rollback.ps1
```

Um timeout de aproximadamente 60 s faz parte da falha planejada. Observe eventos e o teste interno durante a falha. O script restaura a versão anterior em finally. Se precisar recuperar manualmente:

```powershell
kubectl --context=ops-lab -n ops-lab rollout undo deployment/rotas
kubectl --context=ops-lab -n ops-lab rollout status deployment/rotas --timeout=180s
```

## 8. Ler o experimento sem refazer tudo

Na cópia original do repositório, abra `projeto/resultados/comparativo.csv` e `projeto/resultados/logs/3pods-c.txt`. Localize rotas_ok=244, p95 e falhas. Faça 244/60 e compare com a tabela. Depois calcule a mediana de throughput de três Pods.

Pergunta: por que o Job aparece Failed se o teste é válido? Resposta: código 99 e resumo completo indicam thresholds descumpridos. Isso é resultado de desempenho, diferente de falha de execução sem resumo.

Não rode a série na cópia histórica só para aprender a conta. Se novas medições forem necessárias, use a pasta limpa de demonstração, faça piloto nesse notebook, fixe a taxa e execute a série inteira. Não reúna resultados de hosts diferentes como se fossem repetições do mesmo experimento.

## 9. Encerrar

Feche o túnel com Ctrl+C. Para apenas parar e preservar o estado:

```powershell
.\scripts\encerrar-ambiente.ps1
```

Para cumprir a limpeza do guia após salvar as evidências:

```powershell
.\scripts\encerrar-ambiente.ps1 -LimparNamespace
```

O segundo comando remove os objetos do namespace e para o perfil. Não o execute no meio da demonstração. Para a próxima apresentação, será necessário iniciar e publicar novamente.
