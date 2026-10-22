# Preparar o outro notebook: Windows 11 e 16 GB de RAM

Esses recursos são suficientes para tentar o laboratório do guia, desde que virtualização, espaço em disco, permissões e backend Linux estejam funcionando. A preparação do outro notebook ainda precisa ser executada e validada nele.

## 1. O que é transferido e o que não é

O repositório transfere código, manifestos, scripts, documentação, apresentação e resultados anteriores. Ele não transfere instalações, imagens Docker, o cluster, serviços em execução, login GitHub ou a configuração do Windows.

As evidências históricas são do computador original. O notebook da apresentação só precisa reproduzir a aplicação para a demonstração, salvo exigência do professor de repetir a coleta nele.

## 2. Baixar o projeto

Use Code > Download ZIP no GitHub e extraia, ou use Git caso já esteja instalado:

```powershell
git clone https://github.com/gmmouraFag/trabalho-kubernets.git C:\RotaExpress
cd C:\RotaExpress\projeto
```

Se baixar ZIP, o GitHub pode criar uma pasta chamada trabalho-kubernets-main. Ajuste o caminho. A pasta correta para os scripts contém app.py, Dockerfile, carga.js, k8s e scripts.

## 3. Criar a pasta de ensaio

Na pasta `projeto` do repositório:

```powershell
.\scripts\preparar-demonstracao.ps1 -Destino C:\RotaExpress-demonstracao
cd C:\RotaExpress-demonstracao
```

O destino precisa não existir. O script copia as fontes e a automação, inicia uma tabela vazia e não copia os logs históricos. Assim, novos ensaios não sobrescrevem as evidências originais. A separação é de arquivos; o perfil do cluster continua ops-lab.

## 4. Diagnosticar antes de instalar

Abra Gerenciador de Tarefas > Desempenho > CPU e veja se Virtualização está habilitada. Se estiver desabilitada, pode ser necessário habilitar na BIOS/UEFI. Não altere opções desconhecidas sozinho.

Execute:

```powershell
.\scripts\verificar-ambiente.ps1
```

Identifique quais comandos faltam. Não reinstale ferramentas que já funcionam. Reserve espaço livre para imagens e downloads. Use o notebook na tomada e evite outras cargas pesadas durante a medição ou apresentação.

## 5. WSL e Docker

Se o WSL não estiver instalado, abra PowerShell como administrador:

```powershell
wsl --install --no-distribution
```

Se o Windows pedir reinício, reinicie antes de continuar. Não é necessário instalar um Ubuntu separado apenas para satisfazer o backend do Docker Desktop. No PowerShell normal, na pasta de demonstração:

```powershell
.\scripts\instalar-dependencias.ps1
```

O script instala as ferramentas ausentes via winget. Aprovações administrativas e termos do fornecedor devem ser concluídos por você. Abra o Docker Desktop, selecione backend WSL 2 se necessário e espere o mecanismo Linux iniciar.

Abra um terminal novo se os executáveis não aparecerem no PATH. Confirme:

```powershell
docker version
docker info
kubectl version --client
minikube version
```

Não avance se docker version mostrar só Client acompanhado de erro. Abra Docker manualmente sempre que necessário: inicialização automática desativada não significa desinstalação.

## 6. Publicar e testar

Na pasta C:\RotaExpress-demonstracao:

```powershell
.\scripts\iniciar-cluster.ps1
.\scripts\publicar-aplicacao.ps1
.\scripts\validar-aplicacao.ps1 -PortForward
```

O primeiro cria perfil e namespace. O segundo constrói/testa/carrega a imagem e aplica os objetos. O terceiro valida a rede interna e mantém o túnel. Abra http://localhost:8080 e calcule nove entregas.

Por que reconstruir no notebook? Porque a imagem não veio no GitHub e o runtime do nó tem seu próprio armazenamento. O Dockerfile usa a base Python do projeto, independentemente do Python instalado no Windows.

Se Python local não estiver instalado, a aplicação em contêiner ainda pode funcionar, mas as ferramentas de consolidação em Python não. Para novas medições com gráficos, instale Python compatível e prepare o ambiente auxiliar conforme a documentação de instalação. Isso é separado de simplesmente abrir a demonstração.

## 7. O ensaio que precisa passar

- Docker apresenta Server sem erro.
- Nó ops-lab fica Ready.
- Namespace ops-lab fica Active.
- Deployment fica com uma réplica pronta.
- Service tem endpoint pronto.
- Navegador calcula nove entregas.
- Logs mostram o atendimento.
- Escala para três converge e mostra três endpoints.
- Você consegue explicar o resultado original sem chamar os dados de novos resultados do notebook.
- PowerPoint e logs históricos estão disponíveis localmente, mesmo se a Internet falhar.

Faça isso antes do dia da apresentação. Os downloads iniciais precisam de Internet. Imagens já carregadas reduzem a dependência, mas não garantem funcionamento offline de todos os componentes.

## 8. Preparação no dia

Abra Docker, inicie o cluster, confirme os objetos e deixe o túnel em um terminal separado. Feche aplicações pesadas. Tenha a apresentação, os logs e o relatório abertos. Não faça atualizações de versões ou uma nova calibração minutos antes da defesa.

Se o namespace foi removido no último encerramento, publique novamente. Para uma demonstração curta, não é necessário repetir o piloto e as nove medições. Se o professor exigir a coleta nesse notebook, planeje tempo para todo o procedimento e mantenha os resultados em uma pasta identificada como novo experimento.

## 9. Plano alternativo

Se o ambiente falhar ao vivo, use as evidências reais do computador original: logs de publicação, recriação, rollback e k6, CSVs e captura da interface. Informe que são registros de uma execução anterior. Não apresente uma imagem estática como aplicação rodando naquele momento.

Os caminhos e o roteiro detalhado estão em [laboratório guiado](02-laboratorio-guiado.md) e [guia de demonstração](../projeto/documentacao/07-guia-demonstracao.md).
