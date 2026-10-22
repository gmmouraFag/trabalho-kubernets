#!/usr/bin/env bash
source "$(dirname "$0")/comum.sh"
docker version
minikube start -p ops-lab --driver=docker --cpus=3 --memory=3072
minikube profile ops-lab
test "$(kubectl config current-context)" = ops-lab
k apply -f k8s/namespace.yaml
kubectl config set-context ops-lab --namespace=ops-lab
minikube addons enable metrics-server -p ops-lab
k wait --for=condition=Ready node/ops-lab --timeout=180s
k get nodes -o wide
k get pods -A
