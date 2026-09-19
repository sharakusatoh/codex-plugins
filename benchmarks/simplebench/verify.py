"""Audit a completed run against the registered schedule and private metadata.

Does not call a model, alter answers, or reuse report.py for scoring.
"""
from pathlib import Path
import argparse, ast, collections, hashlib, json, platform, re, subprocess
from simplebench import ROOT, REPO, PROTOCOL, read, digest, schedule, write
from transport import CODEX


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', type=Path, default=REPO.parent / 'plugin-benchmark/simplebench-2026-09-19')
    cache = parser.parse_args().cache.resolve()
    state = read(cache / 'state.json')
    result = read(ROOT / 'results.json')
    plan = schedule()
    assert set(state['attempts']) == {p['key'] for p in plan}
    assert result['completed_answers'] == 100
    assert all(r['status'] == 'completed' for r in state['attempts'].values())
    assert all(not r['tool_calls'] for r in state['attempts'].values())
    assert len(list((cache / 'responses').glob('*.json'))) == 100
    assert len(list((cache / 'metadata').glob('*.json'))) == 100
    expected_scores = collections.Counter()
    raw_questions = read(cache / PROTOCOL['dataset']['file'])['eval_data']
    answer_key = {q['question_id']: q['answer'] for q in raw_questions}
    for item, published in zip(plan, result['trials'], strict=True):
        raw = state['attempts'][item['key']]
        saved = read(cache / 'responses' / (item['key'] + '.json'))
        assert raw == saved
        assert all(published[k] == v for k, v in item.items())
        assert published['response'] == raw['response']
        assert published['usage'] == raw['usage']
        assert raw['model_requested'] == raw['model_resolved'] == PROTOCOL['solver']['model']
        assert raw['effort'] == PROTOCOL['solver']['effort']
        meta = read(cache / 'metadata' / (item['key'] + '.json'))
        assert meta['model'] == PROTOCOL['solver']['model']
        assert meta['reasoningEffort'] == PROTOCOL['solver']['effort']
        assert meta['sandbox'] == {'type': 'readOnly', 'networkAccess': False}
        assert meta['instructionSources'] == []
        match = re.search(r'Final Answer:\s*([A-F])', raw['response'].strip(), re.IGNORECASE)
        answer = match.group(1).upper() if match else None
        expected = answer_key[item['question_id']]
        correct = answer == expected
        assert published['selected_answer'] == answer
        assert published['expected_answer'] == expected
        assert published['correct'] == correct
        expected_scores[item['condition']] += correct
        usage = raw['usage']
        assert usage['totalTokens'] == usage['inputTokens'] + usage['outputTokens']
        assert usage.get('cachedInputTokens', 0) <= usage['inputTokens']
        assert usage.get('reasoningOutputTokens', 0) <= usage['outputTokens']
    for condition in ('baseline', 'sherlock-report'):
        assert result['summary'][condition]['correct'] == expected_scores[condition]
        assert result['summary'][condition]['completed'] == 50
    registered = state['registration_commit']
    def git_blob(path):
        return subprocess.check_output(['git', '-C', str(REPO), 'show', registered + ':' + path])
    for name, expected_hash in state['source_hashes'].items():
        assert digest((ROOT / name).read_bytes()) == expected_hash
        assert digest(git_blob('benchmarks/simplebench/' + name)) == expected_hash
    def metric_ast(source):
        return [ast.dump(node, include_attributes=False) for node in ast.parse(source).body
                if isinstance(node, ast.FunctionDef) and node.name in ('percentile', 'paired_interval', 'summarize')]
    assert metric_ast(git_blob('benchmarks/simplebench/report.py').decode('utf-8-sig')) == metric_ast((ROOT / 'report.py').read_text(encoding='utf-8-sig'))
    reviewed = state.get('reviewed_failed_attempts', [])
    assert len(reviewed) == 1 and reviewed[0]['sequence'] == 45
    assert reviewed[0]['status'] == 'failed' and not reviewed[0]['response'] and reviewed[0]['usage'] is None
    assert 'usageLimitExceeded' in reviewed[0]['error']
    archived = read(cache / 'failed-attempts' / (reviewed[0]['key'] + '-response.json'))
    assert archived['status'] == 'failed' and archived['response'] == '' and archived['usage'] is None
    skill_path = PROTOCOL['plugin']['source_path']
    assert digest(git_blob(skill_path)) == PROTOCOL['plugin']['skill_sha256']
    assert digest((cache / 'work/sherlock-report/.agents/skills/sherlock-report/SKILL.md').read_bytes()) == PROTOCOL['plugin']['skill_sha256']
    assert state['skill_discovery']['baseline']['sherlock_available'] is False
    assert state['skill_discovery']['sherlock-report']['sherlock_available'] is True
    assert state['protocol_sha256'] == digest((ROOT / 'protocol.json').read_bytes())
    assert digest((cache / PROTOCOL['dataset']['file']).read_bytes()) == PROTOCOL['dataset']['sha256']
    serialized = (ROOT / 'results.json').read_text(encoding='utf-8')
    assert str(cache) not in serialized
    assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,})', serialized)
    audit = {'passed': True, 'verified_trials': 100, 'verified_pairs': 50, 'questions': 10,
             'model': PROTOCOL['solver']['model'], 'effort': PROTOCOL['solver']['effort'],
             'actual_model_and_effort_verified_from_100_thread_start_records': True,
             'tools_observed': 0, 'unexpected_instruction_sources': 0,
             'registered_inference_sources_unchanged': True, 'registered_metric_functions_unchanged': True,
             'reviewed_quota_rejections': 1, 'completed_answers_regenerated': 0, 'full_native_skill_bytes_verified': True,
             'baseline_sherlock_unavailable': True, 'independent_rescore_matches': True,
             'token_accounting_consistent': True, 'completed_records_match_saved_responses': True,
             'registration_commit': registered, 'codex_version': state['codex_version'],
             'codex_binary_sha256': digest(CODEX.read_bytes()),
             'python_version': platform.python_version(), 'platform': platform.system(),
             'correct': dict(expected_scores),
             'limitation': 'This audit verifies recorded execution and accounting, not model-internal compliance, unseen weights, training contamination, or reasoning quality.'}
    write(ROOT / 'audit.json', audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
