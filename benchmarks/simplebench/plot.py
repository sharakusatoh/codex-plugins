"""Regenerate the standalone comparison figure from published results.json."""
from pathlib import Path
import json, os, sys
ROOT = Path(__file__).resolve().parent
local_deps = ROOT.parents[2] / 'plugin-benchmark/chart-deps'
if local_deps.is_dir():
    sys.path.insert(0, str(local_deps))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    data = json.loads((ROOT / 'results.json').read_text(encoding='utf-8'))
    if data['completed_answers'] != 100:
        raise RuntimeError('Plot final comparisons only after all 100 planned answers finish')
    colors = ['#507899', '#B65C3A']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                         'axes.spines.right': False, 'svg.hashsalt': 'simplebench-public-v1'})
    fig, (a, b) = plt.subplots(1, 2, figsize=(12.8, 5.4), gridspec_kw={'width_ratios': [1, 2]})
    fig.patch.set_facecolor('#FBFAF6')
    for ax in (a, b):
        ax.set_facecolor('#FBFAF6')
        ax.set_axisbelow(True)
        ax.grid(axis='y', alpha=.15)
    labels = ['No plugin', 'Sherlock Report']
    rates = [data['summary'][c]['accuracy_pct'] for c in ('baseline', 'sherlock-report')]
    a.bar(labels, rates, color=colors, width=.58)
    a.set_ylim(0, 110)
    a.set_yticks(range(0, 101, 20))
    a.set_ylabel('Correct responses (%)')
    a.set_title('All 50 responses per condition', loc='left', fontsize=12, pad=18)
    for index, c in enumerate(('baseline', 'sherlock-report')):
        s = data['summary'][c]
        a.text(index, rates[index] + 2, f"{rates[index]:.1f}%\n{s['correct']}/50", ha='center', va='bottom', fontsize=11)
    ids = [r['question_id'] for r in data['by_question']]
    for offset, c, color, label in zip((-.19, .19), ('baseline', 'sherlock-report'), colors, labels):
        b.bar([x + offset for x in ids], [r[c]['correct'] for r in data['by_question']], .36, label=label, color=color)
    b.set_xticks(ids)
    b.set_ylim(0, 6.1)
    b.set_yticks(range(6))
    b.set_xlabel('Official public question ID')
    b.set_ylabel('Correct out of 5 repeats')
    b.set_title('Question coverage: 10 public items', loc='left', fontsize=12, pad=18)
    b.legend(loc='upper center', ncol=2, frameon=False, fontsize=10)
    fig.suptitle('SimpleBench public sample: paired comparison', x=.055, ha='left', fontsize=19, fontweight='bold', y=.97)
    diff = data['comparison']['difference_percentage_points']
    fig.text(.055, .865, f'GPT-6 Astra | medium reasoning | tools disabled | Sherlock minus no plugin: {diff:+.1f} pp', fontsize=11, color='#555555')
    fig.text(.055, .035, 'Exploratory public-sample evaluation, not an official leaderboard score. Five repeats do not add new questions.', fontsize=10, color='#555555')
    fig.subplots_adjust(left=.065, right=.98, top=.74, bottom=.19, wspace=.32)
    fig.savefig(ROOT / 'comparison.svg', facecolor=fig.get_facecolor(), metadata={'Date': None})
    fig.savefig(ROOT / 'comparison.png', facecolor=fig.get_facecolor(), dpi=170)
    svg = ROOT / 'comparison.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8', newline='\n')
    print('Wrote comparison.svg and comparison.png')


if __name__ == '__main__':
    main()
