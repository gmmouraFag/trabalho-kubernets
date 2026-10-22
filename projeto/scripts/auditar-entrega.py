"""Reconcilia a tabela com os logs e os objetos reais de cada execução."""
from pathlib import Path
import csv,json,hashlib,statistics,sys,runpy

R=Path(__file__).resolve().parents[1]
helpers=runpy.run_path(str(R/'scripts/consolidar-resultados.py'))
parse_log=helpers['parse_log']
resources=helpers['resource_samples']
checks=[]
def check(label,ok,details):checks.append({'verificacao':label,'passou':bool(ok),'detalhes':details})
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
table=list(csv.DictReader((R/'resultados/comparativo.csv').open(encoding='utf-8-sig'),delimiter=';'))
sequence=['3pods-a','1pod-a','2pods-a','2pods-b','3pods-b','1pod-b','1pod-c','2pods-c','3pods-c']
series=[r for r in table if r['rotulo'] in sequence]
check('Nove medições completas',len(series)==9 and all(r['rotas_ok'] for r in series),[r['rotulo'] for r in series if r['rotas_ok']])
check('Mesma TAXA',len({r['taxa'] for r in series})==1,[r['taxa'] for r in series])
image_ids=set()
time_order=[]
summary_resources=[]
for row in series:
    label=row['rotulo'];prefix=f'resultados/evidencias/{label}'
    try:
        parsed=parse_log((R/'resultados/logs'/f'{label}.txt').read_text(encoding='utf-8-sig'))
        check(label+': tabela versus log',all(abs(float(row[k])-v)<1e-9 for k,v in parsed.items()),parsed)
        before=read(prefix+'/pods-antes.json');after=read(prefix+'/pods-depois.json')
        for pod in before['items']:
            if pod['metadata'].get('deletionTimestamp'):continue
            for c in pod['status']['containerStatuses']:image_ids.add(c['imageID'])
            rc=pod['spec']['containers'][0]['resources']
            check(label+': recursos '+pod['metadata']['name'],rc=={'requests':{'cpu':'500m','memory':'64Mi'},'limits':{'cpu':'500m','memory':'128Mi'}},rc)
        identity=lambda data:{p['metadata']['uid']:sum(c['restartCount'] for c in p['status']['containerStatuses']) for p in data['items'] if not p['metadata'].get('deletionTimestamp')}
        check(label+': identidade e reinícios estáveis',identity(before)==identity(after),identity(after))
        endpoints=read(prefix+'/endpointslices.json')
        ready=[e for sl in endpoints['items'] for e in sl['endpoints'] if e['conditions'].get('ready') and not e['conditions'].get('terminating')]
        check(label+': endpoints prontos',len(ready)==int(row['replicas']),len(ready))
        job=read(prefix+'/job-pods.json')['items'][0]
        exit_code=job['status']['containerStatuses'][0]['state']['terminated']['exitCode']
        check(label+': execução completa do k6',exit_code in [0,99],exit_code)
        env={x['name']:x['value'] for x in job['spec']['containers'][0]['env']}
        check(label+': condições fixas',env=={'TAXA':'6','PARADAS':'9','DURACAO':'60'},env)
        time_order.append((job['metadata']['creationTimestamp'],label))
        samples=resources((R/prefix/'recursos.txt').read_text(encoding='utf-8-sig'))
        live_names={p['metadata']['name'] for p in before['items'] if not p['metadata'].get('deletionTimestamp')}
        samples={p:v for p,v in samples.items() if p in live_names or p==job['metadata']['name']}
        check(label+': recursos amostrados',any(p.startswith('rotas-') for p in samples),list(samples))
        for pod,vals in samples.items():
            summary_resources.append({'rotulo':label,'replicas':row['replicas'],'pod':pod,'tipo':'aplicacao' if pod.startswith('rotas-') else 'k6','amostras':len(vals),'cpu_mediana_m':statistics.median(v[0] for v in vals),'cpu_max_amostrado_m':max(v[0] for v in vals),'memoria_mediana_Mi':statistics.median(v[1] for v in vals),'memoria_max_amostrada_Mi':max(v[1] for v in vals)})
    except Exception as e:check(label+': integridade',False,str(e))
check('Imagem idêntica nas nove execuções',len(image_ids)==1,sorted(image_ids))
check('Ordem A/B/C',len(time_order)==9 and [n for _,n in sorted(time_order)]==sequence,[n for _,n in sorted(time_order)])
for name in ['app.py','carga.js','Dockerfile','.dockerignore','README.md','resultados_modelo.csv']:
    check('Original '+name,(R/name).read_bytes()==(R/'originais'/name).read_bytes(),hashlib.sha256((R/name).read_bytes()).hexdigest())
before_recovery=read('resultados/evidencias/pod-antes-recriacao.json')
after_recovery=read('resultados/evidencias/pod-depois-recriacao.json')
uids=lambda data:{p['metadata']['uid'] for p in data['items']}
check('Pod excluído foi substituído',bool(uids(after_recovery)) and uids(before_recovery).isdisjoint(uids(after_recovery)),{'antes':list(uids(before_recovery)),'depois':list(uids(after_recovery))})
rollback=read('resultados/evidencias/rollback-recuperado.json')
check('Rollback restaurou imagem',rollback['spec']['template']['spec']['containers'][0]['image']=='rotas:1.0',rollback['spec']['template']['spec']['containers'][0]['image'])
check('Tabela mantém as colunas originais',list(table[0])==(R/'originais/resultados_modelo.csv').read_text(encoding='utf-8-sig').splitlines()[0].split(';'),list(table[0]))
if summary_resources:
    with (R/'resultados/recursos-resumo.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary_resources[0]),delimiter=';');w.writeheader();w.writerows(summary_resources)
out={'validado':all(x['passou'] for x in checks),'escopo':'Reconciliação de logs, condições e evidências. Metas de desempenho são avaliadas separadamente.','verificacoes':checks}
(R/'resultados/evidencias/auditoria-final.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'validado':out['validado'],'verificacoes':len(checks),'falhas':[x for x in checks if not x['passou']]},ensure_ascii=False,indent=2))
sys.exit(0 if out['validado'] else 1)
