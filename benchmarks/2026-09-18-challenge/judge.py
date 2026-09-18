from pathlib import Path
import json,re,sys,hashlib
from run import ROOT,Server,prepare,start,turn
names=['Sherlock Report','シャーロック・リポート','AcePilot','エースパイロット','Beautiful Dreamer','ビューティフル・ドリーマー','ドリ子','Edgar Rumple','エドガー・ランプル','Expert Moriarty','エキスパート・モリアーティ','Flight Attendant','フライトアテンダント','Ghost Blogger','ゴーストブロガー','Inspire Lestrade','インスパイア・レストレード','Mycroft Debater','マイクロフト・ディベーター','Rorschach Security','ロールシャッハ・セキュリティ','Work Force','ワークフォース','Mrs. Legal Advisor','みんなの法律アドバイザー','Codex']
def anonymize(text):
 for n in names:text=re.sub(re.escape(n),'[回答者]',text,flags=re.I)
 return text
batch=int(sys.argv[1]);out=ROOT/'judges'/f'batch-{batch}.json'
assert not out.exists(),'No repeated judging'
tasks=json.loads((ROOT/'tasks.json').read_text(encoding='utf-8'));maps=json.loads((ROOT/'judge-map.json').read_text(encoding='utf-8'))
selected=list(maps.items())[batch*3:batch*3+3];payload=[]
for ident,m in selected:
 task=next(t for t in tasks if t['id']==m['task'])
 item={'task':ident,'user_turns':task['turns'],'criteria':task['criteria'],'critical_checks':task['critical_checks']}
 for label in ['A','B']:
  record=json.loads((ROOT/'results'/(m['task']+'--'+m[label]+'.json')).read_text(encoding='utf-8'));assert len(record['turns'])==2
  item[label]=[anonymize(v['response']) for v in record['turns']]
 payload.append(item)
input_text=json.dumps(payload,ensure_ascii=False,indent=2)
(ROOT/'judges'/f'input-{batch}.txt').write_text(input_text,encoding='utf-8')
server=Server()
try:
 tid=start(server,prepare('baseline'),(ROOT/'judge-prompt.txt').read_text(encoding='utf-8'))
 result=turn(server,tid,input_text)
 text=result['response'];text=re.sub(r'^```(?:json)?\s*|\s*```$','',text.strip())
 parsed=json.loads(text);assert len(parsed['reviews'])==3
 for x in parsed['reviews']:
  assert x['task'] in dict(selected)
  for k in ['A','B']:
   assert len(x[k]['scores'])==len(x[k]['evidence'])==4
   assert all(type(s)==int and 0<=s<=4 for s in x[k]['scores'])
 result.update(parsed=parsed,batch=batch,input_sha256=hashlib.sha256(input_text.encode()).hexdigest())
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('JUDGED',batch,result['last_usage'],flush=True)
finally:server.close()
