"""Importa apenas resumos completos do k6. Lacunas nunca viram zero."""
import argparse
import csv
import json
import re
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELDS=(ROOT/'originais/resultados_modelo.csv').read_text(encoding='utf-8-sig').splitlines()[0].split(';')

def number(s):
    return float(str(s).replace(',','.'))

def parse_log(text):
    text=re.sub(r'\x1b\[[0-9;]*m','',text)
    ok=re.search(r'^\s*rotas_ok\.+:\s*(\d+)',text,re.M)
    failures=re.search(r'^\s*falhas\.+:\s*([\d.,]+)%',text,re.M)
    p95=re.search(r'^\s*latencia_ok\.+:.*?p\(95\)=([\d.,]+)(µs|us|ms|s)',text,re.M)
    dropped=re.search(r'dropped_iterations\{scenario:medicao\}[\s\S]{0,160}?count=(\d+)',text)
    if not all([ok,failures,p95,dropped]):
        raise ValueError('Resumo incompleto ou formato desconhecido. Revise log original; nao preencher com zero.')
    scale={'µs':.001,'us':.001,'ms':1,'s':1000}[p95[2]]
    return {'rotas_ok':int(ok[1]),'sucessos_por_s':int(ok[1])/60,'falhas_pct':number(failures[1]),'p95_latencia_ok_ms':number(p95[1])*scale,'dropped_iterations_medicao':int(dropped[1])}

def counts(text):
    result={}
    for line in text.splitlines():
        pod=re.search(r'\[pod/([^/]+)',line)
        values=re.search(r'total_aceitos=(\d+) total_recusados=(\d+)',line)
        if pod:result[pod[1]]=int(values[1]) if values else 0
    return result

def resource_samples(text):
    result={}
    for line in text.splitlines():
        m=re.match(r'^(rotas-\S+|carga-\S+)\s+(\d+)m\s+(\d+)Mi\s*$',line)
        if m:result.setdefault(m[1],[]).append((int(m[2]),int(m[3])))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--importar');p.add_argument('--rodada');p.add_argument('--replicas',type=int);p.add_argument('--taxa',type=int)
    a=p.parse_args()
    table=ROOT/'resultados/comparativo.csv'
    rows=list(csv.DictReader(table.open(encoding='utf-8-sig'),delimiter=';'))
    if a.importar:
        directory=ROOT/'resultados/evidencias'/a.importar
        metrics=parse_log((ROOT/'resultados/logs'/f'{a.importar}.txt').read_text(encoding='utf-8-sig'))
        pods=json.loads((directory/'job-pods.json').read_text(encoding='utf-8-sig'))
        exit_code=pods['items'][0]['status']['containerStatuses'][0]['state']['terminated']['exitCode']
        if exit_code not in (0,99):raise ValueError(f'Falha de execucao, exit code {exit_code}.')
        before=json.loads((directory/'pods-antes.json').read_text(encoding='utf-8-sig'))
        after=json.loads((directory/'pods-depois.json').read_text(encoding='utf-8-sig'))
        identity=lambda data:{x['metadata']['uid']:sum(c.get('restartCount',0) for c in x['status'].get('containerStatuses',[])) for x in data['items'] if not x['metadata'].get('deletionTimestamp')}
        if identity(before)!=identity(after):raise ValueError('Pods mudaram ou reiniciaram durante o teste. Repetir com outro rotulo.')
        b=counts((directory/'contadores-antes.txt').read_text(encoding='utf-8-sig'))
        e=counts((directory/'contadores-depois.txt').read_text(encoding='utf-8-sig'))
        dist=', '.join(f'{k}:{v-b.get(k,0)}' for k,v in e.items())
        samples=resource_samples((directory/'recursos.txt').read_text(encoding='utf-8-sig'))
        live_names={p['metadata']['name'] for p in before['items'] if not p['metadata'].get('deletionTimestamp')}
        resource_text=' | '.join(f'{pod}:CPU mediana {statistics.median(v[0] for v in vals):g}m, max amostrado {max(v[0] for v in vals)}m, memoria max amostrada {max(v[1] for v in vals)}Mi' for pod,vals in samples.items() if pod in live_names)
        row={k:'' for k in FIELDS}
        row.update(rotulo=a.importar,rodada=a.rodada,replicas=a.replicas,taxa=a.taxa,**metrics,status_job='Complete' if exit_code==0 else 'Failed (thresholds, exit 99)',cpu_observada_por_pod=resource_text or f'Sem amostras validas: evidencias/{a.importar}/recursos.txt',distribuicao_aceitos_por_pod=dist,observacoes='Contadores incluem aquecimento. CPU/memoria: amostras do ciclo, nao pico continuo.')
        index=next((i for i,r in enumerate(rows) if r['rotulo']==a.importar),None)
        if index is None:rows.append(row)
        else:
            if rows[index]['rotas_ok']:raise ValueError('Resultado existente nao sera sobrescrito.')
            rows[index]=row
        with table.open('w',encoding='utf-8-sig',newline='') as out:
            w=csv.DictWriter(out,fieldnames=FIELDS,delimiter=';');w.writeheader();w.writerows(rows)
    complete=[r for r in rows if r['rodada'] in ('A','B','C') and r['rotas_ok']!='']
    expected={'3pods-a','1pod-a','2pods-a','2pods-b','3pods-b','1pod-b','1pod-c','2pods-c','3pods-c'}
    if {r['rotulo'] for r in complete} != expected:
        print(f'Serie incompleta: {len(complete)}/9. Medianas e graficos nao foram gerados.');return
    if len({str(r['taxa']) for r in complete})!=1:raise ValueError('Taxas diferentes na serie.')
    names=['sucessos_por_s','falhas_pct','p95_latencia_ok_ms','dropped_iterations_medicao']
    medians=[]
    for n in (1,2,3):
        group=[r for r in complete if int(r['replicas'])==n]
        if len(group)!=3:raise ValueError('Repeticoes invalidas')
        medians.append(dict(replicas=n,cpu_reservada=n*.5,**{k:statistics.median(number(r[k]) for r in group) for k in names}))
    with (ROOT/'resultados/medianas.csv').open('w',encoding='utf-8-sig',newline='') as out:
        w=csv.DictWriter(out,fieldnames=list(medians[0]),delimiter=';');w.writeheader();w.writerows(medians)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        for key,unit,title in [('sucessos_por_s','rotas/s','Throughput'),('falhas_pct','%','Falhas'),('p95_latencia_ok_ms','ms','Latência p95 dos sucessos'),('dropped_iterations_medicao','iterações','Iterações descartadas na medição')]:
            vals=[r[key] for r in medians]
            fig,ax=plt.subplots(figsize=(7,4))
            bars=ax.bar([str(r['replicas']) for r in medians],vals,color='#326ce5')
            ax.bar_label(bars,labels=[f'{v:.2f}' if key!='dropped_iterations_medicao' else str(int(v)) for v in vals],padding=4)
            ax.set(xlabel='Pods',ylabel=unit,title=f'{title}: mediana de três repetições',ylim=(0,max(vals)*1.18 if max(vals)>0 else 1))
            if max(vals)==0:ax.set_yticks([0,1])
            fig.tight_layout();fig.savefig(ROOT/'resultados/graficos'/f'{key}.png',dpi=180);plt.close(fig)
    except ImportError:print('Medianas salvas. Matplotlib ausente; graficos pendentes.')
    print(json.dumps(medians,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
