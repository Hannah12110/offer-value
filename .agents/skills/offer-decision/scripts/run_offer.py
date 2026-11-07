"""Minimal/offline intake. Produces a research skeleton, never claims online research."""
import argparse
from datetime import date
from pathlib import Path
from common import read,dump
from score_offer import WEIGHTS,BLOCKERS,sensitivity
from calculate_compensation import calculate
from render_report import render


def prepare(d):
    if not isinstance(d,dict):raise ValueError('input must be an object')
    offer=d.get('offer',d)
    for k in ('company','role','city'):
        if not isinstance(offer.get(k),str) or not offer[k].strip():raise ValueError(f'{k} required')
    assessment={'research_as_of':date.today().isoformat(),'rubric_version':1,'mode':d.get('mode','A'),'stage':offer.get('stage','pre_salary'),'weights':dict(WEIGHTS),'dimensions':{},'evidence':[],'blockers':{k:{'status':'unknown'} for k in BLOCKERS},'salary_guaranteed_known':False}
    comp=dict(offer.get('compensation') or {});comp.setdefault('currency','CNY')
    return {'offer':offer,'profile':d.get('profile',{}),'assessment':assessment,'compensation':comp,'module_status':{k:'offline' for k in ['industry','role','company','location','capital','compensation','risks','decision']},'sections':{'Executive Decision':'[UNKNOWN] 最小输入/离线待研究报告；未开展在线尽调。请优先确认合同主体、薪资保底、实际职责、个人目标及强约束。'}}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('--out',required=True);a=p.parse_args()
    try:
        d=prepare(read(a.input));pout=Path(a.out)
        # Validate all computations before creating files; never overwrite a prior run.
        s=sensitivity(d['assessment']);c=calculate(d['compensation']);text=render(d)
        pout.mkdir(parents=True,exist_ok=False)
        for name,data in [('bundle',d),('assessment',d['assessment']),('compensation',d['compensation']),('evidence',[]),('score-result',s),('compensation-result',c)]:
            (pout/(name+'.json')).write_text(dump(data)+'\n',encoding='utf-8')
        (pout/'report.md').write_text(text,encoding='utf-8')
        print(str(pout.resolve()))
    except (ValueError,KeyError,TypeError,OSError) as e:p.exit(2,f'Invalid input: {e}\n')
