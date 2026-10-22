#!/usr/bin/env bash
source "$(dirname "$0")/comum.sh"
check_cluster
docker build -t rotas:1.0 .
docker run -d --rm -p 127.0.0.1:8000:8000 --name rotas-teste rotas:1.0
trap 'docker stop rotas-teste || true' EXIT
for i in {1..30}; do curl -fsS http://localhost:8000/healthz && break || sleep 1; done
for endpoint in / /healthz /readyz '/api/rota?paradas=9'; do curl -fsS "http://localhost:8000$endpoint"; done
docker logs rotas-teste
docker stop rotas-teste
trap - EXIT
minikube image load rotas:1.0 -p ops-lab
k apply -f k8s/versoes/deployment-inicial.yaml
k rollout status deployment/rotas --timeout=180s
k get deploy,rs,pods
k delete pod -l app=rotas
k rollout status deployment/rotas --timeout=180s
k apply -f k8s/deployment.yaml
k rollout status deployment/rotas --timeout=180s
k apply -f k8s/service.yaml
k create configmap carga-script --from-file=carga.js --dry-run=client -o yaml | k apply -f -
