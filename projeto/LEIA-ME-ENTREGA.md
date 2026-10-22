# RotaExpress: entrega e retomada

Os arquivos originais do professor permanecem intactos. Os PDFs ficam na pasta acima. O README original foi preservado; este documento é o índice da implementação adicional.

- Comece por documentacao/00-diagnostico-ambiente.md e 02-instalacao.md.
- Passo a passo: documentacao/03-implementacao.md.
- Método, resultados e decisão: documentacao/05-relatorio-experimentos.md.
- Evidências originais: resultados/logs/ e resultados/evidencias/.
- Tabela preenchida: resultados/comparativo.csv, com as colunas do modelo original.
- Apresentação: apresentacao/RotaExpress.pptx. Falas: apresentacao/roteiro-slides.md.
- Situação verificável de cada requisito: CHECKLIST_ENTREGA.md.

Série comparativa: 9/9 medições completas. O script consolidar-resultados.py gera medianas e gráficos somente depois das nove. Não confunda diagnóstico HTTP local com teste de carga Kubernetes.

Para reproduzir, use os scripts PowerShell na sequência indicada no documento 02. Scripts que coletam medições não sobrescrevem evidências existentes: para repetir uma série, use uma cópia limpa da pasta de resultados, preservando os dados anteriores. Não execute preparar-entrega.py durante uma série, porque ele restaura os manifestos-base.

Os CSVs usam ponto e vírgula como separador, UTF-8 e ponto decimal. No Excel, use Dados > De Texto/CSV e selecione a localidade adequada ao ponto decimal ao converter as colunas numéricas.
