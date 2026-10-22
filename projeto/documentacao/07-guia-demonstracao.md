# Demonstração ao vivo

Reserve 5 a 7 minutos. Confirme Docker aberto e cluster ligado antes de chamar o professor. Os comandos separados por ponto e vírgula abaixo são operações consecutivas para o apresentador.

## 1. Cluster

```powershell
kubectl --context=ops-lab cluster-info
```

API respondendo. Explique que kubectl faz chamadas à API.

## 2. Namespace

```powershell
kubectl --context=ops-lab get namespace ops-lab
```

Namespace Active. Organização dos objetos da atividade.

## 3. Deployment e Pods

```powershell
kubectl --context=ops-lab -n ops-lab get deploy,rs,pods -o wide
```

Compare desejado e pronto e mostre hierarquia.

## 4. Service

```powershell
kubectl --context=ops-lab -n ops-lab get service rotas; kubectl --context=ops-lab -n ops-lab get endpointslices -l kubernetes.io/service-name=rotas
```

Compare endpoints com IPs prontos.

## 5. Interface

```powershell
kubectl --context=ops-lab -n ops-lab port-forward service/rotas 8080:8000
```

Deixe em outro terminal e abra localhost:8080. Calcule nove entregas e leia nome do Pod.

## 6. Cálculo HTTP

```powershell
curl.exe "http://localhost:8080/api/rota?paradas=9"
```

JSON com ordem, distância, cálculo e Pod. Não apresentar tempo isolado como benchmark.

## 7. Logs

```powershell
kubectl --context=ops-lab -n ops-lab logs -l app=rotas --prefix --tail=3
```

Mostre totais por Pod e explique a recusa 503.

## 8. Escala

```powershell
kubectl --context=ops-lab -n ops-lab scale deployment/rotas --replicas=3; kubectl --context=ops-lab -n ops-lab rollout status deployment/rotas
```

Aguarde convergência e mostre EndpointSlices novamente. Port-forward não demonstra balanceamento.

## 9. Resultados

```powershell
Get-Content resultados/comparativo.csv; Get-Content resultados/medianas.csv
```

Use logs reais para verificar as medianas. Caso medianas não exista, declare série pendente.

## 10. Restauração

```powershell
kubectl --context=ops-lab -n ops-lab scale deployment/rotas --replicas=1
```

Restaure estado antes do encerramento. Para limpar, use encerrar-ambiente.ps1 -LimparNamespace.

## Plano alternativo

Se o Docker ou cluster falhar, apresente `resultados/logs/cluster-*.txt`, `publicacao-*.txt`, `rollback-*.txt`, os nove logs do k6 e os JSONs dos objetos. Mostre os gráficos somente se houver série completa. Explique data e condições da execução registrada. Não execute carga através do port-forward para substituir uma medição. Se o problema for só o túnel, reinicie-o após confirmar Pod pronto. Use as evidências de antes/depois para explicar reconciliação e rollback sem provocar novamente o incidente durante a defesa.
