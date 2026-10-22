#!/usr/bin/env bash
source "$(dirname "$0")/comum.sh"
check_cluster
if test "${1:-}" = --limpar-namespace; then k delete namespace ops-lab; fi
minikube stop -p ops-lab
