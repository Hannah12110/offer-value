"""Dependency-free package check for this skill's deliberately small YAML subset.
Not a replacement for Codex runtime discovery or a general YAML parser.
"""
import argparse
import ast
import json
import re
from pathlib import Path


def check(root):
    root=Path(root);errors=[];text=(root/'SKILL.md').read_text()
    if not text.startswith('---\n'):errors.append('missing YAML frontmatter')
    blocks=text.split('---',2)
    if len(blocks)!=3:return {'valid':False,'errors':['frontmatter fence incomplete']}
    fields={}
    for line in blocks[1].strip().splitlines():
        key,sep,value=line.partition(':')
        if not sep:errors.append('invalid YAML subset line');continue
        try:fields[key]=ast.literal_eval(value.strip()) if value.strip().startswith(('"',"'")) else value.strip()
        except (SyntaxError,ValueError):errors.append('invalid quoted scalar')
    if fields.get('name')!='offer-decision':errors.append('name mismatch')
    if not isinstance(fields.get('description'),str) or not fields['description'].strip():errors.append('description missing')
    if re.search(r'\bTODO\b|\[INSERT|\[TODO',text):errors.append('unfinished placeholder')
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if '://' not in link and not (root/link).exists():errors.append(f'broken reference: {link}')
    ui=(root/'agents/openai.yaml').read_text()
    for key in ('display_name','short_description','default_prompt'):
        match=re.search(rf'^  {key}: (".*")$',ui,re.M)
        if not match:errors.append(f'UI quoted string missing: {key}')
        else:
            try:ast.literal_eval(match[1])
            except (ValueError,SyntaxError):errors.append(f'UI invalid scalar: {key}')
    if '$offer-decision' not in ui:errors.append('default_prompt missing invocation')
    if 'allow_implicit_invocation: true' not in ui:errors.append('implicit invocation missing')
    for name in ('score_offer.py','calculate_compensation.py','validate_evidence.py','render_report.py','run_offer.py'):
        path=root/'scripts'/name
        if not path.is_file():errors.append(f'missing script: {name}')
        else:
            try:ast.parse(path.read_text())
            except SyntaxError as e:errors.append(str(e))
    for path in (root/'assets').glob('*.json'):
        try:json.loads(path.read_text())
        except ValueError as e:errors.append(str(e))
    return {'valid':not errors,'errors':errors,'scope':'restricted YAML scalars, local links, JSON, Python syntax; not Codex runtime discovery'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory');a=p.parse_args()
    try:
        result=check(a.directory);print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['valid'] else 2)
    except (OSError,ValueError) as e:p.exit(2,str(e)+'\n')
