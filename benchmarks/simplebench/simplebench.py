"""Fixed paired evaluation of the complete SimpleBench public sample.

Only final assistant messages are saved. Hidden reasoning is never collected.
Requires a locally authenticated Codex CLI; no API key or non-stdlib package.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, time, urllib.request
from datetime import datetime, timezone
from transport import Server, CODEX

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
PROTOCOL = json.loads((ROOT / 'protocol.json').read_text(encoding='utf-8'))
CONDITIONS = ('baseline', 'sherlock-report')


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.partial')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    tmp.replace(path)


def schedule(protocol=PROTOCOL):
    result = []
    for repeat in range(1, protocol['solver']['repetitions'] + 1):
        def rank(qid):
            return digest((protocol['order']['seed'] + '\0' + str(repeat) + '\0' + str(qid)).encode())
        for index, qid in enumerate(sorted(protocol['dataset']['question_ids'], key=rank)):
            order = CONDITIONS if (index + repeat) % 2 == 0 else CONDITIONS[::-1]
            for condition in order:
                result.append({'sequence': len(result) + 1, 'repeat': repeat, 'question_id': qid,
                               'condition': condition, 'key': f'r{repeat:02}-q{qid:02}-{condition}'})
    return result


def score(response, expected):
    # Same first-match extractor as the upstream scorer. Missing output is incorrect.
    matches = re.findall(r'Final Answer:\s*([A-F])', response.strip(), re.IGNORECASE)
    answer = matches[0].upper() if matches else None
    return {'selected_answer': answer, 'correct': answer == expected,
            'answer_marker_count': len(matches), 'format_issue': len(matches) != 1}


def load_dataset(cache):
    cfg = PROTOCOL['dataset']
    path = cache / cfg['file']
    if digest(path.read_bytes()) != cfg['sha256']:
        raise RuntimeError('Official dataset digest does not match the fixed revision')
    rows = read(path)['eval_data']
    if len(rows) != cfg['count'] or sorted(r['question_id'] for r in rows) != cfg['question_ids']:
        raise RuntimeError('Dataset questions differ from the registered full public sample')
    for row in rows:
        if not isinstance(row['prompt'], str) or row['answer'] not in 'ABCDEF' or len(row['answer']) != 1:
            raise RuntimeError('Invalid official question or key')
    return {row['question_id']: row for row in rows}


def prepare(cache):
    cache.mkdir(parents=True, exist_ok=True)
    cfg = PROTOCOL['dataset']
    path = cache / cfg['file']
    if not path.exists():
        url = f"https://raw.githubusercontent.com/{cfg['repository']}/{cfg['revision']}/{cfg['file']}"
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
        if digest(data) != cfg['sha256']:
            raise RuntimeError('Downloaded dataset digest mismatch')
        path.write_bytes(data)
    load_dataset(cache)
    src = REPO / 'plugins/sherlock-report/skills/sherlock-report'
    if digest((src / 'SKILL.md').read_bytes()) != PROTOCOL['plugin']['skill_sha256']:
        raise RuntimeError('Plugin changed; start a new series instead of mixing versions')
    if (src / 'system-prompt/inst.txt').read_text(encoding='utf-8-sig').strip() not in (src / 'SKILL.md').read_text(encoding='utf-8-sig'):
        raise RuntimeError('Full source prompt is not embedded in SKILL.md')
    for condition in CONDITIONS:
        cwd = cache / 'work' / condition
        cwd.mkdir(parents=True, exist_ok=True)
        if condition == 'sherlock-report':
            dest = cwd / '.agents/skills/sherlock-report'
            if not dest.exists():
                shutil.copytree(src, dest)
            if (dest / 'SKILL.md').read_bytes() != (src / 'SKILL.md').read_bytes():
                raise RuntimeError('Native skill copy is not byte-identical')
    write(ROOT / 'schedule.json', schedule())
    print('Prepared 10 questions, 50 paired trials, 100 model calls.', flush=True)


def preflight(server, cache):
    audit = {}
    for condition in CONDITIONS:
        cwd = cache / 'work' / condition
        inventory = server.call('skills/list', {'cwds': [str(cwd)], 'forceReload': True})
        enabled = [s for group in inventory['data'] for s in group['skills'] if s['enabled']]
        sherlock = [s for s in enabled if s['name'] == 'sherlock-report']
        if condition == 'baseline' and sherlock:
            raise RuntimeError('Sherlock is discoverable in baseline; isolation failed')
        if condition == 'sherlock-report':
            expected = cwd / '.agents/skills/sherlock-report/SKILL.md'
            if len(sherlock) != 1 or Path(sherlock[0]['path']) != expected:
                raise RuntimeError('Native full-skill discovery failed')
        audit[condition] = {'enabled_skill_names': sorted(s['name'] for s in enabled),
                            'sherlock_available': bool(sherlock)}
    return audit


def infer(server, cache, item, question):
    condition = item['condition']
    cwd = cache / 'work' / condition
    solver = PROTOCOL['solver']
    common = PROTOCOL['prompts']['common_developer_instructions']
    instructions = common + '\n\n' + PROTOCOL['prompts']['official_system_prompt']
    info = server.call('thread/start', {
        'model': solver['model'], 'allowProviderModelFallback': False,
        'cwd': str(cwd), 'ephemeral': True, 'approvalPolicy': 'never', 'sandbox': 'read-only',
        'developerInstructions': instructions, 'selectedCapabilityRoots': [],
        'config': {'model_reasoning_effort': solver['effort'], 'model_verbosity': 'low'},
    })
    if info.get('model') != solver['model']:
        raise RuntimeError('Unexpected model fallback')
    tid = info['thread']['id']
    # Raw start metadata is local only; never published.
    write(cache / 'metadata' / (item['key'] + '.json'), info)
    inputs = []
    prompt = question['prompt']  # The answer key and question ID are NOT passed to the solver.
    if condition == 'sherlock-report':
        skill = cwd / '.agents/skills/sherlock-report/SKILL.md'
        inputs.append({'type': 'skill', 'name': 'sherlock-report', 'path': str(skill)})
        prompt = '$sherlock-report\n' + prompt
    inputs.append({'type': 'text', 'text': prompt})
    started = time.monotonic()
    server.request_id += 1
    rid = server.request_id
    server.send({'id': rid, 'method': 'turn/start', 'params': {
        'threadId': tid, 'model': solver['model'], 'effort': solver['effort'],
        'summary': 'none', 'input': inputs,
    }})
    response = ''
    usage = None
    tool_calls = []
    result = {**item, 'status': 'running', 'timestamp_utc': now(),
              'model_requested': solver['model'], 'model_resolved': info['model'],
              'effort': solver['effort']}
    try:
        while time.monotonic() - started < solver['timeout_seconds']:
            msg = server.receive(max(.1, solver['timeout_seconds'] - (time.monotonic() - started)))
            if msg.get('id') == rid and 'error' in msg:
                raise RuntimeError('turn/start error: ' + json.dumps(msg['error']))
            params = msg.get('params', {})
            if params.get('threadId') != tid:
                continue
            method = msg.get('method')
            if method == 'thread/tokenUsage/updated':
                usage = params['tokenUsage']['total']
            if method == 'item/completed':
                model_item = params['item']
                kind = model_item['type']
                if kind == 'agentMessage' and model_item.get('phase') != 'commentary':
                    response += model_item.get('text', '') + '\n'
                if kind in ('commandExecution', 'mcpToolCall', 'webSearch', 'fileChange', 'dynamicToolCall',
                            'collabAgentToolCall', 'imageGeneration', 'enteredReviewMode'):
                    tool_calls.append(kind)
            if method == 'turn/completed':
                if params['turn']['status'] != 'completed' or tool_calls or usage is None or not response.strip():
                    raise RuntimeError('Invalid completion: ' + json.dumps({'status': params['turn']['status'],
                                       'error': params['turn'].get('error'), 'tools': tool_calls,
                                       'usage_available': usage is not None, 'response_present': bool(response)}))
                result['status'] = 'completed'
                break
        else:
            raise TimeoutError('Turn timed out; no automatic retry')
    except Exception as exc:
        result['status'] = 'failed'
        result['error'] = str(exc)
    result.update(response=response.strip(), usage=usage, tool_calls=tool_calls,
                  seconds=round(time.monotonic() - started, 3), completed_at=now())
    return result


def run(cache, max_calls):
    questions = load_dataset(cache)
    code_files = ('simplebench.py', 'transport.py', 'protocol.json', 'schedule.json')
    if subprocess.check_output(['git', '-C', str(REPO), 'diff', 'HEAD', '--',
                               *['benchmarks/simplebench/' + name for name in code_files]], text=True).strip():
        raise RuntimeError('Commit the protocol and executable source before model calls')
    version = subprocess.check_output([str(CODEX), '--version'], text=True).strip()
    if version != PROTOCOL['solver']['codex_version']:
        raise RuntimeError('Codex version differs from the registered environment')
    state_path = cache / 'state.json'
    if state_path.exists():
        state = read(state_path)
        if state['protocol_sha256'] != digest((ROOT / 'protocol.json').read_bytes()):
            raise RuntimeError('Protocol changed after the first call')
        if state['source_hashes'] != {name: digest((ROOT / name).read_bytes()) for name in code_files}:
            raise RuntimeError('Executable source changed during the run')
    else:
        state = {'series': PROTOCOL['series'], 'started_at': now(), 'codex_version': version,
                 'protocol_sha256': digest((ROOT / 'protocol.json').read_bytes()),
                 'source_hashes': {name: digest((ROOT / name).read_bytes()) for name in code_files},
                 'registration_commit': subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip(),
                 'attempts': {}}
    for value in state['attempts'].values():
        if value['status'] != 'completed':
            raise RuntimeError('An interrupted/failed attempt needs manual audit; it will not be rerun')
    server = Server(cache)
    made = 0
    try:
        state['skill_discovery'] = preflight(server, cache)
        write(state_path, state)
        for item in schedule():
            if item['key'] in state['attempts']:
                continue
            state['attempts'][item['key']] = {**item, 'status': 'started', 'timestamp_utc': now()}
            write(state_path, state)
            print(f"START {item['sequence']}/100 {item['key']}", flush=True)
            result = infer(server, cache, item, questions[item['question_id']])
            write(cache / 'responses' / (item['key'] + '.json'), result)
            state['attempts'][item['key']] = result
            state['updated_at'] = now()
            write(state_path, state)
            print(f"DONE {item['sequence']}/100 status={result['status']} seconds={result['seconds']}", flush=True)
            if result['status'] != 'completed':
                raise RuntimeError(result.get('error', 'Failed turn'))
            made += 1
            if max_calls and made >= max_calls:
                break
        if len(state['attempts']) == 100:
            state['completed_at'] = now()
            write(state_path, state)
    finally:
        server.close()
    from report import render
    render(cache)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'preflight', 'run', 'report'])
    parser.add_argument('--cache', type=Path, default=REPO.parent / 'plugin-benchmark/simplebench-2026-09-19')
    parser.add_argument('--max-calls', type=int, default=0)
    args = parser.parse_args()
    cache = args.cache.resolve()
    if cache == REPO or REPO in cache.parents:
        raise RuntimeError('Keep the private cache outside the public repository')
    if args.command == 'prepare':
        prepare(cache)
    elif args.command == 'preflight':
        server = Server(cache)
        try:
            audit = preflight(server, cache)
            write(cache / 'preflight.json', audit)
            print(json.dumps(audit, ensure_ascii=False, indent=2))
        finally:
            server.close()
    elif args.command == 'run':
        run(cache, args.max_calls)
    else:
        from report import render
        render(cache)


if __name__ == '__main__':
    main()
