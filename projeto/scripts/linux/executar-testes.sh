#!/usr/bin/env bash
source "$(dirname "$0")/comum.sh"
check_cluster
# Uso: bash scripts/linux/executar-testes.sh ROTULO REPLICAS TAXA RODADA
# A calibração é manual: execute pilotos de uma réplica e fixe TAXA na série.
label="${1:?Informe rotulo}"; replicas="${2:?Informe replicas}"; rate="${3:?Informe taxa}"; round="${4:?Informe rodada}"
[[ "$label" =~ ^[a-z0-9-]+$ && "$replicas" =~ ^[123]$ && "$rate" =~ ^[1-9][0-9]*$ ]] || exit 1
dir="resultados/evidencias/$label"
test ! -e "$dir" || { echo 'Evidências já existem.'; exit 1; }
test -z "$(k get job carga --ignore-not-found -o name)" || { echo 'Salve e remova o Job anterior.'; exit 1; }
mkdir -p "$dir" resultados/logs
k scale deployment/rotas --replicas="$replicas"
k rollout status deployment/rotas --timeout=180s
k get pods -l app=rotas -o json > "$dir/pods-antes.json"
k get endpointslices -l kubernetes.io/service-name=rotas -o json > "$dir/endpointslices.json"
k logs -l app=rotas --prefix --tail=1 > "$dir/contadores-antes.txt"
python3 - "$rate" "$dir/job.yaml" <<'PY'
import re,sys
from pathlib import Path
text=Path('k8s/job-carga.yaml').read_text()
text=re.sub(r'(name: TAXA\s+value: ")[^"]+(\")',lambda m:m[1]+sys.argv[1]+m[2],text)
Path(sys.argv[2]).write_text(text)
PY
k apply -f "$dir/job.yaml"
(for i in {1..20}; do date -Is; k top pods || true; sleep 15; done) > "$dir/recursos.txt" 2>&1 &
sampler=$!
trap 'kill "$sampler" 2>/dev/null || true' EXIT
for i in {1..20}; do
  k wait --for=condition=Ready pod -l job-name=carga --timeout=10s && break || sleep 1
done
k logs -f job/carga || true
k logs job/carga > "resultados/logs/$label.txt"
k get pods -l job-name=carga -o json > "$dir/job-pods.json"
k get job carga -o json > "$dir/job-status.json"
k get events --sort-by=.lastTimestamp > "$dir/eventos.txt"
k get pods -l app=rotas -o json > "$dir/pods-depois.json"
k logs -l app=rotas --prefix --tail=1 > "$dir/contadores-depois.txt"
kill "$sampler" 2>/dev/null || true
trap - EXIT
python3 scripts/consolidar-resultados.py --importar "$label" --replicas "$replicas" --taxa "$rate" --rodada "$round"
k delete job carga
