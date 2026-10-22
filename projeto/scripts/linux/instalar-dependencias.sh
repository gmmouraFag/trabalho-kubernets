#!/usr/bin/env bash
source "$(dirname "$0")/comum.sh"
# Ubuntu amd64. Não executado no host Windows desta entrega.
test "$(uname -m)" = x86_64 || { echo 'Este instalador exige amd64.'; exit 1; }
source /etc/os-release
test "$ID" = ubuntu || { echo 'Este instalador exige Ubuntu.'; exit 1; }
if ! command -v docker >/dev/null; then
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  printf 'Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: %s\nComponents: stable\nArchitectures: amd64\nSigned-By: /etc/apt/keyrings/docker.asc\n' "$VERSION_CODENAME" | sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER"
  echo 'Saia e entre na sessão para ativar o grupo docker.'
fi
tmpdir="$(mktemp -d)"
if ! command -v kubectl >/dev/null; then
  curl -fsSL https://dl.k8s.io/release/v1.37.1/bin/linux/amd64/kubectl -o "$tmpdir/kubectl"
  curl -fsSL https://dl.k8s.io/release/v1.37.1/bin/linux/amd64/kubectl.sha256 -o "$tmpdir/kubectl.sha256"
  (cd "$tmpdir"; echo "$(cat kubectl.sha256)  kubectl" | sha256sum -c -)
  sudo install -m 0755 "$tmpdir/kubectl" /usr/local/bin/kubectl
fi
if ! command -v minikube >/dev/null; then
  curl -fsSL https://storage.googleapis.com/minikube/releases/v1.39.0/minikube-linux-amd64 -o "$tmpdir/minikube"
  curl -fsSL https://storage.googleapis.com/minikube/releases/v1.39.0/minikube-linux-amd64.sha256 -o "$tmpdir/minikube.sha256"
  (cd "$tmpdir"; echo "$(cat minikube.sha256)  minikube" | sha256sum -c -)
  sudo install -m 0755 "$tmpdir/minikube" /usr/local/bin/minikube
fi
python3 --version
echo 'Arquivos temporários preservados em:' "$tmpdir"
