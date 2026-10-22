#!/usr/bin/env bash
source "$(dirname "$0")/comum.sh"
mkdir -p resultados/logs
{
  uname -a
  cat /etc/os-release
  lscpu
  free -h
  df -h .
  for tool in docker kubectl minikube python3 git; do command -v "$tool" || true; done
  docker version || true
  docker info || true
  kubectl version --client || true
  minikube version || true
  python3 --version || true
} 2>&1 | tee "resultados/logs/diagnostico-linux-$(date +%Y%m%d-%H%M%S).txt"
