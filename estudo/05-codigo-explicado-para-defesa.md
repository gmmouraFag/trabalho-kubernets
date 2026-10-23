# Entenda o código e explique ao professor

Este é o seu guia de estudo do código que está neste repositório. Abra o arquivo original ao lado de cada explicação. Os trechos abaixo destacam o que estudar; não são arquivos substitutos. O código funcional e os resultados anteriores foram preservados.

**Sua primeira explicação:** “A aplicação recebe uma quantidade de entregas, testa todas as ordens possíveis e devolve o menor circuito em linha reta, saindo e voltando ao depósito. Cada processo permite somente um cálculo por vez. Docker empacota a aplicação; Kubernetes mantém as réplicas e oferece um endereço de serviço; k6 gera pedidos para medir o comportamento sob carga.”

## 1. O mapa dos arquivos

| Arquivo | Responsabilidade | Onde executa |
|---|---|---|
| [app.py](../projeto/app.py) | Servidor HTTP, cálculo da rota e página com o mapa | Python, dentro de cada contêiner da aplicação |
| [carga.js](../projeto/carga.js) | Geração de requisições e métricas | k6, em um Job separado |
| [Dockerfile](../projeto/Dockerfile) | Instruções para construir a imagem da aplicação | Docker, na construção |
| [.dockerignore](../projeto/.dockerignore) | Define o que entra no contexto da construção | Docker |
| [k8s](../projeto/k8s) | Estado desejado de aplicação, rede e teste | Interpretado pela API e pelos controladores Kubernetes |
| [scripts](../projeto/scripts) | Instalação, publicação, coleta e análise | Principalmente PowerShell e Python no computador do operador |
| [resultados](../projeto/resultados) | Evidências e dados coletados | Arquivos para análise e entrega |

Há dois códigos JavaScript com papéis diferentes: o JavaScript dentro de `PAGINA` executa no navegador; `carga.js` executa no k6. Não há Node.js ou banco de dados na aplicação. A biblioteca padrão do Python atende o servidor e o cálculo.

### Caminho de uma solicitação

```text
Navegador ou k6
      | GET /api/rota?paradas=9
      v
Service rotas:8000 (quando o acesso passa pelo Service)
      |
      v
um Pod pronto -> Handler.do_GET() -> valida parâmetro -> tenta VAGA
                                                       | livre: calcula -> 200 + JSON
                                                       | ocupada: 503 + JSON de erro
```

No teste local em Python, o cliente acessa diretamente o servidor. No laboratório, `kubectl port-forward service/rotas ...` permite abrir a aplicação no computador e encaminha o acesso a um Pod selecionado; não serve para demonstrar distribuição entre todos os Pods. O k6 dentro do cluster usa o Service `http://rotas:8000`.

## 2. Python: como ler a sintaxe que aparece aqui

| Construção | Significado no projeto |
|---|---|
| `import` / `from ... import` | Carregam bibliotecas ou nomes específicos |
| `def nome(...)` | Define uma função; o corpo executa quando ela é chamada |
| Indentação | Define quais instruções pertencem à função, condição ou laço |
| `return` | Entrega um resultado e encerra aquela chamada |
| Lista `[a, b]` / tupla `(a, b)` | Sequência; as coordenadas são pares e os pontos formam uma lista |
| Dicionário `{'chave': valor}` | Agrupa dados por nome; depois pode virar JSON |
| `for`, `if`, `else` | Repetição e decisão |
| `try`, `except`, `finally` | Tentativa, tratamento de erro e limpeza garantida |
| `with` | Gerencia um recurso; aqui, libera a trava ao sair do bloco |
| `class Handler(...)` | Define uma classe que aproveita comportamento da classe base |
| `self` | Referência ao objeto que está atendendo a requisição |
| `f'...{valor}...'` | Texto que incorpora valores de variáveis |

Não precisa decorar a tabela. Localize uma ocorrência de cada construção no arquivo e explique o que ela faz naquele ponto.

## 3. `app.py`: bibliotecas e estado inicial

O texto entre três aspas no início é uma documentação do módulo. Ele declara o limite do problema: pontos fictícios, sem ruas ou trânsito, para um protótipo didático.

| Importação | Uso efetivo |
|---|---|
| `itertools` | Gera permutações das entregas |
| `json` | Transforma dicionários em JSON nas respostas |
| `math` | Calcula distância entre coordenadas |
| `os` | Lê `HOSTNAME` e `PORT` do ambiente |
| `socket` | Obtém o hostname como alternativa |
| `threading` | Fornece semáforo e trava dos contadores |
| `time` | Mede a duração do cálculo |
| `BaseHTTPRequestHandler` | Base do tratamento HTTP |
| `ThreadingHTTPServer` | Servidor que atende conexões usando threads |
| `urlparse`, `parse_qs` | Separam caminho e parâmetros da URL |

### `PONTOS`, `POD`, `VAGA` e contadores

```python
POD = os.getenv('HOSTNAME', socket.gethostname())
VAGA = threading.BoundedSemaphore(1)
CONTAGEM = {'aceitos': 0, 'recusados': 0}
TRAVA_CONTAGEM = threading.Lock()
```

- `PONTOS` guarda dez pares de coordenadas. O índice 0 é o depósito; os demais são entregas. Com nove paradas, são dez pontos no circuito.
- `POD` lê o hostname do ambiente ou do sistema. No Kubernetes, normalmente identifica o Pod; fora dele, pode identificar a máquina ou o contêiner. Não é uma consulta à API Kubernetes.
- `VAGA` é um semáforo com uma permissão. Cada processo tem sua própria vaga. Não existe uma trava única compartilhada entre todos os Pods.
- `CONTAGEM` acumula pedidos aceitos e recusados durante a vida do processo. Reiniciar o processo perde esses valores; não há persistência em banco.
- `TRAVA_CONTAGEM` impede duas threads de alterarem os contadores ao mesmo tempo. Ela protege os números; `VAGA` limita os cálculos. São responsabilidades diferentes.

**Fala sugerida:** “O servidor aceita conexões em threads, mas o semáforo permite somente um cálculo ativo por processo. Com mais Pods, temos mais processos e mais vagas independentes.”

## 4. `registrar(evento, detalhe='')`: o log

1. Recebe `aceitos` ou `recusados` e um detalhe opcional.
2. Entra na trava com `with TRAVA_CONTAGEM`.
3. Incrementa o contador correspondente e copia os dois totais.
4. Sai da trava e imprime uma linha, usando `flush=True` para liberar a saída imediatamente.

`evento[:-1]` remove o último caractere: `aceitos` aparece como `aceito`, por exemplo. Isso é formatação; o nome usado no dicionário continua no plural.

Uma linha ilustrativa seria:

```text
aceito calculo_ms=400.0 total_aceitos=12 total_recusados=5
```

O Kubernetes coleta a saída padrão do contêiner, consultável com `kubectl logs`. Os scripts comparam contadores antes e depois de um teste para estimar a distribuição do atendimento.

**Limite:** o `print` fica fora da trava. Os incrementos são protegidos, mas threads podem imprimir em ordem diferente da atualização. Além disso, o contador aceito é registrado depois da tentativa de envio; não comprova que o cliente recebeu e validou a resposta. Por isso a medição principal usa as métricas do k6, e os contadores dos Pods ajudam a interpretar a distribuição.

## 5. `calcular_rota(paradas)`: o algoritmo completo

### 5.1 Escolher pontos e preparar distâncias

```python
pontos = PONTOS[:paradas + 1]
dist = [[math.dist(a, b) for b in pontos] for a in pontos]
melhor = float('inf')
ordem = None
```

O fatiamento pega o depósito e a quantidade solicitada de entregas. Com `paradas=3`, pega os índices 0, 1, 2 e 3. O limite final do fatiamento não é incluído.

A compreensão de listas dupla cria uma matriz. `dist[a][b]` dá a distância do ponto de índice `a` ao de índice `b`. Isso evita recalcular raízes quadradas para cada candidato. A distância euclidiana entre `(x1,y1)` e `(x2,y2)` é `sqrt((x2-x1)² + (y2-y1)²)`.

`float('inf')` representa infinito: qualquer primeira rota válida será melhor. `ordem=None` indica que ainda não há uma solução escolhida. A função pressupõe uma entrada válida; quem verifica a faixa é o atendimento HTTP.

### 5.2 Enumerar e comparar circuitos

```python
for rota in itertools.permutations(range(1, len(pontos))):
    total = dist[0][rota[0]] + dist[rota[-1]][0]
    for a, b in zip(rota, rota[1:]):
        total += dist[a][b]
    if total < melhor:
        melhor, ordem = total, rota
```

- `range(1, len(pontos))` inclui as entregas e deixa o depósito fora da permutação.
- `permutations` gera todas as ordens possíveis, uma por vez.
- `rota[0]` é a primeira entrega; `rota[-1]`, a última.
- A primeira soma inclui a saída do depósito e o retorno a ele.
- `zip(rota, rota[1:])` forma pares de entregas consecutivas. Para `(1,3,2)`, produz `(1,3)` e `(3,2)`.
- O laço interno soma os deslocamentos entre entregas.
- Se o total for menor, a atribuição simultânea guarda distância e ordem. Como usa `<`, um empate mantém a primeira ordem encontrada.

Exemplo de leitura com três entregas: o candidato `(1,3,2)` representa `0 → 1 → 3 → 2 → 0`. Seu total é `dist[0][1] + dist[1][3] + dist[3][2] + dist[2][0]`. Esse exemplo explica uma tentativa; não afirma que ela é a vencedora.

### 5.3 Montar o resultado

```python
return {'pontos': pontos, 'ordem': [0, *ordem, 0],
        'distancia': round(melhor, 2), 'paradas': paradas}
```

`*ordem` expande a sequência dentro da lista. O resultado inclui o depósito no começo e no fim. A distância é arredondada somente na saída; as comparações anteriores usam os valores sem esse arredondamento.

### 5.4 Por que esse cálculo pesa?

Com `n` entregas, existem `n!` ordens. São 6 para três entregas, 5.040 para sete, 40.320 para oito e 362.880 para nove. Cada candidato ainda exige somas proporcionais a `n`: o custo de tempo cresce como `O(n × n!)`.

A matriz ocupa espaço proporcional a `(n+1)²`. O gerador não guarda uma lista com todas as permutações. Como as distâncias são simétricas, um circuito e seu inverso têm o mesmo tamanho; esta implementação testa ambos. Não usa heurística, cache nem poda de candidatos.

**Fala sugerida:** “É uma busca exata: testa todas as ordens e escolhe a menor. É adequada ao exercício pequeno, mas o crescimento fatorial inviabiliza simplesmente aumentar muito a quantidade de entregas.”

## 6. `PAGINA`: HTML, CSS e JavaScript no mesmo arquivo

`PAGINA` é uma string Python com um documento HTML. O Python envia esse texto; o navegador interpreta o HTML, aplica o CSS e executa o JavaScript.

| Parte | Função |
|---|---|
| `lang="pt-BR"`, `charset="utf-8"`, `title` | Idioma, codificação e título |
| `<style>` | Aparência: cores, espaçamentos, fontes e dimensões |
| `<select id="n">` | Escolha de 7, 8 ou 9 entregas; 9 vem selecionado |
| `<button id="go">` | Dispara a consulta |
| `<p id="info">` | Mostra instruções, resultado ou erro |
| `<svg id="mapa">` | Área vetorial para desenhar pontos e circuito |

### O clique, na ordem em que acontece

1. `document.querySelector('#go').onclick=async()=>{...}` associa uma função assíncrona ao botão. `#` seleciona um elemento pelo identificador.
2. A função obtém `#info` e mostra “Calculando…”.
3. `fetch('/api/rota?paradas='+...value)` pede ao mesmo servidor uma rota com a opção selecionada. O caminho relativo acompanha o endereço por onde a página foi aberta.
4. `await` espera a resposta e, depois, sua leitura como JSON. O cálculo continua no servidor; não foi transferido para o navegador.
5. `if(!r.ok) throw Error(d.erro)` encaminha um status de erro ao `catch`. `fetch` não lança automaticamente uma exceção só porque recebeu HTTP 503.
6. O texto com crases e `${...}` exibe distância, tempo de cálculo e Pod que respondeu.
7. `d.ordem.map(...)` troca índices por coordenadas; `join(',')` e `join(' ')` montam os pares para a `<polyline>`, que desenha o circuito.
8. `forEach` acrescenta um `<circle>` e um `<text>` para cada ponto. O operador `i===0 ? ... : ...` escolhe vermelho para o depósito e verde para entregas.
9. `innerHTML=s` coloca o desenho no SVG. Se houver erro, `catch(e)` escreve a mensagem em `#info`.

O `viewBox="0 0 110 110"` define o espaço de coordenadas do desenho. São unidades fictícias, não quilômetros. A API permite de 3 a 9 entregas; a interface oferece somente 7 a 9. A validação no servidor continua necessária, pois qualquer cliente pode montar uma URL manualmente.

**Limite da interface:** o botão não é desabilitado durante o pedido. Clicar novamente pode gerar outra requisição e receber 503. Os pontos são fixos e produzidos pelo próprio servidor; esta página não é um exemplo de tratamento geral de HTML fornecido por usuários.

## 7. `Handler`: receber pedidos e responder

`Handler(BaseHTTPRequestHandler)` aproveita o processamento básico HTTP da biblioteca e define o comportamento específico da aplicação. `protocol_version='HTTP/1.1'` escolhe a versão usada nas respostas.

### `log_message(self, fmt, *args)`

O método existe na classe base. Aqui ele é sobrescrito com `pass`, que não faz nada. Isso silencia os registros automáticos de acesso, especialmente os frequentes checks de saúde. Os logs de aceito/recusado continuam porque usam `registrar`.

### `responder(self, status, dados, tipo=...)`

Este método centraliza o envio:

1. Se `dados` já é texto, codifica em bytes UTF-8. Caso contrário, serializa com `json.dumps` e codifica. HTML usa o primeiro caminho; dicionários usam o segundo.
2. `send_response(status)` inicia a resposta com seu código HTTP.
3. Envia os cabeçalhos: `Content-Type` informa o formato; `Content-Length` informa o tamanho em bytes; `X-Pod` identifica quem respondeu; `Connection: close` anuncia encerramento da conexão.
4. `end_headers()` encerra os cabeçalhos.
5. `self.wfile.write(corpo)` escreve o corpo no fluxo de saída.
6. Se o cliente já fechou a conexão, `BrokenPipeError` ou `ConnectionResetError` é ignorado. Isso não garante entrega ao cliente.
7. `self.close_connection=True` determina o encerramento da conexão após o atendimento.

`Content-Length` usa `len(corpo)` depois da codificação porque caracteres acentuados podem ocupar mais de um byte. A aplicação usa HTTP/1.1, mas fecha explicitamente cada conexão.

### `do_GET(self)`: a sequência de decisões

`urlparse(self.path)` separa, por exemplo, `/api/rota` de `paradas=9`. O servidor chama `do_GET` quando recebe o método GET.

| Caminho/condição | Resposta | Calcula rota? |
|---|---|---|
| `/healthz` ou `/readyz` | 200 com status e identificação | Não |
| `/` | 200 com HTML | Não |
| Caminho GET desconhecido | 404 com erro | Não |
| `/api/rota` com parâmetro inválido | 400 com orientação | Não |
| `/api/rota` válido, vaga ocupada | 503 com erro e identificação | Não |
| `/api/rota` válido, vaga livre | 200 com resultado | Sim |

Os `return` encerram cada ramo, evitando que a execução continue até o cálculo. Métodos como POST não foram implementados; o tratamento padrão da classe base responde 501.

### Validação do parâmetro

```python
n = int(parse_qs(url.query).get('paradas', ['9'])[0])
if not 3 <= n <= 9:
    raise ValueError
```

`parse_qs` devolve um dicionário de listas, pois uma chave pode aparecer mais de uma vez. `.get(..., ['9'])` usa 9 quando a chave está ausente, e `[0]` escolhe seu primeiro valor. `int` converte texto para inteiro. Uma conversão impossível ou um valor fora de 3 a 9 cai no `except ValueError` e retorna 400.

Exemplos: `?paradas=3` é aceito; `?paradas=2`, `?paradas=10` e `?paradas=abc` retornam 400. Sem parâmetro, usa 9. Com o comportamento padrão de `parse_qs`, um valor vazio em `?paradas=` é descartado e também leva ao padrão 9. Outros parâmetros são ignorados.

### A vaga e a resposta 503

```python
if not VAGA.acquire(blocking=False):
    registrar('recusados')
    return self.responder(503, ...)
```

`acquire` tenta obter a permissão. `blocking=False` manda retornar imediatamente se ela estiver ocupada. O pedido é recusado sem esperar numa fila de cálculos da aplicação.

Não confunda isso com ausência de qualquer fila de rede ou do servidor: o que o código evita é esperar pela vaga do calculador. O Service encaminha conexões aos endpoints disponíveis e não consulta esse semáforo. Ele pode escolher um Pod pronto que já está ocupado, mesmo havendo outra vaga livre em outro Pod.

### Cálculo protegido por `try/finally`

Após obter a vaga, o código marca `inicio=time.perf_counter()`, chama `calcular_rota(n)` e acrescenta `pod` e `calculo_ms` ao dicionário com `resultado.update(...)`. A diferença entre os relógios é multiplicada por mil para virar milissegundos e arredondada para uma casa decimal.

Depois envia 200 e registra o atendimento. No `finally`, `VAGA.release()` devolve a permissão mesmo se ocorrer uma exceção no bloco. Um semáforo limitado também detecta liberações além de sua capacidade.

**Distinção para a defesa:** `calculo_ms` mede o trecho de cálculo no servidor, com pequeno custo de instrumentação; a latência HTTP do k6 mede o pedido do ponto de vista do cliente, incluindo envio, espera e recebimento. Não são a mesma medida.

Não existe um `except` geral que transforme toda falha inesperada em JSON com status 500. O `finally` garante a liberação; ele não resolve automaticamente a causa de uma exceção.

## 8. Inicialização: quando o servidor começa

```python
if __name__ == '__main__':
    porta = int(os.getenv('PORT', '8000'))
    print(f'RotaExpress em http://localhost:{porta}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', porta), Handler).serve_forever()
```

O bloco executa ao iniciar `python app.py`. Ao importar o módulo para uma verificação, ele não inicia automaticamente o servidor. `PORT` pode substituir 8000. Um valor não numérico causa erro na inicialização.

`0.0.0.0` permite escutar nas interfaces do ambiente onde o processo roda. Dentro do contêiner, isso permite receber o tráfego encaminhado ao contêiner. A exposição para fora ainda depende de portas, Service, encaminhamento e rede. `serve_forever` mantém o laço de atendimento até o servidor ser encerrado.

Usar threads não significa que este processo fará vários cálculos Python em paralelo: o próprio semáforo restringe a um, e o ambiente de execução também importa para trabalho de CPU. As threads permitem tratar conexões e caminhos leves enquanto existe um cálculo, sem garantir resposta instantânea sob saturação.

## 9. `carga.js`: como o experimento faz pedidos

Abra [carga.js](../projeto/carga.js). O k6 executa esse JavaScript usando suas próprias bibliotecas `k6/http` e `k6/metrics`.

### Parâmetros e métricas

`__ENV` contém variáveis de ambiente. `||` escolhe um padrão quando o valor não foi fornecido. `Number(...)` converte taxa e duração para números.

| Nome | Padrão | Uso |
|---|---|---|
| `URL` | `http://rotas:8000` | Endereço do Service, resolvido dentro do namespace |
| `TAXA` | 6 | Iterações iniciadas por segundo; cada uma faz um pedido |
| `PARADAS` | `9` | Entregas solicitadas |
| `DURACAO` | 60 | Segundos da janela de medição |
| `Counter('rotas_ok')` | Contador | Número de respostas consideradas válidas |
| `Rate('falhas')` | Proporção | Fração das tentativas medidas sem resposta válida |
| `Trend('latencia_ok', true)` | Distribuição de tempos | Duração HTTP somente dos sucessos |

`rotasOk` é o nome da variável no JavaScript; `rotas_ok` é o nome da métrica emitida. O segundo argumento `true` do Trend indica uma métrica de tempo. Não é uma meta de aprovação.

### `cenario` e `options`

`constant-arrival-rate` tenta manter a taxa de início de iterações independentemente de cada resposta. `rate=TAXA` e `timeUnit='1s'` definem a demanda. `preAllocatedVUs=40` e `maxVUs=40` disponibilizam clientes virtuais; não significam 40 Pods nem 40 pedidos/s.

O operador `...cenario` copia as propriedades comuns para os dois cenários:

```text
0 s                  10 s                 20 s                     80 s
|---- aquecimento ----|---- intervalo ----|------ medição 60 s ------|
```

`aquecer()` só chama `pedirRota()`, sem alimentar as três métricas próprias. `medir()` começa aos 20 s. `gracefulStop='10s'` permite terminar iterações pendentes após o período do cenário; o tempo total de execução pode ultrapassar o fim nominal da medição.

`noConnectionReuse=true` abre conexões novas; isso favorece novas escolhas de endpoint pelo Service. Não garante alternância nem quantidades exatamente iguais por Pod. `summaryTrendStats` escolhe média, mediana, p95 e máximo para o resumo.

### `pedirRota()`, `aquecer()` e `medir()`

`pedirRota()` monta `/api/rota?paradas=...` e faz GET com timeout de 5 s. Esse timeout é diferente da meta de p95 de 800 ms.

Em `medir()`, o JSON é lido num `try/catch`; uma resposta que não seja JSON deixa `corpo=null`. A variável `ok` exige status 200, corpo não nulo e `ordem` como array. Essa verificação identifica a estrutura esperada, mas não demonstra matematicamente que a rota é ótima.

`falhas.add(!ok)` registra um valor em toda tentativa medida: verdadeiro representa falha. Se `ok`, soma uma rota ao contador e adiciona `r.timings.duration` à distribuição de latência. Um 503 rápido não entra no p95 dos sucessos.

### Critérios de aprovação

| Threshold | Leitura correta |
|---|---|
| `falhas: ['rate<0.01']` | Menos de 1% de falhas; exatamente 1% não passa |
| `latencia_ok: ['p(95)<800']` | p95 dos pedidos válidos abaixo de 800 ms |
| `dropped_iterations{scenario:medicao}: ['count==0']` | Nenhuma iteração de medição descartada pelo gerador |

Uma iteração descartada não chegou a fazer o pedido planejado. Um HTTP 503 chegou à aplicação e recebeu recusa. São fenômenos diferentes. As métricas HTTP gerais do resumo podem incluir aquecimento; as três métricas próprias foram instrumentadas para a medição.

Quando thresholds falham, o k6 pode sair com código 99, e o Job aparece como Failed. Isso pode ser uma execução válida que demonstrou desempenho insuficiente. É necessário olhar logs e estado do contêiner antes de concluir a causa.

## 10. Docker: explicar cada instrução

Abra o [Dockerfile](../projeto/Dockerfile).

| Instrução | Explicação |
|---|---|
| `FROM python:3.12-slim` | Parte de uma imagem com Python e base Linux reduzida |
| `WORKDIR /app` | Define o diretório de trabalho dentro da imagem |
| `COPY app.py .` | Copia a aplicação para `/app/app.py` |
| `ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1` | Libera saída sem buffer e evita gerar arquivos de bytecode `.pyc` |
| `USER 10001:10001` | Executa com UID e GID numéricos sem usar root |
| `EXPOSE 8000` | Documenta a porta pretendida; sozinho não publica a porta |
| `CMD ["python", "app.py"]` | Comando padrão ao iniciar o contêiner, em formato de lista |

Não existe `pip install`: a aplicação só usa a biblioteca padrão. A versão Python do contêiner vem do `FROM`; pode ser diferente da versão instalada no Windows.

O [.dockerignore](../projeto/.dockerignore) começa com `*`, excluindo tudo, e abre exceções com `!app.py` e `!Dockerfile`. PDFs, resultados e documentação não entram no contexto enviado para construir essa imagem.

**Fala sugerida:** “A imagem é o pacote construído com essas instruções. O contêiner é uma execução desse pacote. O Pod envolve essa execução no Kubernetes. Alterar um arquivo no Windows não muda automaticamente uma imagem já construída.”

## 11. Kubernetes: ler os manifestos sem decorar YAML

Em YAML, indentação expressa hierarquia; `-` inicia um item de lista. Os manifestos declaram estado desejado. `kubectl apply` envia esse estado; controladores trabalham para alcançá-lo.

### [namespace.yaml](../projeto/k8s/namespace.yaml)

`apiVersion: v1`, `kind: Namespace`, `metadata.name: ops-lab` criam a área lógica do laboratório. Namespace organiza nomes e recursos; sua criação, isoladamente, não instala uma política de isolamento de rede.

### [deployment.yaml](../projeto/k8s/deployment.yaml)

| Campo | Por que existe |
|---|---|
| `apiVersion: apps/v1`, `kind: Deployment` | Identificam o tipo de recurso e sua API |
| `metadata.name: rotas`, `namespace: ops-lab` | Nome e localização lógica |
| `spec.replicas: 1` | Quantidade inicial desejada; o experimento usa escala para 1, 2 e 3 |
| `selector.matchLabels.app: rotas` | Identifica os Pods gerenciados |
| `template.metadata.labels.app: rotas` | Rótulo aplicado aos Pods criados |
| `template.spec.containers` | Descrição do contêiner de aplicação |
| `image: rotas:1.0` | Imagem usada, previamente carregada no Minikube |
| `imagePullPolicy: IfNotPresent` | Usa imagem local se presente; caso contrário, tenta obter a imagem |
| `ports.containerPort: 8000` | Declara a porta do contêiner; não cria publicação externa |

O Deployment gerencia ReplicaSets, que mantêm os Pods. Ao excluir um Pod, o controlador cria outro para atender ao número desejado. O novo Pod não recupera os contadores em memória do antigo.

`requests.cpu: 500m` equivale a 0,5 CPU e participa do agendamento; `limits.cpu: 500m` limita o consumo de CPU do contêiner. Request não significa consumo permanente. `requests.memory: 64Mi` e `limits.memory: 128Mi` tratam memória, em mebibytes. Exceder limite de memória pode provocar encerramento por falta de memória; limitação de CPU tende a restringir tempo de processamento.

`readinessProbe` consulta `/readyz` a cada 5 s para indicar se o Pod deve receber tráfego do Service. `livenessProbe` consulta `/healthz`, com início após 10 s e período de 10 s; falhas consecutivas podem provocar reinício. São finalidades diferentes, embora os dois caminhos tenham o mesmo corpo simples na aplicação.

O check retorna “ok” sem testar `VAGA`. Portanto, um Pod pode estar vivo e pronto e ainda recusar um cálculo. Isso ajuda a explicar as falhas sob carga.

`securityContext` exige usuário não root, desabilita elevação de privilégios e deixa o sistema de arquivos raiz somente para leitura. Isso combina com o usuário numérico da imagem e com a aplicação sem escrita persistente. Não equivale a uma revisão completa de segurança.

A [versão mínima](../projeto/k8s/versoes/deployment-inicial.yaml) permite comparar a publicação inicial com a versão que acrescenta recursos, probes e restrições. O manifesto final não configura HPA: a escala deste experimento é manual/scriptada.

### [service.yaml](../projeto/k8s/service.yaml)

`kind: Service`, nome `rotas`, tipo `ClusterIP`: oferece endereço estável interno. `selector.app: rotas` encontra os Pods da aplicação. `port: 8000` é a porta do serviço e `targetPort: 8000` é a porta de destino nos Pods.

O nome `rotas` é resolvido pelo DNS do cluster para clientes no mesmo namespace. O Service não calcula rotas, não cria réplicas e não mede a ocupação do semáforo. O Job do k6 usa outro rótulo, evitando entrar como destino do Service.

### [job-carga.yaml](../projeto/k8s/job-carga.yaml) e ConfigMap

Um Job executa uma tarefa até terminar. Aqui o contêiner é `grafana/k6:1.0.0`, com comando `k6 run /scripts/carga.js`. Não usa a imagem Python `rotas:1.0`.

- As variáveis `TAXA=6`, `PARADAS=9` e `DURACAO=60` alimentam `__ENV`.
- O volume vem do ConfigMap `carga-script` e é montado somente para leitura em `/scripts`.
- O ConfigMap é criado a partir de `carga.js` na publicação; não há um arquivo YAML independente dele versionado na pasta `k8s`.
- `restartPolicy: Never` impede reinício automático do contêiner terminado; `backoffLimit: 0` impede novas tentativas do Job após falha.
- `activeDeadlineSeconds: 240` limita o tempo de execução do Job.
- Requests do k6 são 250m de CPU e 128Mi de memória; limits são 500m e 256Mi. O gerador também precisa de recursos.

**Fala sugerida:** “Deployment mantém um serviço contínuo. Job executa um teste que tem começo e fim. ConfigMap leva o script de teste para dentro do contêiner do k6.”

## 12. Automação: o que os scripts fazem

Você não precisa recitar todos os comandos administrativos. Precisa explicar as entradas, as ações, as verificações e os arquivos produzidos. Os scripts PowerShell foram executados no Windows; os equivalentes em [scripts/linux](../projeto/scripts/linux) tiveram sintaxe verificada, sem execução completa em Linux.

### `comum.ps1`: funções compartilhadas

Os scripts carregam esse arquivo com dot-sourcing (`. caminho`), disponibilizando suas funções na sessão do script. Ele define a raiz do projeto, ajusta o PATH do processo e escolhe o Python do ambiente local de ferramentas quando disponível.

`Run` executa um programa com argumentos, exibe sua saída e verifica `$LASTEXITCODE`; código diferente de zero provoca erro. `K` acrescenta contexto e namespace `ops-lab` ao kubectl. `Check-Cluster` confere o vínculo do contexto com o cluster esperado e o estado do perfil Minikube. `Save-K` salva uma saída de kubectl em evidências e também verifica seu código de retorno.

Essas verificações reduzem a chance de atuar no cluster errado e de ignorar erros. Não substituem a leitura da saída pelo operador.

### `executar-testes.ps1`: do parâmetro ao dado coletado

1. Recebe modo `Piloto` ou `Serie`, taxa, rótulo e justificativa; valida formatos e limites.
2. Confere o cluster e abre um arquivo de trava com acesso exclusivo, evitando duas execuções simultâneas deste script.
3. Para cada medição, recusa um rótulo já existente e um Job `carga` preexistente, preservando evidências.
4. Ajusta a quantidade de réplicas e espera o rollout. Confere a quantidade de Pods e endpoints prontos antes do teste.
5. Salva Pods, endpoints e contadores anteriores. Gera uma cópia do manifesto do Job com a taxa escolhida e o aplica.
6. Acompanha o término do contêiner e coleta amostras de recursos com `kubectl top`. Erros dessa consulta são registrados; não viram valores inventados.
7. Salva logs do k6, estado do Job, estado do Pod de carga, eventos, contadores e Pods posteriores, inclusive quando o teste de desempenho falha.
8. Chama o consolidador. Só após aceitar a coleta remove o Job, permitindo o próximo teste.
9. No `finally`, libera o arquivo de trava.

O piloto usa uma réplica. A série exige piloto da mesma taxa sem descartes e uma justificativa de calibração. Guarda parâmetros e hashes de aplicação, carga e manifestos para verificar consistência em retomadas. A ordem das nove medições é A: 3/1/2, B: 2/3/1, C: 1/2/3. Isso alterna configurações e evita medir sempre em ordem crescente.

O script pode retomar linhas já preenchidas. Portanto, para outra máquina use uma pasta de demonstração separada e resultados vazios; não apresente evidências antigas como se tivessem sido medidas naquele notebook.

### `consolidar-resultados.py`: de logs para tabela e gráficos

- Lê o cabeçalho do CSV modelo e preserva suas 13 colunas, com separador `;` e UTF-8 com BOM.
- `parse_log` remove códigos de cor e usa expressões regulares para extrair contagem de rotas, percentual de falhas, p95 e descartes. Normaliza unidades de latência para milissegundos. Se faltar uma métrica necessária, rejeita a coleta.
- Confere código de saída do k6: 0 ou 99 são aceitos como execuções analisáveis. Não aceita qualquer falha como se fosse um resultado de desempenho.
- Compara identificadores e reinícios dos Pods antes/depois. Mudanças invalidam a comparação que pressupõe as mesmas réplicas durante a medição.
- Compara contadores por Pod e extrai amostras de CPU, filtrando os nomes dos Pods pertinentes ao teste.
- Preenche a linha correspondente sem sobrescrever uma medição já preenchida.
- Quando há exatamente as nove medições esperadas e taxa consistente, calcula medianas por quantidade de réplicas e produz o resumo. Havendo Matplotlib, gera os quatro gráficos.

O cálculo de throughput divide sucessos por **60**, coerente com a duração fixa da atividade. Alterar somente `DURACAO` no Job não adapta automaticamente esse analisador: seria necessário revisar o método e o código de consolidação. O leitor de amostras de recursos também espera o formato específico de unidades registrado neste laboratório.

### Inventário dos demais scripts

| Arquivo | Papel para explicar na defesa |
|---|---|
| `verificar-ambiente.ps1` | Diagnostica ferramentas, máquina e ambiente |
| `instalar-dependencias.ps1` | Auxilia a instalação de dependências; certas etapas do Windows exigem administrador |
| `iniciar-cluster.ps1` | Inicia o perfil Minikube e prepara o laboratório |
| `publicar-aplicacao.ps1` | Constrói/testa a imagem, carrega no cluster e publica os recursos |
| `validar-aplicacao.ps1` | Confere publicação, rede e resposta HTTP |
| `testar-rollback.ps1` | Aplica imagem inválida, coleta diagnóstico e reverte a atualização |
| `testar-capacidade.ps1` | Testa seis réplicas, registra o que ocorreu e restaura uma réplica |
| `comprovar-final.ps1` | Coleta o estado final e evidências de funcionamento |
| `encerrar-ambiente.ps1` | Encerra o laboratório, com opção de excluir o namespace |
| `preparar-demonstracao.ps1` | Prepara uma cópia separada para ensaio, preservando os resultados originais |
| `validar-estatico.py` | Verifica originais, manifestos e HTTP local; grava relatórios de validação |
| `auditar-entrega.py` | Cruza verificações das evidências e da entrega |
| `revisar-recursos.py` | Revisa a análise de recursos a partir dos registros |
| `preparar-entrega.py`, `gerar-documentacao.py` | Geram/preparam materiais auxiliares da entrega; não são o servidor |
| `preparar-slides.py`, `empacotar-entrega.py` | Auxiliam materiais de apresentação e empacotamento |
| `requirements-validacao.txt` | Dependências das ferramentas de validação/análise, não do servidor original |

Geradores de documentação e validadores podem gravar arquivos. Não execute toda a pasta de scripts indiscriminadamente só para estudar. Use o [laboratório guiado](02-laboratorio-guiado.md) e a cópia de demonstração descrita no [guia do outro notebook](03-outro-notebook.md).

## 13. Relacionar o código aos resultados reais

Consulte a [análise experimental](../projeto/documentacao/05-relatorio-experimentos.md). Os números abaixo são do computador original, com nove entregas, taxa de seis pedidos/s e medição de 60 s; não são previsão para outra máquina.

| Réplicas | Mediana de sucessos/s | Mediana de falhas | Mediana do p95 dos sucessos |
|---|---:|---:|---:|
| 1 | 2,23 | 62,88% | 387,96 ms |
| 2 | 3,53 | 41,27% | 382,28 ms |
| 3 | 4,07 | 32,40% | 380,58 ms |

As nove medições tiveram zero descartes. Todas ficaram abaixo de 800 ms no p95 de sucessos, mas nenhuma atingiu falhas menores que 1%. A quantidade de rotas atendidas por segundo cresceu; a meta completa continuou descumprida.

**Ligação causal com o código:** busca exaustiva custa CPU; cada processo tem uma vaga; pedidos sem vaga recebem 503; os checks não retiram o Pod do Service por causa dessa ocupação; mais réplicas acrescentam capacidade, mas não garantem que cada pedido seja encaminhado a uma vaga livre. Os resultados também dependem dos recursos compartilhados do computador.

No exercício de seis réplicas, os seis Pods ficaram Running. O scheduler considerou recursos anunciados pelo nó, que diferiam da quota aplicada ao contêiner do nó. Não afirme que um Pod ficou Pending só porque esse era um resultado esperado no material ilustrativo.

### Contas que você deve conseguir fazer

- Uma medição com 244 sucessos em 60 s tem `244 / 60 = 4,0667` rotas/s. O valor arredondado é 4,07.
- Com demanda de seis pedidos/s, planejam-se aproximadamente 360 inícios em 60 s. Use os valores efetivamente registrados para percentuais; não reconstrua uma porcentagem exata apenas desse número nominal.
- Mediana de três valores é o valor central depois de ordenar. Não é a soma dividida por três.
- Três réplicas reservam `3 × 500m = 1500m`, ou 1,5 CPU, para a aplicação. Isso não inclui k6 e componentes do cluster e não representa consumo constante de 1,5 CPU.

## 14. Roteiro para explicar com o editor aberto

Ensaie uma apresentação de 8 a 10 minutos. Aponte para o código enquanto fala e adapte as frases ao que entendeu.

1. **Problema e fluxo (1 min):** abra `app.py`, mostre `PONTOS` e descreva depósito, entregas e circuito. Desenhe cliente → Service → Pod.
2. **Algoritmo (2 min):** mostre `calcular_rota`. Explique matriz de distâncias, permutações, soma do circuito, comparação e retorno. Faça o exemplo `0 → 1 → 3 → 2 → 0`.
3. **Atendimento (2 min):** mostre `do_GET`, a faixa 3–9, os códigos 400/503/200 e o `finally`. Explique a diferença entre semáforo e trava dos contadores.
4. **Tela (1 min):** mostre `PAGINA`, o `fetch` e a montagem do SVG. Diga onde executam Python e JavaScript.
5. **Infraestrutura (1–2 min):** abra Dockerfile, Deployment e Service. Relacione comando, porta, imagem, réplicas, selector, recursos e probes.
6. **Experimento (1–2 min):** abra `carga.js`. Explique demanda, medição, sucesso, falha e thresholds. Mostre a tabela e conclua quais critérios passaram e falharam.

Para uma demonstração ao vivo, siga os comandos já verificados no [laboratório](02-laboratorio-guiado.md). Prepare o outro notebook antes da aula; não dependa de instalar Docker ou baixar imagens durante a apresentação.

## 15. Perguntas prováveis, com respostas para treinar

**1. Onde é calculada a rota?** No servidor Python, em `calcular_rota`. O navegador só solicita e desenha a resposta.

**2. Por que nove entregas usam dez pontos?** Porque o depósito ocupa o índice zero e não conta como entrega.

**3. O algoritmo encontra a menor rota?** Encontra o menor circuito para os pontos e distâncias euclidianas modelados, pois examina todas as ordens. Não encontra uma rota real em ruas.

**4. Por que não aumentar para cem entregas?** A enumeração fatorial cresce muito rápido; seria necessário rever o algoritmo e os requisitos.

**5. Por que usar uma matriz?** Para calcular cada distância antecipadamente e reaproveitá-la ao somar candidatos.

**6. Se há threads, por que retorna ocupado?** Porque a aplicação limita deliberadamente a um cálculo por processo usando `VAGA`.

**7. O semáforo é distribuído?** Não. Cada processo possui o seu; três Pods da aplicação representam três vagas independentes nesta arquitetura.

**8. O que acontece sem `finally`?** Uma exceção depois de obter a vaga poderia deixá-la presa e provocar recusas posteriores. O `finally` garante a liberação.

**9. Um 503 significa que o Pod morreu?** Não. Aqui significa que o calculador estava ocupado. O servidor pode continuar atendendo saúde e página.

**10. Readiness garante vaga livre?** Não. O endpoint só retorna status simples e não verifica o semáforo.

**11. O Service distribui exatamente um terço para cada Pod?** Não há essa garantia; novas conexões podem ser encaminhadas a endpoints prontos sem saber a vaga disponível.

**12. Qual a diferença entre tempo de cálculo e p95?** Um é o tempo instrumentado do cálculo no servidor; o outro resume a distribuição das durações HTTP dos sucessos medidos pelo cliente.

**13. O teste passou porque p95 ficou bom?** Não. Os critérios são conjuntos; falhas menores que 1% também eram necessárias e não foram atingidas.

**14. Zero descartes significa zero falhas?** Não. Significa que o gerador não descartou iterações da medição; a aplicação ainda respondeu 503 a muitos pedidos.

**15. Por que o Job Failed não foi apagado imediatamente como erro inválido?** Porque thresholds reprovados podem produzir saída 99 e dados válidos para análise. Primeiro coletamos e verificamos logs e estado.

**16. Quem recria um Pod apagado?** Os controladores Kubernetes mantêm o número desejado através do Deployment/ReplicaSet; não é uma função do código Python.

**17. Por que rollback manteve atendimento?** A atualização gradual preservou a instância disponível enquanto a nova imagem inválida não ficou pronta. A reversão restaurou a especificação anterior; ela não corrige o código de uma imagem defeituosa.

**18. O que é 500m?** Meio núcleo de CPU em unidades de Kubernetes, e não 500 MB de memória.

**19. O outro notebook terá os mesmos números?** Não necessariamente. Hardware, virtualização, recursos e carga concorrente afetam o resultado. Uma nova medição precisa de método e evidências próprios.

**20. O que você alterou nesta atualização de estudo?** Acrescentei documentação explicativa e ligações no roteiro. O código funcional, os manifestos e as evidências históricas foram mantidos.

## 16. Exercícios de compreensão com gabarito

Antes de ler a resposta, tente falar e apontar o trecho correspondente.

| Exercício | Resposta esperada |
|---|---|
| Trace um GET de três entregas do início ao fim | `do_GET` → caminho → parâmetro válido → obtém vaga → `calcular_rota(3)` → seis permutações → resultado acrescido de tempo/Pod → resposta 200 → log → liberação |
| Um segundo pedido chega durante o cálculo; onde para? | Na tentativa de obter `VAGA`; registra recusa e recebe 503 |
| Trocar a opção da tela muda `PONTOS`? | Não; altera quantos pontos iniciais entram no circuito |
| Uma resposta 503 de 2 ms reduz `latencia_ok`? | Não; só sucessos são adicionados ao Trend |
| Onde muda o número de réplicas? | No estado do Deployment, pelo manifesto ou comando de escala; não em `app.py` |
| Onde o código do k6 chega ao Job? | No volume do ConfigMap montado em `/scripts` |
| Como provar que um pedido voltou ao depósito? | Mostrar que `ordem` começa e termina em 0 e explicar a soma dos dois trechos externos |
| Por que as evidências não devem ser sobrescritas no ensaio? | Sustentam os resultados entregues; o ensaio deve usar uma pasta e coleta separadas |

### Seu plano para estudar este arquivo

1. **Primeiro dia:** seções 1–8, com `app.py` aberto. Explique cada função sem ler o parágrafo inteiro.
2. **Segundo dia:** seções 9–13, com `carga.js`, Dockerfile e YAML abertos. Relacione cada métrica ao trecho que a registra.
3. **Terceiro dia:** apresente a seção 14 em voz alta e responda 15–16 sem consultar. Volte aos pontos em que travou.

Você está pronto para defender o código quando consegue partir de uma URL, percorrer as funções na ordem correta, justificar uma resposta 200 ou 503 e relacionar isso ao comportamento medido. Para retomar o restante da preparação, use o [plano geral](00-plano-de-estudo.md).

## 17. Verificação desta atualização

Em 23/10/2026, a atualização de documentação foi conferida contra os arquivos do repositório. Os seis arquivos de referência mantiveram seus hashes SHA-256 originais. O validador existente passou em 22 verificações numa cópia temporária, incluindo consistência dos manifestos, respostas HTTP locais, integridade das rotas de três e nove entregas, erros de entrada e atendimento concorrente com respostas 200 e 503. Os links locais dos três documentos atualizados também foram verificados.

Essa verificação executou Python localmente; não repetiu os experimentos Docker/Kubernetes/k6 nem alterou as evidências históricas. A atualização modifica apenas documentação.
