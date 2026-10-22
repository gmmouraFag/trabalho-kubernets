# Preparação e reprodução

## Windows

Abra PowerShell na pasta `projeto`. Os instaladores foram executados pelo winget. Em outra máquina, rode `scripts/instalar-dependencias.ps1`. O script verifica os executáveis antes de instalar. Não instala k6 local. Para o WSL inicial, use PowerShell como administrador e `wsl --install --no-distribution`. Reinicie se solicitado. Abra Docker Desktop com backend WSL 2 e conclua os termos exigidos pelo fornecedor.

```powershell
.\scripts\verificar-ambiente.ps1
.\scripts\iniciar-cluster.ps1
.\scripts\publicar-aplicacao.ps1
.\scripts\validar-aplicacao.ps1
.\scripts\testar-rollback.ps1
.\scripts\executar-testes.ps1 -Modo Piloto -Taxa 6 -Rotulo piloto
```

O piloto deve ser examinado antes de fixar a série. Se houver quase só sucessos, aumente a taxa. Se houver quase nenhum sucesso e descartes, reduza. Guarde cada piloto com rótulo distinto. A taxa escolhida deve revelar diferença entre as configurações, mantendo geração sem descartes. Depois:

```powershell
.\scripts\executar-testes.ps1 -Modo Serie -Taxa TAXA_CALIBRADA -Justificativa 'Justificativa baseada nos pilotos'
.\scripts\testar-capacidade.ps1
.\.ferramentas\Scripts\python.exe scripts/consolidar-resultados.py
```

`TAXA_CALIBRADA` é uma indicação textual que deve ser substituída pelo número do piloto. O arquivo `resultados/calibracao.json`, quando existir, guarda o valor efetivamente fixado e hashes das fontes. Não reaplique deployment.yaml durante a série: isso voltaria a uma réplica.

Para abrir a interface em um terminal separado:

```powershell
.\scripts\validar-aplicacao.ps1 -PortForward
```

Abra http://localhost:8080, calcule nove entregas e confira o Pod mostrado. O túnel precisa continuar ativo. Ctrl+C fecha o túnel. Para encerrar o cluster preservando seu estado, execute `scripts/encerrar-ambiente.ps1`. Com `-LimparNamespace`, o script também remove os objetos da atividade, conforme o Grupo 8.5. Não apaga o perfil nem outros clusters.

## Ubuntu 22.04 ou superior

Os comandos Docker, Minikube e kubectl são iguais. Instale Docker Engine pelo repositório oficial de sua distribuição seguindo https://docs.docker.com/engine/install/ubuntu/. Não execute automaticamente scripts remotos como root. Após a instalação, `sudo usermod -aG docker "$USER"` permite usar o daemon, mas confere privilégios elevados sobre o host; saia e entre novamente na sessão. Instale kubectl por `sudo snap install kubectl --classic`, conforme o guia, ou pelo repositório oficial. Baixe `minikube_latest_amd64.deb` do servidor oficial e instale com `sudo dpkg -i minikube_latest_amd64.deb`.

Use os comandos do documento 03 na ordem. Troque `curl.exe` por `curl`. YAML e JavaScript são os mesmos. Os scripts PowerShell podem rodar com PowerShell 7 no Linux, exceto diagnóstico e instalação, que usam APIs Windows. Os equivalentes Bash de instalação não foram executados neste computador e estão marcados como não validados. Nunca rode Minikube com driver Docker como root.

## Validação e dependências auxiliares

```powershell
python -m venv .ferramentas
.\.ferramentas\Scripts\python.exe -m pip install -r scripts/requirements-validacao.txt
.\.ferramentas\Scripts\python.exe scripts/validar-estatico.py
```

O teste estático verifica nomes, portas, requests e preservação dos originais. O teste HTTP local cobre respostas 200, 400, 404 e 503. A validação de esquema no servidor Kubernetes é separada e usa `kubectl apply --dry-run=server -f ARQUIVO`.

Fontes oficiais consultadas para a instalação: https://docs.docker.com/desktop/setup/install/windows-install/ e https://learn.microsoft.com/en-us/windows/wsl/basic-commands. Os parâmetros acadêmicos prevalecem sobre mudanças opcionais de produção.
