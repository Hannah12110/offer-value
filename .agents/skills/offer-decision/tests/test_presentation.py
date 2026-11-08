import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_scoring import full
from run_offer import prepare
from render_report import render
from common import PLAIN_DECISION, PLAIN_STATUS, PLAIN_BLOCKER, PLAIN_BLOCKER_STATUS, plain_decision
from render_charts import render_charts

ROOT = Path(__file__).resolve().parents[1]
ENUMS = re.compile(r"\b(ACCEPT|CONDITIONAL_ACCEPT|NEGOTIATE|HOLD|DECLINE|SUFFICIENT_EVIDENCE|INSUFFICIENT_EVIDENCE)\b")


class Presentation(unittest.TestCase):
    def test_maps_cover_every_state(self):
        self.assertEqual(set(PLAIN_DECISION), {'ACCEPT', 'CONDITIONAL_ACCEPT', 'NEGOTIATE', 'HOLD', 'DECLINE'})
        self.assertEqual(set(PLAIN_STATUS), {'SUFFICIENT_EVIDENCE', 'INSUFFICIENT_EVIDENCE'})
        self.assertEqual(set(PLAIN_BLOCKER), {'entity', 'salary', 'duties', 'legal_safety', 'constraints'})
        self.assertEqual(set(PLAIN_BLOCKER_STATUS), {'clear', 'unknown', 'blocked'})
        self.assertEqual(plain_decision('HOLD'), '先别签，先谈条件')
        with self.assertRaises(ValueError):
            plain_decision('MAYBE')

    def test_report_leads_with_action_sentence(self):
        d = prepare({'company': 'A', 'role': 'R', 'city': 'S'})
        text = render(d)
        self.assertIn('先别签，先谈条件', text)
        self.assertIn('证据不足', text)
        self.assertIn('阈值读法', text)
        self.assertIn('待核实关口', text)
        self.assertIn('签约主体（entity）', text)
        # 内部状态保留在括号里供复核，但不得单独作为结论
        self.assertNotRegex(text, r'结论：\*\*HOLD\*\*')

    def test_charts_rendered_without_enums(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'charts'
            meta = render_charts(full(), str(out))
            self.assertEqual(meta['files'], ['chart_coverage.html', 'chart_sensitivity.html', 'chart_weight.html'])
            for name in meta['files']:
                html = (out / name).read_text(encoding='utf-8')
                self.assertIn('<svg', html)
                self.assertIn('html-box-height-mode', html)
                self.assertNotRegex(html, ENUMS)
            for name in ('chart_weight.html', 'chart_sensitivity.html'):
                self.assertIn('65', (out / name).read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            out2 = str(Path(tmp) / 'charts')
            render_charts(full(), out2)
            with self.assertRaises(ValueError):
                render_charts(full(), out2)  # 同目录二次写入必须拒绝

    def test_charts_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [sys.executable, str(ROOT / 'scripts/render_charts.py'), str(ROOT / 'assets/assessment.example.json'),
                   '--outdir', str(Path(tmp) / 'charts')]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)

    def test_presentation_reference_linked(self):
        skill = (ROOT / 'SKILL.md').read_text()
        self.assertIn('references/report-presentation.md', skill)
        self.assertIn('先别签', skill)


if __name__ == '__main__':
    unittest.main()
