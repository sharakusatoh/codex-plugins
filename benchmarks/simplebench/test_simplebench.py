"""Tests use synthetic questions and a fake transport; no model calls."""
import json, tempfile, unittest
from pathlib import Path
from simplebench import score, schedule, infer
from report import paired_interval, summarize


class FakeServer:
    request_id = 0
    def call(self, method, params):
        self.start_params = params
        return {'model': 'gpt-6-astra', 'thread': {'id': 'synthetic-thread'}}
    def send(self, message):
        self.request = message
        self.events = iter([
            {'method': 'thread/tokenUsage/updated', 'params': {'threadId': 'synthetic-thread', 'tokenUsage': {'total': {'inputTokens': 10, 'outputTokens': 2, 'totalTokens': 12}}}},
            {'method': 'item/completed', 'params': {'threadId': 'synthetic-thread', 'item': {'type': 'reasoning', 'text': 'hidden content must never be retained'}}},
            {'method': 'item/completed', 'params': {'threadId': 'synthetic-thread', 'item': {'type': 'agentMessage', 'phase': 'final_answer', 'text': 'Final Answer: A'}}},
            {'method': 'turn/completed', 'params': {'threadId': 'synthetic-thread', 'turn': {'status': 'completed'}}},
        ])
    def receive(self, seconds):
        return next(self.events)


class BenchmarkTests(unittest.TestCase):
    def test_official_extractor_and_failures(self):
        self.assertTrue(score('Explanation.\nFinal Answer: c', 'C')['correct'])
        self.assertFalse(score('I choose C', 'C')['correct'])
        self.assertIsNone(score('I choose C', 'C')['selected_answer'])
        self.assertFalse(score('Final Answer: B', 'C')['correct'])
        result = score('Final Answer: B\nFinal Answer: C', 'B')
        self.assertTrue(result['correct'])
        self.assertTrue(result['format_issue'])
        self.assertEqual(result['answer_marker_count'], 2)

    def test_full_balanced_schedule(self):
        items = schedule()
        self.assertEqual(items, schedule())
        self.assertEqual(len(items), 100)
        self.assertEqual(len({i['key'] for i in items}), 100)
        self.assertEqual(sum(i['condition'] == 'baseline' for i in items[::2]), 25)
        for index in range(0, 100, 2):
            a, b = items[index:index + 2]
            self.assertEqual((a['question_id'], a['repeat']), (b['question_id'], b['repeat']))
            self.assertNotEqual(a['condition'], b['condition'])
        for qid in range(1, 11):
            for condition in ('baseline', 'sherlock-report'):
                self.assertEqual(sum(i['question_id'] == qid and i['condition'] == condition for i in items), 5)

    def test_solver_never_receives_key_or_hidden_reasoning(self):
        with tempfile.TemporaryDirectory() as folder:
            server = FakeServer()
            item = {'condition': 'baseline', 'key': 'synthetic', 'repeat': 1, 'question_id': 987, 'sequence': 1}
            result = infer(server, Path(folder), item, {'prompt': 'Synthetic question with options.', 'answer': 'SECRET-KEY-CANARY'})
            sent = json.dumps(server.request)
            self.assertNotIn('SECRET-KEY-CANARY', sent)
            self.assertNotIn('987', sent)
            self.assertNotIn('hidden content', json.dumps(result))
            self.assertEqual(result['response'], 'Final Answer: A')
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(server.request['params']['input'], [{'type': 'text', 'text': 'Synthetic question with options.'}])

    def test_sherlock_receives_native_skill_and_marker(self):
        with tempfile.TemporaryDirectory() as folder:
            server = FakeServer()
            item = {'condition': 'sherlock-report', 'key': 'synthetic', 'repeat': 1, 'question_id': 987, 'sequence': 1}
            infer(server, Path(folder), item, {'prompt': 'Question.', 'answer': 'B'})
            inputs = server.request['params']['input']
            self.assertEqual(inputs[0]['type'], 'skill')
            self.assertEqual(inputs[0]['name'], 'sherlock-report')
            self.assertEqual(inputs[1]['text'], '$sherlock-report\nQuestion.')

    def test_summary_clusters_questions_and_keeps_negative_effect(self):
        rows = []
        for item in schedule():
            rows.append({**item, 'status': 'completed', 'correct': item['condition'] == 'baseline',
                         'selected_answer': 'A', 'format_issue': False, 'seconds': 1, 'usage': {}})
        summary, questions, comparison, repeats = summarize(rows)
        self.assertEqual(summary['baseline']['correct'], 50)
        self.assertEqual(summary['sherlock-report']['correct'], 0)
        self.assertEqual(comparison['difference_percentage_points'], -100)
        self.assertEqual(comparison['paired_question_bootstrap_95pct_pp'], [-100, -100])
        self.assertEqual(comparison['baseline_only'], 50)
        self.assertEqual(comparison['question_clusters'], 10)
        self.assertEqual(len(repeats), 5)
        rows.pop()
        self.assertIsNone(summarize(rows)[2]['difference_percentage_points'])

    def test_bootstrap_reproducible_and_paired(self):
        self.assertEqual(paired_interval([0] * 10), [0, 0])
        values = [0, .2, -.4, .8, .2, .2, -.2, 0, 0, -.2]
        self.assertEqual(paired_interval(values), paired_interval(values))


if __name__ == '__main__':
    unittest.main()
