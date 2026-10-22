# Diagnóstico e instalação
Atualizado em 21/10/2026. Fonte principal: Guia_Atividade.pdf, na pasta acima. Fundamentação: Aula_Kubernetes.pdf.


## Equipamento observado

Windows 11 Pro 25H2, build 26200 (10.0.26200.9711), x64. AMD Ryzen 5 7600X, 6 núcleos e 12 processadores lógicos. RAM física: 31,11 GB. Espaço livre inicial no C: aproximadamente 361,54 GB. Virtualização de firmware habilitada e hypervisor presente. A sessão original não tinha privilégios administrativos.

## Ferramentas

| Ferramenta | Estado e versão |
|---|---|
| Python | Já instalado, 3.14.5. A imagem da aplicação usa Python 3.12, conforme o professor. |
| Git | Já instalado, 2.54.0.windows.1. |
| winget | Já instalado, 1.29.380. |
| kubectl | Instalado pelo winget, 1.37.1. |
| Minikube | Instalado pelo winget, 1.39.0. |
| Docker Desktop | Instalado pelo winget, 4.96.0.243774. Engine e cliente 29.9.1. |
| WSL | Instalado pelo usuário com administrador, 3.0.3.0, kernel 6.18.54.1. |
| Ferramentas de validação | Ambiente local `.ferramentas`, PyYAML 6.0.3 e matplotlib 3.11.2. |
| k6 | Previsto e executado somente no cluster, imagem fixa grafana/k6:1.0.0. Consulte os logs para confirmar cada execução. |

O primeiro `wsl --install --no-distribution` não instalou o componente. A alternativa via winget retornou 0x80073d28, exigindo administrador. O usuário executou o comando elevado, habilitou VirtualMachinePlatform e reiniciou. Após o reinício, `docker version` apresentou Client e Server e `wsl --status` confirmou versão padrão 2 e docker-desktop. Não foi necessário instalar Ubuntu separado: Docker Desktop mantém sua própria distribuição.

## Rede, PATH e permissões

Foram feitas solicitações HEAD aos servidores oficiais Docker, Kubernetes, Minikube e Microsoft/WSL, todas HTTP 200. Isso confirma conectividade HTTPS inicial, não garante todo download de imagem. Não foram alterados proxy nem firewall. DOCKER_HOST e KUBECONFIG estavam vazios. Os scripts atualizam o PATH apenas no processo, lendo os caminhos já registrados pelos instaladores. O kubeconfig é gerenciado pelo Minikube.

## Evidências

`resultados/evidencias/diagnostico.json` contém inventário e PATH. `conectividade.json` contém os testes de rede. Os arquivos `resultados/logs/diagnostico-*.txt` registram versões, erros e verificações. `cluster-*.txt` registra a configuração real do runtime. `originais/` preserva os seis arquivos recebidos e hashes SHA-256.

## Limitações de interpretação

O teste Python local valida HTTP e lógica no Windows. Seus tempos não são o piloto k6 e não devem entrar na comparação Kubernetes. O Docker enxerga 12 CPUs e cerca de 15 GiB na VM; o nó do experimento recebe somente 3 CPUs e 3072 MiB. Request de CPU é capacidade declarada para agendamento, não medida de consumo efetivo.
