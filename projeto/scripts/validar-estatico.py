"""Validação estática e HTTP local. Não substitui Docker/Kubernetes/k6."""
import concurrent.futures
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
import yaml

root=Path(__file__).resolve().parents[1]
report={'escopo':'Estático e Python no Windows. Sem medição Kubernetes.','python':sys.version,'checks':[]}
def record(name,ok,details):
    report['checks'].append({'nome':name,'passou':bool(ok),'detalhes':details})
    if not ok:raise AssertionError(name)

for name in ['app.py','carga.js','Dockerfile','.dockerignore','README.md','resultados_modelo.csv']:
    a=hashlib.sha256((root/name).read_bytes()).hexdigest()
    b=hashlib.sha256((root/'originais'/name).read_bytes()).hexdigest()
    record('Original preservado: '+name,a==b,a)
manifests={p.name:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (root/'k8s').glob('*.yaml')}
d=manifests['deployment.yaml'];s=manifests['service.yaml'];j=manifests['job-carga.yaml']
record('Namespace consistente',all(x['metadata'].get('namespace','ops-lab')=='ops-lab' for x in manifests.values()),list(manifests))
record('Labels e selectors',d['spec']['selector']['matchLabels']==s['spec']['selector']==d['spec']['template']['metadata']['labels'],s['spec']['selector'])
c=d['spec']['template']['spec']['containers'][0]
record('Recursos do guia',c['resources']=={'requests':{'cpu':'500m','memory':'64Mi'},'limits':{'cpu':'500m','memory':'128Mi'}},c['resources'])
record('Portas consistentes',c['ports'][0]['containerPort']==s['spec']['ports'][0]['port']==s['spec']['ports'][0]['targetPort']==8000,8000)
record('k6 conforme guia',j['spec']['backoffLimit']==0 and j['spec']['template']['spec']['containers'][0]['image']=='grafana/k6:1.0.0' and j['spec']['template']['metadata']['labels']!=s['spec']['selector'],j['spec'])
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
env=dict(os.environ,PORT=str(port),PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1')
log=(root/'resultados/logs/python-local.txt').open('w',encoding='utf-8')
process=subprocess.Popen([sys.executable,str(root/'app.py')],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
def get(path):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=15) as r:return r.status,r.read().decode('utf-8'),dict(r.headers)
    except urllib.error.HTTPError as e:return e.code,e.read().decode('utf-8'),dict(e.headers)
try:
    for _ in range(100):
        try:get('/healthz');break
        except OSError:time.sleep(.1)
    for path in ['/','/healthz','/readyz','/api/rota?paradas=9','/api/rota?paradas=3','/api/rota?paradas=2','/api/rota?paradas=abc','/nao-existe']:
        status,body,headers=get(path)
        expected=400 if path.endswith(('=2','=abc')) else 404 if path=='/nao-existe' else 200
        details={'HTTP':status,'X-Pod':headers.get('X-Pod')}
        if path.startswith('/api/rota') and status==200:
            data=json.loads(body);n=data['paradas']
            record('Integridade rota '+str(n),data['ordem'][0]==data['ordem'][-1]==0 and sorted(data['ordem'][1:-1])==list(range(1,n+1)) and data['distancia']>0,data)
            details['resposta']=data
        else:details['resposta']=body if path!='/' else 'HTML RotaExpress presente'
        record('HTTP '+path,status==expected,details)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        responses=list(pool.map(lambda _:get('/api/rota?paradas=9')[0],range(8)))
    record('Concorrencia com recusas 503',200 in responses and 503 in responses,responses)
finally:
    process.terminate();process.wait(timeout=10);log.close()
    (root/'resultados/evidencias/validacao-estatica-http.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
