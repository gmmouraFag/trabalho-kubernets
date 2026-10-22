#!/usr/bin/env bash
source "$(dirname "$0")/comum.sh"
check_cluster
k rollout status deployment/rotas --timeout=180s
k get endpointslices -l kubernetes.io/service-name=rotas
k run "teste-$(date +%H%M%S)" --rm -i --restart=Never --image=busybox:1.36 -- wget -qO- http://rotas:8000/healthz
if test "${1:-}" = --port-forward; then k port-forward --address=127.0.0.1 service/rotas 8080:8000; fi
