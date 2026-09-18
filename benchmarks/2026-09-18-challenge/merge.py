from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
maps=json.loads((ROOT/'judge-map.json').read_text(encoding='utf-8'));scores={}
for p in sorted((ROOT/'judges').glob('batch-*.json')):
 for review in json.loads(p.read_text(encoding='utf-8'))['parsed']['reviews']:
  m=maps[review['task']];item={'blind_id':review['task'],'reason':review['reason'],'winner':'tie' if review['winner']=='tie' else m[review['winner']]}
  for label in ['A','B']:item[m[label]]=review[label]
  item['delta']=sum(item['plugin']['scores'])-sum(item['baseline']['scores']);scores[m['task']]=item
(ROOT/'scores.json').write_text(json.dumps(scores,ensure_ascii=False,indent=2),encoding='utf-8');print('Merged',len(scores),'pairs')
for k,v in scores.items():print(k,sum(v['baseline']['scores']),sum(v['plugin']['scores']),v['winner'],v['reason'])
