"""Deterministic scoring and reporting. Uses question clusters for uncertainty."""
from pathlib import Path
import json, random, statistics
from simplebench import ROOT, PROTOCOL, CONDITIONS, read, write, score, load_dataset, schedule


def percentile(values, q):
    values = sorted(values)
    x = (len(values) - 1) * q
    lo = int(x)
    return values[lo] + (values[min(lo + 1, len(values) - 1)] - values[lo]) * (x - lo)


def paired_interval(differences):
    if not differences:
        return None
    rng = random.Random(20260919)
    boot = [sum(rng.choices(differences, k=len(differences))) / len(differences) for _ in range(10000)]
    return [round(percentile(boot, .025) * 100, 2), round(percentile(boot, .975) * 100, 2)]


def summarize(rows):
    summary = {}
    for condition in CONDITIONS:
        completed = [r for r in rows if r['condition'] == condition and r['status'] == 'completed']
        correct = sum(r['correct'] for r in completed)
        times = [r['seconds'] for r in completed]
        summary[condition] = {
            'completed': len(completed), 'planned': 50, 'correct': correct,
            'accuracy_pct': round(100 * correct / len(completed), 2) if completed else None,
            'format_issues': sum(r['format_issue'] for r in completed),
            'mean_seconds': round(statistics.mean(times), 3) if times else None,
            'median_seconds': round(statistics.median(times), 3) if times else None,
            'usage': {key: sum((r.get('usage') or {}).get(key, 0) for r in completed)
                      for key in ('inputTokens', 'cachedInputTokens', 'outputTokens', 'reasoningOutputTokens', 'totalTokens')},
        }
    questions = []
    counts = {'both_correct': 0, 'baseline_only': 0, 'sherlock_only': 0, 'both_incorrect': 0, 'complete_pairs': 0}
    keyed = {(r['repeat'], r['question_id'], r['condition']): r for r in rows if r['status'] == 'completed'}
    for qid in PROTOCOL['dataset']['question_ids']:
        row = {'question_id': qid}
        for condition in CONDITIONS:
            values = [keyed[(rep, qid, condition)] for rep in range(1, 6) if (rep, qid, condition) in keyed]
            row[condition] = {'correct': sum(v['correct'] for v in values), 'completed': len(values),
                              'answers': [v['selected_answer'] for v in values]}
        questions.append(row)
        for rep in range(1, 6):
            pair = [keyed.get((rep, qid, c)) for c in CONDITIONS]
            if not all(pair):
                continue
            a, b = [p['correct'] for p in pair]
            counts['complete_pairs'] += 1
            counts['both_correct' if a and b else 'baseline_only' if a else 'sherlock_only' if b else 'both_incorrect'] += 1
    complete = len(keyed) == 100
    differences = [(q['sherlock-report']['correct'] - q['baseline']['correct']) / 5 for q in questions] if complete else []
    comparison = {**counts, 'difference_percentage_points': round(statistics.mean(differences) * 100, 2) if differences else None,
                  'paired_question_bootstrap_95pct_pp': paired_interval(differences), 'question_clusters': 10,
                  'inference_scope': 'Exploratory public sample; repeats are not new questions.'}
    repetitions = []
    for rep in range(1, 6):
        item = {'repeat': rep}
        for condition in CONDITIONS:
            values = [r for r in rows if r['repeat'] == rep and r['condition'] == condition and r['status'] == 'completed']
            item[condition] = {'correct': sum(r['correct'] for r in values), 'completed': len(values)}
        repetitions.append(item)
    return summary, questions, comparison, repetitions


def render(cache):
    state_path = cache / 'state.json'
    state = read(state_path) if state_path.exists() else {'attempts': {}}
    questions_by_id = load_dataset(cache)
    rows = []
    fields = ('sequence', 'repeat', 'question_id', 'condition', 'key', 'status', 'timestamp_utc', 'completed_at',
              'model_requested', 'model_resolved', 'effort', 'seconds', 'response', 'usage', 'tool_calls')
    for item in schedule():
        raw = state['attempts'].get(item['key'])
        if raw is None:
            continue
        row = {key: raw.get(key) for key in fields}
        row['expected_answer'] = questions_by_id[item['question_id']]['answer']
        if row['status'] == 'completed':
            row.update(score(row['response'], row['expected_answer']))
        else:
            row.update(selected_answer=None, correct=None, answer_marker_count=0, format_issue=None)
        rows.append(row)
    summary, questions, comparison, repetitions = summarize(rows)
    count = sum(v['completed'] for v in summary.values())
    result = {'series': PROTOCOL['series'], 'status': 'completed' if count == 100 else 'incomplete' if rows else 'registered',
              'completed_answers': count, 'planned_answers': 100, 'registration_commit': state.get('registration_commit'),
              'started_at': state.get('started_at'), 'completed_at': state.get('completed_at'),
              'protocol_sha256': state.get('protocol_sha256'), 'source_hashes': state.get('source_hashes'),
              'skill_discovery': state.get('skill_discovery'), 'summary': summary,
              'comparison': comparison, 'by_question': questions, 'by_repetition': repetitions,
              'trials': rows}
    write(ROOT / 'results.json', result)
    lines = ['# SimpleBench公開10問：プラグインなし / Sherlock Report', '',
             '**公式ランキングのスコアではありません。** 公開サンプル全10問を各条件5回ずつ、履歴を共有しない新しい会話で評価します。', '',
             f'状態：**{count}/100回答完了**。GPT-6 Astra / reasoning medium / ツール無効。', '',
             '| 条件 | 正解数 | 正答率 | 平均応答時間 | 入力 / 出力トークン |',
             '|---|---:|---:|---:|---:|']
    for condition, label in (('baseline', 'プラグインなし'), ('sherlock-report', 'Sherlock Report')):
        s = summary[condition]
        rate = f"{s['accuracy_pct']:.1f}%" if s['accuracy_pct'] is not None else '未実施'
        latency = f"{s['mean_seconds']:.2f}秒" if s['mean_seconds'] is not None else '—'
        u = s['usage']
        lines.append(f"| {label} | {s['correct']}/{s['completed']} | {rate} | {latency} | {u['inputTokens']:,} / {u['outputTokens']:,} |")
    if count == 100:
        diff = comparison['difference_percentage_points']
        ci = comparison['paired_question_bootstrap_95pct_pp']
        conclusion = 'この公開サンプルでは同点でした。' if diff == 0 else ('この公開サンプルではSherlock Reportの正答率が高くなりました。' if diff > 0 else 'この公開サンプルではプラグインなしの正答率が高くなりました。')
        lines += ['', f"{conclusion} 差（Sherlock − なし）は **{diff:+.1f}ポイント**。問題単位のペア・ブートストラップ95%区間は {ci[0]:+.1f}～{ci[1]:+.1f}ポイントです。公開10問の探索的結果であり、一般的な能力差を確立するものではありません。", '',
                  f"50ペアの内訳：両方正解 {comparison['both_correct']}、なしのみ正解 {comparison['baseline_only']}、Sherlockのみ正解 {comparison['sherlock_only']}、両方不正解 {comparison['both_incorrect']}。", '',
                  '![比較結果](comparison.svg)', '']
    lines += ['', '## 比較条件と採点', '',
              '- 問題は公式公開JSONの全10問。翻訳・書き換え・選択肢変更・成績による選別はありません。公式の非公開問題群にはアクセスしていません。',
              '- モデル、推論設定、共通指示、問題文、ツール制限は両条件で共通。Sherlock条件だけに改変していないSKILL.md全文をnative skill入力で適用します。スキル検出とバイト一致を確認しています。',
              '- Codexの通常ホスト指示は共通して残ります。「プラグインなし」はSherlockを読み込まないCodexであり、システム指示のない素のAPIモデルではありません。',
              '- 各問題×各条件×各反復に新規コンテキストを作成。固定seedで問題順を決め、先に実行する条件を交互に変更します。検索・Python・その他ツール、記憶、追加プラグインは無効です。',
              '- 共通の実行制約に公式system_promptを追加。両条件に簡潔な説明を求めます。temperature、top-p、出力トークン上限は明示指定せず、Codex/モデルの既定値を用います。公式ランキングと実行条件は異なります。',
              '- 正解キーは解答モデルに渡しません。公式実装と同じ正規表現で最初の `Final Answer: A～F` を抽出し、正解キーと比較します。抽出失敗は不正解、複数マーカーは警告として記録します。LLM採点・手動修正はありません。',
              '- 主指標は50回答の平均正答率。5回の多数決・最高点・pass@5ではありません。未完了は未完了として表示し、完了済みの回答を再生成しません。失敗・中断は自動再試行しません。',
              '- 不確かさは10問を単位とするペア・ブートストラップ（10,000回、seed固定）で記述します。同じ問題の5反復を別々の50問とみなしません。検定による優越性の主張はしません。', '',
              '## 問題ごとの結果', '', '| 問題ID | なし | Sherlock | 差（正解数） |', '|---|---:|---:|---:|']
    for q in questions:
        a, b = q['baseline'], q['sherlock-report']
        lines.append(f"| {q['question_id']} | {a['correct']}/{a['completed']} | {b['correct']}/{b['completed']} | {b['correct'] - a['correct']:+} |")
    lines += ['', '## 反復ごとの結果', '', '| 反復 | なし | Sherlock |', '|---|---:|---:|']
    for r in repetitions:
        a, b = r['baseline'], r['sherlock-report']
        lines.append(f"| {r['repeat']} | {a['correct']}/{a['completed']} | {b['correct']}/{b['completed']} |")
    total = sum(s['usage']['totalTokens'] for s in summary.values())
    issues = sum(s['format_issues'] for s in summary.values())
    lines += ['', '## 解釈上の限界', '',
              '公開済みの少数問題なので、学習時の接触や暗記を排除できません。5反復は回答の揺れを測りますが、問題の種類は10問のままです。ブートストラップ区間もこの少数問題に基づく記述的な目安です。全問同じ成績なら区間が0に縮んでも、未知問題での能力差がないことを証明しません。', '',
              '今回はツールなしの選択式推論に限定しています。Sherlockのウェブ調査・Python検算・論文作成能力は測っていません。人格定義内の最大推論要求にかかわらず、推論設定は比較のため両方mediumに固定しています。同じモデル名でも提供側の更新は排除できません。', '',
              f'記録された評価呼び出しの総トークンは {total:,}。キャッシュは入力の内数、推論トークンは出力の内数です。準備・集計を行う親タスクの使用量は含みません。最終回答形式の警告は {issues} 件です。応答時間はターン送信から完了までで、スキル検出や会話作成時間は含みません。', '',
              '## 再現と監査', '',
              '[固定プロトコル](protocol.json) / [事前固定した実行順](schedule.json) / [全100回答・正誤・使用量](results.json) / [実行コード](simplebench.py) / [採点と集計](report.py) / [検証](test_simplebench.py)', '',
              '認証済みのCodex CLIとPython 3.10以降を使います。モデルとCLI版はprotocol.jsonに固定しています。別の版で実行するときは既存結果を上書きせず、別シリーズとして登録してください。', '',
              '```powershell', 'python benchmarks/simplebench/simplebench.py prepare', 'python benchmarks/simplebench/simplebench.py preflight', 'python -m unittest discover -s benchmarks/simplebench -p "test_*.py"',
              '# Commit protocol, schedule, and source before the first model call.', 'python benchmarks/simplebench/simplebench.py run', 'python benchmarks/simplebench/simplebench.py report', '```', '',
              'キャッシュはリポジトリ外の `../plugin-benchmark/simplebench-2026-09-19`。`--cache` で別のリポジトリ外フォルダを指定できます。そこに公式データ・最終応答・ローカル実行記録を保存します。モデルから返された最終回答だけを公開し、内部推論、認証情報、ローカルパスを含む生ログは公開しません。図は `python benchmarks/simplebench/plot.py` で再生成します（Matplotlibが必要）。', '']
    if state.get('registration_commit'):
        commit = state['registration_commit']
        lines += [f'初回出題前の登録コミット：[ {commit[:7]} ](https://github.com/sharakusatoh/codex-plugins/commit/{commit})。実行日時（UTC）：{state.get("started_at")} ～ {state.get("completed_at") or "進行中"}。', '']
    rev = PROTOCOL['dataset']['revision']
    lines += ['## 出典', '',
              f'- [SimpleBench公式データとコード](https://github.com/simple-bench/SimpleBench/tree/{rev})。取得したJSONのSHA-256はprotocol.jsonに保存。上流のMITライセンスは [SIMPLEBENCH-LICENSE.txt](SIMPLEBENCH-LICENSE.txt) に収録。',
              '- [SimpleBench公式サイト](https://simple-bench.com/)',
              '- [Codex App Server公式資料](https://developers.openai.com/ja-JP/docs/app-server)', '']
    if (ROOT / 'REPORT-NOTES.md').is_file():
        lines += ['', (ROOT / 'REPORT-NOTES.md').read_text(encoding='utf-8').strip(), '']
    (ROOT / 'README.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    print(json.dumps({'completed': count, 'summary': summary, 'comparison': comparison}, ensure_ascii=False), flush=True)
    return result
