from pathlib import Path
import json,re,ast,copy,difflib
ROOT=Path(__file__).resolve().parent
records=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'results').glob('*.json')]
checks={}
for row in records:
 if len(row['turns'])!=2:continue
 ident=row['task']+'--'+row['condition'];first,last=[t['response'] for t in row['turns']]
 item={'characters':[len(re.sub(r'\s','',t['response'])) for t in row['turns']],'revision_similarity':round(difflib.SequenceMatcher(None,first,last).ratio(),3)}
 banned={'beautiful-dreamer':['傷も思い出','もう一度','物語','未来','あなたらしさ'],'ghost-blogger':['忙しい日常','小さな幸せ','時間が止まる','人生','気づかせてくれた']}.get(row['task'],[])
 if banned:item['final_banned_strings']={s:last.count(s) for s in banned}
 if row['task']=='acepilot':
  snippets=re.findall(r'```(?:python)?\s*\n(.*?)```',last,re.S);assert snippets,'Missing code'
  source='\n'.join(snippets);tree=ast.parse(source)
  assert not any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(tree)), 'Review imports before execution'
  forbidden={'open','exec','eval','compile','__import__','input'}
  assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in forbidden for n in ast.walk(tree))
  scope={};exec(compile(tree,'inspected-event-reducer','exec'),scope);f=scope['apply_events']
  class OnePass:
   def __init__(self,data):self.data=data;self.used=False
   def __iter__(self):
    if self.used:raise RuntimeError('input iterated twice')
    self.used=True;return iter(self.data)
  results=[]
  for i,test in enumerate(json.loads((ROOT/'code-tests.json').read_text())):
   data=copy.deepcopy(test['events']);before=copy.deepcopy(data)
   try:
    got=f(OnePass(data));ok=got==test['expected'] and data==before
    results.append({'case':i+1,'passed':ok,'actual':got,'input_unchanged':data==before})
   except Exception as e:results.append({'case':i+1,'passed':False,'error':str(e)})
  item.update(code_tests=results,passed=sum(v['passed'] for v in results),function_count=sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) for n in ast.walk(tree)),class_count=sum(isinstance(n,ast.ClassDef) for n in ast.walk(tree)),imports=0,code_nonblank_lines=sum(bool(l.strip()) for l in source.splitlines()),explanation_chars=len(re.sub(r'\s','',re.sub(r'```.*?```','',last,flags=re.S))))
 checks[ident]=item
(ROOT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print('Checked',len(checks),'conversations; code:',[(k,v['passed']) for k,v in checks.items() if 'passed' in v])
