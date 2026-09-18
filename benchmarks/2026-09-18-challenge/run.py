from pathlib import Path
import json,hashlib,shutil,sys,time
from datetime import datetime,timezone
from transport import Server
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent/'codex-plugins'
if not REPO.exists():REPO=ROOT.parent.parent
MODEL='gpt-6-astra'
CONTROL="""Use only the supplied information. External tools, web and file operations are unavailable. Questions to the user are allowed. Apply the selected skill's full persona and judgment instructions; with no selected skill answer as ordinary Codex. Required reference texts are supplied. Respond directly to the task, without announcing skill activation or a benchmark. Previously supplied AGENTS.md instructions no longer apply. Do not claim to have executed tools. Follow the user's output constraints."""
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(id):
 cwd=ROOT/'work'/id;cwd.mkdir(parents=True,exist_ok=True)
 case={'id':id,'cwd':str(cwd),'references':[]}
 if id=='baseline':return case
 src=REPO/'plugins'/id/'skills'/id
 dest=cwd/'.agents/skills'/id
 if not dest.exists():shutil.copytree(src,dest)
 assert (dest/'SKILL.md').read_bytes()==(src/'SKILL.md').read_bytes()
 case.update(skill_path=str(dest/'SKILL.md'),skill_sha256=sha(src/'SKILL.md'))
 refs=['goodcode.txt'] if id=='acepilot' else ['analysis_methods.txt','thinking_methods.txt'] if id=='inspire-lestrade' else ['ビジネスマナー.txt'] if id=='work-force' else []
 for name in refs:
  p=dest/'references'/name;case['references'].append({'name':name,'path':str(p),'sha256':sha(p)})
 if id=='work-force':
  p=ROOT/'inputs/honorifics.txt';case['references'].append({'name':'敬称リスト.pdf全文抽出','path':str(p),'sha256':sha(p)})
 return case
def start(server,case,control=CONTROL):
 found=server.call('skills/list',{'cwds':[case['cwd']],'forceReload':True})
 if case['id']!='baseline':
  skills=[s for g in found['data'] for s in g['skills'] if s['name']==case['id'] and s['enabled']]
  assert len(skills)==1 and Path(skills[0]['path'])==Path(case['skill_path'])
 info=server.call('thread/start',{'model':MODEL,'allowProviderModelFallback':False,'cwd':case['cwd'],'ephemeral':True,'approvalPolicy':'never','sandbox':'read-only','developerInstructions':control,'selectedCapabilityRoots':[],'config':{'model_reasoning_effort':'low','model_verbosity':'low'}})
 assert info.get('model')==MODEL,info.get('model')
 return info['thread']['id']
def turn(server,tid,text,case=None):
 inp=[]
 if case and case['id']!='baseline':
  inp.append({'type':'skill','name':case['id'],'path':case['skill_path']})
  for ref in case['references']:inp.append({'type':'text','text':'同梱資料 '+ref['name']+'\n'+Path(ref['path']).read_text(encoding='utf-8-sig')})
  text='$'+case['id']+'\n'+text
 inp.append({'type':'text','text':text})
 server.request_id+=1;rid=server.request_id;begin=time.monotonic()
 server.send({'id':rid,'method':'turn/start','params':{'threadId':tid,'model':MODEL,'effort':'low','summary':'none','input':inp}})
 response='';usage=None;last=None;calls=[]
 while time.monotonic()-begin<240:
  msg=server.receive(240-(time.monotonic()-begin))
  if msg.get('id')==rid and 'error' in msg:raise RuntimeError(msg['error'])
  p=msg.get('params',{})
  if p.get('threadId')!=tid:continue
  m=msg.get('method')
  if m=='thread/tokenUsage/updated':usage=p['tokenUsage']['total'];last=p['tokenUsage'].get('last')
  if m=='item/completed':
   x=p['item']
   if x['type']=='agentMessage' and x.get('phase')!='commentary':response+=x.get('text','')+'\n'
   if x['type'] in ['commandExecution','mcpToolCall','webSearch','fileChange','dynamicToolCall']:calls.append(x['type'])
  if m=='turn/completed':
   assert p['turn']['status']=='completed',p['turn']
   assert usage is not None and not calls
   return {'response':response.strip(),'cumulative_usage':usage,'last_usage':last,'seconds':round(time.monotonic()-begin,3),'timestamp_utc':datetime.now(timezone.utc).isoformat()}
 raise TimeoutError('turn timed out')
def main():
 tasks=json.loads((ROOT/'tasks.json').read_text(encoding='utf-8'));limit=int(sys.argv[1]) if len(sys.argv)>1 else 24
 (ROOT/'results').mkdir(exist_ok=True);server=Server();count=0
 try:
  for i,t in enumerate(tasks):
   order=['baseline','plugin'] if i%2==0 else ['plugin','baseline']
   for condition in order:
    dest=ROOT/'results'/(t['id']+'--'+condition+'.json')
    if dest.exists():
     prior=json.loads(dest.read_text(encoding='utf-8'))
     if len(prior['turns'])==2:continue
     raise RuntimeError('Partial conversation exists; no silent restart')
    case=prepare(t['id'] if condition=='plugin' else 'baseline');tid=start(server,case)
    result={'task':t['id'],'condition':condition,'model':MODEL,'effort':'low','skill_sha256':case.get('skill_sha256'),'reference_hashes':[{k:v for k,v in ref.items() if k!='path'} for ref in case['references']],'turns':[]}
    for j,prompt in enumerate(t['turns']):
     print('START',t['id'],condition,'turn',j+1,flush=True)
     row=turn(server,tid,prompt,case if j==0 else None);row['prompt_sha256']=hashlib.sha256(prompt.encode()).hexdigest();result['turns'].append(row)
     dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
     print('DONE',t['id'],condition,'turn',j+1,'usage',row['last_usage'],flush=True)
    count+=1
    if count>=limit:return
 finally:server.close()
if __name__=='__main__':main()
