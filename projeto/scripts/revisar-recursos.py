"""Filtra leituras em cache de Pods já removidos. Preserva métricas k6 e logs."""
import csv,json,runpy,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1]
parse=runpy.run_path(str(R/'scripts/consolidar-resultados.py'))['resource_samples']
path=R/'resultados/comparativo.csv'
rows=list(csv.DictReader(path.open(encoding='utf-8-sig'),delimiter=';'))
for row in rows:
    if not row['rotas_ok']:continue
    d=R/'resultados/evidencias'/row['rotulo']
    before=json.loads((d/'pods-antes.json').read_text(encoding='utf-8-sig'))
    names={p['metadata']['name'] for p in before['items'] if not p['metadata'].get('deletionTimestamp')}
    samples=parse((d/'recursos.txt').read_text(encoding='utf-8-sig'))
    row['cpu_observada_por_pod']=' | '.join(f'{p}:CPU mediana {statistics.median(v[0] for v in values):g}m, max amostrado {max(v[0] for v in values)}m, memoria max amostrada {max(v[1] for v in values)}Mi' for p,values in samples.items() if p in names)
with path.open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
print('Coluna de recursos revisada contra os nomes reais dos Pods. Métricas k6 preservadas.')
