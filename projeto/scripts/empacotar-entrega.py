"""Cria pacote sem ambientes virtuais nem arquivos privados de construção."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(R.rglob('*')):
    if not p.is_file():continue
    relative=p.relative_to(R)
    if any(x in {'.ferramentas','.build-apresentacao','__pycache__'} for x in relative.parts):continue
    if any(x.startswith('.chart-data-') for x in relative.parts):continue
    if p.suffix=='.lock':continue
    if relative.as_posix() in ['resultados/evidencias/inventario-final.json','ENTREGAVEIS.md']:continue
    files.append(p)
inventory=[{'arquivo':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(R/'resultados/evidencias/inventario-final.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'ENTREGAVEIS.md').write_text('# Inventário dos entregáveis\n\nArquivos originais permanecem na raiz e em originais/. Os arquivos adicionais estão listados abaixo. Ambientes virtuais e arquivos privados de construção não entram no pacote.\n\n'+''.join(f'- {r["arquivo"]} ({r["bytes"]} bytes)\n' for r in inventory),encoding='utf-8')
archive=R.parent/'RotaExpress-entrega.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in ['Aula_Kubernetes.pdf','Guia_Atividade.pdf']:z.write(R.parent/name,'RotaExpress/'+name)
    for p in files+[R/'resultados/evidencias/inventario-final.json',R/'ENTREGAVEIS.md']:z.write(p,'RotaExpress/projeto/'+p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
    bad=z.testzip()
    if bad:raise RuntimeError('Arquivo corrompido: '+bad)
    count=len(z.namelist())
print(json.dumps({'arquivo':str(archive),'entradas':count,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'integridade_zip':'validada'},ensure_ascii=False,indent=2))
