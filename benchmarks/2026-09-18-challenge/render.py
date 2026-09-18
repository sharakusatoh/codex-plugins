from pathlib import Path
import json,sys,re,html
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent/'codex-plugins'
if not REPO.exists():REPO=ROOT.parent.parent
p=ROOT.parent/'chart-deps'
if p.exists():sys.path.insert(0,str(p))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
fp=FontProperties(fname=str(REPO/'plugins/work-force/skills/work-force/assets/fonts/NotoSansJP-Medium.ttf'))
plt.rcParams['svg.fonttype']='path'
tasks=json.loads((ROOT/'tasks.json').read_text(encoding='utf-8'));scores=json.loads((ROOT/'scores.json').read_text(encoding='utf-8'));checks=json.loads((ROOT/'checks.json').read_text(encoding='utf-8'))
records=json.loads((REPO/'benchmarks/2026-09-18-challenge/results.json').read_text(encoding='utf-8'))
names=['Sherlock Report','AcePilot','Beautiful Dreamer','Edgar Rumple','Expert Moriarty','Flight Attendant','Ghost Blogger','Inspire Lestrade','Mycroft Debater','Rorschach Security','Work Force','Mrs. Legal Advisor']
pack=[]
for name,t in zip(names,tasks):
 if t['id'] not in scores:continue
 item={**t,**scores[t['id']],'name':name}
 for cond in ['baseline','plugin']:
  record=next(x for x in records['results'] if x['task']==t['id'] and x['condition']==cond)
  item[cond].update(turns=record['turns'],checks=checks[t['id']+'--'+cond])
 pack.append(item)
fig,(ax,bx)=plt.subplots(1,2,figsize=(14,9),gridspec_kw={'width_ratios':[3,1.45]});fig.subplots_adjust(left=.21,right=.94,top=.82,bottom=.14,wspace=.23)
winlabels={'tie':'同等','baseline':'なし優位','plugin':'あり優位'}
for i,d in enumerate(pack):
 b=sum(d['baseline']['scores']);p=sum(d['plugin']['scores']);delta=p-b
 ax.barh(i-.16,b,height=.28,color='#64748b',label='なし' if i==0 else None)
 ax.barh(i+.16,p,height=.28,color='#0284c7',label='あり' if i==0 else None)
 ax.text(b+.12,i-.16,str(b),fontsize=10,va='center');ax.text(p+.12,i+.16,str(p),fontsize=10,va='center')
 ax.text(18.1,i,f'{delta:+d}',fontsize=11,ha='center',va='center')
 cb=d['baseline']['checks']['characters'][-1];cp=d['plugin']['checks']['characters'][-1]
 bx.barh(i,cp/cb,height=.42,color='#64748b');bx.text(cp/cb+.04,i,f'{cp/cb:.2f}倍',fontproperties=fp,fontsize=10,va='center')
ax.set_yticks(range(len(pack)),[d['name'] for d in pack],fontproperties=fp,fontsize=10);ax.invert_yaxis();ax.set_xlim(0,19);ax.set_xticks([0,4,8,12,16]);ax.set_xlabel('同一課題の基準別合計（16点満点）',fontproperties=fp)
ax.legend(prop=fp,ncol=2,frameon=False,loc='lower left',bbox_to_anchor=(0,1.025));ax.text(18.1,-.8,'差',fontproperties=fp,ha='center')
bx.set_yticks(range(len(pack)),['']*len(pack));bx.invert_yaxis();bx.axvline(1,color='#94a3b8',lw=1);bx.set_xlim(0,max(1.8,max(d['plugin']['checks']['characters'][-1]/d['baseline']['checks']['characters'][-1] for d in pack)+.65));bx.set_title('最終回答の文字数比',fontproperties=fp,fontsize=12,pad=20);bx.set_xlabel('あり ÷ なし（短い＝高品質ではない）',fontproperties=fp,fontsize=10)
for a in [ax,bx]:
 a.grid(axis='x',alpha=.13);a.set_axisbelow(True);a.tick_params(length=0)
 for s in a.spines.values():s.set_visible(False)
fig.text(.04,.951,'条件変更への対応：プラグインなし／あり',fontproperties=fp,fontsize=21)
fig.text(.04,.903,'12人格 × 2ターン。条件名を伏せた別文脈のAI採点と、実測量を分けて比較。',fontproperties=fp,fontsize=12)
fig.text(.04,.064,'各人格で課題・4評価軸が異なるため、人格間の点数順位には意味がありません。採点差は有意差ではありません。',fontproperties=fp,fontsize=10)
fig.text(.04,.034,'GPT-6 Astra / low / 各条件1会話。同じモデルによる採点で、独立した専門家評価や完全な盲検ではありません。',fontproperties=fp,fontsize=10)
for ext in ['svg','png']:fig.savefig(ROOT/('comparison.'+ext),dpi=150,facecolor='white')
plt.close(fig);svg=ROOT/'comparison.svg';svg.write_text('\n'.join(l.rstrip() for l in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
page="""<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>条件変更への対応を比較</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#172330;font:16px/1.65 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:28px 22px}h1{font-size:28px}h2{font-size:21px}img{width:100%;height:auto}select{font:inherit;padding:10px;max-width:100%}.card{background:white;border-radius:10px;padding:22px;margin:20px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}.answer{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}td,th{padding:11px;border-bottom:1px solid #d8e0e8;text-align:left;vertical-align:top}table{width:100%;border-collapse:collapse;font-size:14px}.note{color:#475569}.score{color:#0369a1}summary{cursor:pointer;padding:8px 0}a{color:#0369a1}@media(max-width:700px){main{padding:15px}.pair{grid-template-columns:1fr}.card{padding:15px}table{font-size:12px}td,th{padding:7px}}</style><main><h1>初回の回答と、条件変更への対応を比較する</h1><p class="note">同じ2段階の課題。満点の多かった前回から課題を改め、A/B匿名採点と実測の検証を分けました。</p><img src="comparison.svg" alt="人格ごとの基準別得点と最終回答文字数の比較。詳細は下の課題選択で確認できます。"><section class="card"><label for="task">課題を選ぶ </label><select id="task"></select><h2 id="title"></h2><p id="verdict"></p><details open><summary>初回と追加入力</summary><p id="q1"></p><p id="q2"></p></details><table><thead><tr><th>事前固定の評価軸</th><th>なし（0〜4）</th><th>あり（0〜4）</th></tr></thead><tbody id="rubric"></tbody></table><p class="note" id="measure"></p></section><div class="pair"><section class="card"><h2>なし <span id="bs" class="score"></span></h2><details><summary>初回回答</summary><div class="answer" id="b1"></div></details><h3>追加情報後の回答</h3><div class="answer" id="b2"></div></section><section class="card"><h2>あり <span id="ps" class="score"></span></h2><details><summary>初回回答</summary><div class="answer" id="p1"></div></details><h3>追加情報後の回答</h3><div class="answer" id="p2"></div></section></div><footer class="card"><p>点数差とA/Bの優位判定は別です。小さな点数差があっても実質同等と判定される場合があります。1課題・1会話では安定した性能差や一般的優劣を証明できません。条件名は採点入力から除外しましたが、語調から推測できる可能性があります。</p><p>文章量は品質点に直結させません。文字数は空白除外、禁止語検査は引用や説明にも反応するため原文確認が必要です。</p><a href="README.md">レポート</a> · <a href="scores.json">採点</a> · <a href="results.json">応答・使用量</a> · <a href="checks.json">機械検査</a> · <a href="tasks.json">事前課題</a></footer></main><script>
const data=__DATA__,select=document.getElementById('task'),labels={tie:'実質同等',baseline:'プラグインなし優位',plugin:'プラグインあり優位'};data.forEach((d,i)=>{let o=document.createElement('option');o.value=i;o.textContent=d.name+' — '+d.title;select.appendChild(o)});
function render(){const d=data[Number(select.value)];document.getElementById('title').textContent=d.title;document.getElementById('verdict').textContent=labels[d.winner]+'：'+d.reason;document.getElementById('q1').textContent='初回：'+d.turns[0];document.getElementById('q2').textContent='追加：'+d.turns[1];let body=document.getElementById('rubric');body.replaceChildren();d.criteria.forEach((c,i)=>{let row=document.createElement('tr');[c,d.baseline.scores[i]+'点：'+d.baseline.evidence[i],d.plugin.scores[i]+'点：'+d.plugin.evidence[i]].forEach(v=>{let cell=document.createElement('td');cell.textContent=v;row.appendChild(cell)});body.appendChild(row)});[['b','baseline'],['p','plugin']].forEach(([pre,key])=>{let v=d[key];document.getElementById(pre+'s').textContent=v.scores.reduce((a,b)=>a+b,0)+'/16';document.getElementById(pre+'1').textContent=v.turns[0].response;document.getElementById(pre+'2').textContent=v.turns[1].response;});let b=d.baseline.checks,p=d.plugin.checks;document.getElementById('measure').textContent='文字数（初回→最終）：なし '+b.characters.join('→')+' ／あり '+p.characters.join('→')+(d.id==='acepilot'?'。事前コードテスト：なし '+b.passed+'/12、あり '+p.passed+'/12':'');}
select.addEventListener('change',render);render();</script></html>"""
(ROOT/'dashboard.html').write_text(page.replace('__DATA__',json.dumps(pack,ensure_ascii=False).replace('<','\u003c')),encoding='utf-8')
counts={k:sum(d['winner']==k for d in pack) for k in ['baseline','plugin','tie']}
lines=['## 結果','','![比較図](comparison.svg)','','[対話的な比較画面](dashboard.html)はファイルとして開くと動作します（GitHubではソース表示）。回答と根拠は以下のデータでも確認できます。','',f'匿名評価の判定：なし優位 {counts["baseline"]}、あり優位 {counts["plugin"]}、実質同等 {counts["tie"]}。この比率は汎用的な勝率ではありません。','',
'| 人格 | 課題 | なし | あり | 差 | 判定 | 最終文字数 なし→あり |','| --- | --- | ---: | ---: | ---: | --- | ---: |']
for d in pack:
 b=sum(d['baseline']['scores']);p=sum(d['plugin']['scores']);cb=d['baseline']['checks']['characters'][-1];cp=d['plugin']['checks']['characters'][-1]
 lines.append(f'| {d["name"]} | {d["title"]} | {b} | {p} | {p-b:+d} | {winlabels[d["winner"]]} | {cb}→{cp} |')
lines+=['','### 読み方','','得点は4項目の充足度の合計で、性能の倍率・統計的有意差ではありません。小さな得点差でもA/B比較は同等と判定する場合があります。評価軸が人格ごとに異なるため人格間の順位表には使えません。','',
'コードは事前固定した12ケースと1回走査・入力不変を検証。[機械検査](checks.json)と[採点根拠](scores.json)、[採点者への入力](judge-inputs)、[採点原文](judge-results.json)を公開しています。採点者は実行結果を見ずに回答文を評価したため、テストを実施していないとの指摘は回答者の記述についてであり、後から行ったこちらの実行検証とは別です。','',
'元の人格・同梱資料は変更していません。回答の条件名と人格名だけを採点入力から外し、初回と追加回答を提示しました。試行ごとのばらつきは測っていないため、今回の差は次に検証すべき仮説です。','',
'### 各課題の匿名判定理由','']
for d in pack:lines.append('- **'+d['name']+'**：'+d['reason'])
if (ROOT/'audit.md').exists():lines+=['',(ROOT/'audit.md').read_text(encoding='utf-8')]
(ROOT/'assessment.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Rendered',len(pack),'pairs;',counts)
