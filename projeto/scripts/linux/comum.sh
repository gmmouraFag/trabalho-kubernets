#!/usr/bin/env bash
set -euo pipefail
LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$LAB_ROOT"
k() { kubectl --context=ops-lab --namespace=ops-lab "$@"; }
check_cluster() {
  test "$(kubectl config view -o 'jsonpath={.contexts[?(@.name=="ops-lab")].context.cluster}')" = ops-lab
  minikube status -p ops-lab
}
