from pathlib import Path
import json,html,sys
ROOT=Path(__file__).resolve().parent
local_deps=ROOT.parent/'chart-deps'
if local_deps.exists():sys.path.insert(0,str(local_deps))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
repo=ROOT.parent.parent/'codex-plugins'
if not repo.exists():repo=ROOT.parent.parent
font=repo/'plugins/work-force/skills/work-force/assets/fonts/NotoSansJP-Medium.ttf'
fp=FontProperties(fname=str(font))
plt.rcParams['svg.fonttype']='path'
tasks=json.loads((ROOT/'tasks.json').read_text(encoding='utf-8'))['tasks']
scores=json.loads((ROOT/'scores.json').read_text(encoding='utf-8'))
public=repo/'benchmarks/2026-09-18-capability/results.json'
results=json.loads(public.read_text(encoding='utf-8'))
names=['Sherlock Report','AcePilot','Beautiful Dreamer','Edgar Rumple','Expert Moriarty','Flight Attendant','Ghost Blogger','Inspire Lestrade','Mycroft Debater','Rorschach Security','Work Force','Mrs. Legal Advisor']
fig,ax=plt.subplots(figsize=(13,9));fig.subplots_adjust(left=.31,right=.91,top=.88,bottom=.13)
for i,t in enumerate(tasks):
 s=scores[t['id']];b=sum(s['baseline']['scores']);p=sum(s['plugin']['scores'])
 ax.barh(i-.16,b,height=.27,color='#64748b',label='なし' if i==0 else None)
 ax.barh(i+.16,p,height=.27,color='#0284c7',label='あり' if i==0 else None)
 ax.text(b+.09,i-.16,str(b),va='center',fontsize=10,color='#334155')
 ax.text(p+.09,i+.16,str(p),va='center',fontsize=10,color='#075985')
 ax.text(11.15,i,f'{p-b:+d}',ha='center',va='center',fontsize=12,fontweight='bold')
ax.set_yticks(range(12),[n+' / '+t['title'] for n,t in zip(names,tasks)],fontproperties=fp,fontsize=10)
ax.invert_yaxis();ax.set_xlim(0,11.7);ax.set_xticks(range(0,11,2));ax.set_xlabel('各課題の基準充足点（10点満点）',fontproperties=fp)
ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
for spine in ax.spines.values():spine.set_visible(False)
ax.tick_params(axis='both',length=0)
ax.legend(prop=fp,frameon=False,loc='lower right',bbox_to_anchor=(1,1.015),ncol=2)
ax.text(11.15,-.82,'差',fontproperties=fp,ha='center')
fig.text(.04,.958,'人格別の能力課題：プラグインなし／あり',fontproperties=fp,fontsize=21)
fig.text(.04,.916,'同じ課題内の比較。異なる課題の点数で人格を順位付けしない。',fontproperties=fp,fontsize=12)
fig.text(.04,.054,'GPT-6 Astra / low / 各条件1回 / 非盲検のAI採点。多くの課題で満点に達し、差の検出力は限定的。',fontproperties=fp,fontsize=10)
fig.text(.04,.025,'Sherlockの差は仮説ごとの観測予測。AcePilotは両方7/7ケース通過、定義したスロップ4項目は両方0件。',fontproperties=fp,fontsize=10)
for ext in ['png','svg']:fig.savefig(ROOT/('comparison.'+ext),dpi=160,facecolor='white')
plt.close(fig)
svg=ROOT/'comparison.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
pack=[]
for n,t in zip(names,tasks):
 item={**t,'name':n,**scores[t['id']]}
 for c in ['baseline','plugin']:
  row=next(x for x in results['results'] if x['task']==t['id'] and x['condition']==c)
  item[c].update(response=row['response'],usage=row['usage'])
 pack.append(item)
data=json.dumps(pack,ensure_ascii=False).replace('<','\u003c')
page="""<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>人格別・能力比較</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#172330;font:16px/1.65 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:32px 24px}h1{font-size:28px;line-height:1.4;margin:0 0 12px}h2{font-size:20px}.note{color:#485665;max-width:960px}img{width:100%;height:auto;background:white;border-radius:12px}select{max-width:100%;padding:10px;font:inherit;background:white;border:1px solid #8b99a7;border-radius:6px}.panel{background:white;border-radius:12px;padding:24px;margin:20px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}.answer{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.8 system-ui,sans-serif}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #dae1e7;padding:12px;text-align:left;vertical-align:top}.score{font-weight:700;font-size:22px;color:#075985}summary{cursor:pointer}footer{margin:28px 0;color:#485665}a{color:#0369a1}@media(max-width:720px){main{padding:20px 12px}.pair{grid-template-columns:1fr}.panel{padding:15px}h1{font-size:23px}td,th{padding:8px}table{font-size:12px}}
</style><main><h1>人格別の能力課題を比較する</h1><p class="note">12課題 × プラグインなし／あり。各1回の探索的評価です。異なる課題の得点で人格を順位付けせず、同じ課題の回答差を確認してください。</p>
<img src="comparison.svg" alt="Sherlock Reportは8点から9点。他11課題は同点。Mycroftは両方8点、ほかは両方10点。">
<div class="panel"><label for="task">課題を選ぶ　</label><select id="task"></select><h2 id="title"></h2><p id="question"></p><p id="finding"></p><table><thead><tr><th>事前に固定した基準</th><th>なし（0〜2）</th><th>あり（0〜2）</th></tr></thead><tbody id="rubric"></tbody></table></div>
<div class="pair"><section class="panel"><h2>プラグインなし <span class="score" id="bscore"></span></h2><p class="note" id="busage"></p><div class="answer" id="banswer"></div></section><section class="panel"><h2>プラグインあり <span class="score" id="pscore"></span></h2><p class="note" id="pusage"></p><div class="answer" id="panswer"></div></section></div>
<footer><strong>解釈の限界</strong><p>0＝欠落・誤り、1＝部分的・曖昧、2＝十分具体的。調整役AIによる非盲検採点で、独立した専門家評価ではありません。多くの課題が満点となり、差を検出する難度は不足しています。ツール・Web・多ターンの実務性能は未測定。図の差は効果量や統計的有意差ではありません。</p><p>AcePilotの「スロップ」は不要な抽象化・依存・要求外仕様・定型的水増しの4分類に限定し、両条件0件でした。AI文一般の客観的な指標ではありません。</p><a href="README.md">全結果</a> · <a href="results.json">生データ</a> · <a href="scores.json">採点根拠</a> · <a href="tasks.json">事前課題</a></footer></main>
<script>
const data=__DATA__;
const select=document.getElementById('task');
data.forEach((d,i)=>{const o=document.createElement('option');o.value=i;o.textContent=d.name+' — '+d.title;select.appendChild(o)});
function render(){const d=data[Number(select.value)];document.getElementById('title').textContent=d.title;document.getElementById('question').textContent=d.prompt;document.getElementById('finding').textContent=d.summary;const body=document.getElementById('rubric');body.replaceChildren();d.criteria.forEach((c,i)=>{const tr=document.createElement('tr');[c,d.baseline.scores[i]+'点：'+d.baseline.evidence[i],d.plugin.scores[i]+'点：'+d.plugin.evidence[i]].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td)});body.appendChild(tr)});[['b','baseline'],['p','plugin']].forEach(([prefix,key])=>{const v=d[key];document.getElementById(prefix+'score').textContent=v.scores.reduce((a,b)=>a+b,0)+'/10';document.getElementById(prefix+'answer').textContent=v.response;document.getElementById(prefix+'usage').textContent='入力 '+v.usage.inputTokens.toLocaleString()+' / 出力 '+v.usage.outputTokens.toLocaleString()+' tokens';});}
select.addEventListener('change',render);render();
</script></html>"""
(ROOT/'dashboard.html').write_text(page.replace('__DATA__',data),encoding='utf-8')
lines=['## 比較結果','','![課題別のペア比較](comparison.svg)','','[対話的な比較画面](dashboard.html)はダウンロードして開くか、ローカルで表示できます。GitHub上ではHTMLソースとして表示されます。静的な図は上で閲覧できます。','','| 人格 | 課題 | なし | あり | 差 |','| --- | --- | ---: | ---: | ---: |']
for x in pack:
 b=sum(x['baseline']['scores']);p=sum(x['plugin']['scores']);lines.append(f"| {x['name']} | {x['title']} | {b} | {p} | {p-b:+d} |")
lines+=['','### 読み取れること','','- Sherlockは、仮説ごとの観測予測を明示した点が差になりました。なしも不確実性・競合仮説・測定計画を提示しており、科学的思考ができないという意味ではありません。','- AcePilotは両条件で同じ独立7ケースと提示assertが通過。不要抽象化・依存・要求外仕様・定型的水増しは両条件0件。今回はスロップ低減を示せませんでした。関数の非空行はなし12・あり14で、型注釈等の妥当な違いは減点していません。','- 他の11ペアは基準上同点です。表現や補足の差はあっても、得点を上げるために後から基準を追加していません。','- 多くが満点となる天井効果があります。短い、条件の明確な課題だけでは専門人格の差を捉えにくく、一般的な能力向上や人格が無意味という結論のどちらも導けません。','','### 判定の監査','','[基準別得点・根拠](scores.json)と[コード検証・文字数](checks.json)を公開しています。文章の文字数は空白・改行を除いたUnicode文字数を補助指標として記録し、記号を除く厳密な組版文字数ではありません。AcePilotの追加7ケースは回答後の検証であり、事前固定された隠しテストではありません。','',
'最終監査でSherlockありの予測項目を2→1点に修正しました。忘却・移行の予測はありますが、無意識処理仮説を含む「各仮説」という事前基準を完全には満たさないためです（合計10→9点）。基準自体は変更していません。課題と60基準は回答生成前のコミット `b71ad8a` で公開。採点者は回答条件を知るAIで、独立・盲検・複数人評価ではありません。創作性の好みは採点基準で拾える範囲に限定しました。Mycroftの「双方への判断変更」という基準は両条件で片方向のみのため部分点としています。','',
'各課題1回で誤差・再現性は測れません。差が出るまで再生成することは行っていません。次の評価では、実装の保守変更、反証が難しい未知問題、曖昧な長文資料、多ターンの事情聴取など、満点になりにくい別課題を事前固定して反復する必要があります。','',
'### 課題ごとの所見','']
for x in pack:lines.append('- **'+x['name']+'**：'+x['summary'])
(ROOT/'assessment.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Rendered chart, dashboard, assessment')
