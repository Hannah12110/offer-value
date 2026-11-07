import unittest
import tempfile
import subprocess
import json
from pathlib import Path
from test_scoring import full
from run_offer import prepare
from render_report import render,HEADINGS
ROOT=Path(__file__).resolve().parents[1]

class Workflow(unittest.TestCase):
    def test_minimum_offline(self):
        d=prepare({'company':'某同名企业','role':'PM','city':'上海'});r=render(d)
        self.assertEqual(len([h for h in HEADINGS if h in r]),14);self.assertEqual(d['assessment']['blockers']['entity']['status'],'unknown');self.assertIn('HOLD',r)
    def test_missing_city(self):
        with self.assertRaises(ValueError):prepare({'company':'A','role':'R'})
    def test_different_city_no_default_profile(self):
        a=prepare({'company':'A','role':'R','city':'深圳'});b=prepare({'company':'A','role':'R','city':'成都'});self.assertEqual(a['profile'],{});self.assertEqual(a['compensation'],b['compensation'])
    def test_cli_end_to_end_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);source=path/'input.json';source.write_text(json.dumps({'company':'A','role':'R','city':'S'}));cmd=[__import__('sys').executable,str(ROOT/'scripts/run_offer.py'),str(source),'--out',str(path/'result')]
            first=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(first.returncode,0,first.stderr);self.assertTrue((path/'result/report.md').is_file());self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
    def test_partial_sections_not_fabricated(self):
        d=prepare({'company':'A','role':'R','city':'S'});self.assertIn('[UNKNOWN]',render(d));self.assertNotIn('ACCEPT**',render(d))

    def test_package_static(self):
        from validate_skill import check
        self.assertTrue(check(ROOT)['valid'])
    def test_calculators_cli(self):
        import sys
        commands=[('score_offer.py','assessment.example.json'),('calculate_compensation.py','compensation.example.json')]
        for script,asset in commands:
            r=subprocess.run([sys.executable,str(ROOT/'scripts'/script),str(ROOT/'assets'/asset)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr);self.assertIsInstance(json.loads(r.stdout),dict)
    def test_no_upload_client_in_scripts(self):
        import ast
        forbidden={'requests','urllib','http','socket','openai'}
        imports=[]
        for p in (ROOT/'scripts').glob('*.py'):
            for n in ast.walk(ast.parse(p.read_text())):
                if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
                if isinstance(n,ast.ImportFrom):imports.append(n.module or '')
        # urllib.parse is URL syntax only; no transport imports.
        self.assertFalse(set(imports)&forbidden);self.assertFalse(any(x.startswith(('urllib.request','http.client')) for x in imports))
