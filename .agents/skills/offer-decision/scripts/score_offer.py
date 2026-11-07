"""Interval scoring with evidence coverage and decision rules."""
import argparse
from datetime import date
from copy import deepcopy
from collections import Counter
from common import number,read,dump,currency_code
from validate_evidence import validate,qualified
WEIGHTS=dict(industry=10,role=20,company=15,capital=20,fit=15,economics=10,location=5,conditions=5)
BLOCKERS=('entity','salary','duties','legal_safety','constraints')


def weights_valid(w):
    if set(w)!=set(WEIGHTS):raise ValueError('exactly eight weight keys required')
    for k,v in w.items():number(v,k,0,100)
    if abs(sum(w.values())-100)>1e-8:raise ValueError('weights must sum to 100')


def bounds(v):
    if v is None:return [0.,10.]
    if isinstance(v,list):
        if len(v)!=2:raise ValueError('interval needs two bounds')
        a,b=[number(x,'score',0,10) for x in v]
        if a>b:raise ValueError('reversed interval')
        return [a,b]
    v=number(v,'score',0,10);return [v,v]


def blocker_evidence(e, key, status):
    # A goal statement cannot attest employer identity, salary, duties or legal safety.
    if e.get('related_dimension')!=key:return False
    if e.get('conflicts_with') or e.get('supports_or_conflicts')!='supports' or e.get('claim_kind','FACT')!='FACT' or e.get('freshness')!='current':return False
    if key=='constraints' and e.get('evidence_type')=='USER':
        return e.get('verification_status')=='self_reported'
    return e.get('verification_status')=='verified' and e.get('evidence_type') not in {'D','E','USER'} and e.get('credibility') in {'high','medium'}


def score(data):
    if not isinstance(data,dict):raise ValueError('input must be an object')
    if data.get('rubric_version',1)!=1:raise ValueError('unsupported rubric')
    if data.get('mode','A') not in {'A','B','C'}:raise ValueError('invalid mode')
    if data.get('stage','pre_salary') not in {'confirmed','verbal','pre_salary','interview'}:raise ValueError('invalid stage')
    w=data.get('weights',WEIGHTS);weights_valid(w)
    ledger=data.get('evidence',[]);v=validate(ledger)
    if not v['valid']:raise ValueError('; '.join(v['errors']))
    evidence={e['evidence_id']:e for e in ledger};dims=data.get('dimensions',{})
    conflict_ids={e['evidence_id'] for e in ledger if e.get('conflicts_with')} | {ref for e in ledger for ref in e.get('conflicts_with',[])}
    if set(dims)-set(WEIGHTS):raise ValueError('unknown dimension')
    low=high=coverage=known=0.;detail={};referenced=set()
    for k in WEIGHTS:
        rows=dims.get(k,[{'id':str(i),'score':None,'evidence_ids':[],'rationale':'UNKNOWN'} for i in range(3)])
        if not isinstance(rows,list) or len(rows)!=3:raise ValueError(f'{k}: exactly three subindicators')
        if len({r.get('id') for r in rows})!=3 or any(not r.get('id') for r in rows):raise ValueError('unique indicator IDs required')
        intervals=[];n=0;known_sum=0.;items=[]
        for r in rows:
            b=bounds(r.get('score'));refs=r.get('evidence_ids',[])
            if not isinstance(refs,list) or any(x not in evidence for x in refs):raise ValueError('dangling evidence reference')
            referenced.update(refs)
            if r.get('score') is not None and not str(r.get('rationale','')).strip():raise ValueError('rationale required')
            usable=r.get('score') is not None and any(x not in conflict_ids and evidence[x].get('related_dimension')==k and qualified(evidence[x],k) for x in refs)
            if usable:n+=1;known_sum+=sum(b)/2
            else:b=[0.,10.]
            intervals.append(b);items.append(dict(r,effective_interval=b,covered=bool(usable)))
        b=[sum(x[j] for x in intervals)/3 for j in (0,1)];cov=n/3
        low+=w[k]*b[0]/10;high+=w[k]*b[1]/10;coverage+=w[k]/100*cov;known+=w[k]/100*known_sum/3
        detail[k]={'interval':b,'coverage':cov,'weight':w[k],'subindicators':items}
    blocks=data.get('blockers',{})
    if set(blocks)-set(BLOCKERS):raise ValueError('unknown blocker key')
    blocked=[];unresolved=[]
    for k in BLOCKERS:
        item=blocks.get(k,{'status':'unknown'});status=item.get('status','unknown');refs=item.get('evidence_ids',[])
        if status not in {'clear','unknown','blocked'}:raise ValueError('invalid blocker status')
        if not isinstance(refs,list) or any(x not in evidence for x in refs):raise ValueError('invalid blocker evidence')
        if status in {'clear','blocked'}:
            if not refs or not item.get('reason'):raise ValueError('blocker needs evidence/reason')
            if not any(x not in conflict_ids and blocker_evidence(evidence[x],k,status) for x in refs):status='unknown'
        if status=='blocked':blocked.append(k)
        if status=='unknown':unresolved.append(k)
    enough=coverage>=.8-1e-9 and all(detail[k]['coverage']>=2/3 for k in ('company','role','capital','fit')) and not unresolved and data.get('salary_guaranteed_known') is True
    if blocked:decision='DECLINE'
    elif not enough:decision='NEGOTIATE' if data.get('mode')=='C' else 'HOLD'
    elif high<50:decision='DECLINE'
    elif low>=75:decision='ACCEPT' if data.get('stage')=='confirmed' else 'HOLD'
    elif low>=65:decision='CONDITIONAL_ACCEPT' if data.get('stage')=='confirmed' else 'HOLD'
    else:decision='HOLD'
    if enough and data.get('negotiate') is True and decision!='DECLINE':decision='NEGOTIATE'
    return {'decision':decision,'evidence_status':'SUFFICIENT_EVIDENCE' if enough else 'INSUFFICIENT_EVIDENCE','coverage':round(coverage,6),'score_interval':[round(low,4),round(high,4)],'score':round(low,4) if coverage>=1-1e-9 and abs(low-high)<1e-8 else None,'known_weighted_score':round(known/coverage*10,4) if coverage else None,'known_score_label':'非完整总分（已覆盖子项的区间中点）','credibility_counts':dict(Counter(evidence[x]['credibility'] for x in sorted(referenced))),'blocked':blocked,'unresolved_blockers':unresolved,'dimensions':detail}


def sensitivity(data):
    base=score(data);variants=[];w=data.get('weights',WEIGHTS)
    for k in ('role','economics'):
        for shift in (-5,5):
            new=w[k]+shift
            if not 0<=new<=100 or w[k]==100:continue
            d=deepcopy(data);d['weights']={j:(new if j==k else v*(100-new)/(100-w[k])) for j,v in w.items()};r=score(d)
            variants.append({'variable':f'{k} weight {shift:+}','decision':r['decision'],'score_interval':r['score_interval']})
    for k,dim in base['dimensions'].items():
        if dim['interval'][0]==dim['interval'][1]:continue
        for side in (0,1):
            d=deepcopy(data)
            for row in d.get('dimensions',{}).get(k,[]):
                if isinstance(row.get('score'),list): row['score']=row['score'][side]
            actual=score(d)
            lo,hi=actual['score_interval'];old=actual['dimensions'][k]['interval'];value=old[side]
            interval=[lo-w[k]*old[0]/10+w[k]*value/10,hi-w[k]*old[1]/10+w[k]*value/10]
            variants.append({'variable':f'{k} assumed {side}','score_interval':[round(x,4) for x in interval],
                             'decision':actual['decision'],'note':'已覆盖区间取边界并重算建议；未知项只显示假设边界，证据门槛不解除'})
    return {'base':base,'variants':variants,'decision_changes':any(v['decision']!=base['decision'] for v in variants)}


def compare(data):
    if not isinstance(data,dict):raise ValueError('input must be an object')
    offers=data['offers']
    if len(offers)<2:raise ValueError('at least two offers')
    if len({o.get('id') for o in offers})!=len(offers) or any(not o.get('id') for o in offers):raise ValueError('unique offer IDs required')
    first=offers[0]
    cutoff=first.get('research_as_of')
    if not cutoff:raise ValueError('comparison needs research_as_of for each offer')
    if date.fromisoformat(cutoff)>date.today():raise ValueError('future research cutoff')
    if any(o.get('research_as_of')!=cutoff for o in offers):raise ValueError('comparison research cutoff mismatch')
    for o in offers:
        if o.get('currency') is not None:currency_code(o['currency'])
    for o in offers:
        if o.get('weights',WEIGHTS)!=first.get('weights',WEIGHTS) or o.get('rubric_version',1)!=first.get('rubric_version',1):raise ValueError('comparison framework/weights mismatch')
        for k in WEIGHTS:
            if [r['id'] for r in o.get('dimensions',{}).get(k,[])]!=[r['id'] for r in first.get('dimensions',{}).get(k,[])]:raise ValueError('comparison subindicators mismatch')
    results={o['id']:score(o) for o in offers};dominant=[]
    for k,r in results.items():
        if r['evidence_status']=='SUFFICIENT_EVIDENCE' and r['decision']!='DECLINE' and all(j==k or (s['evidence_status']=='SUFFICIENT_EVIDENCE' and r['score_interval'][0]>s['score_interval'][1]) for j,s in results.items()):dominant.append(k)
    currencies={o.get('currency') for o in offers}
    if len(currencies)!=1 or None in currencies: dominant=[]
    return {'results':results,'robust_leader':dominant[0] if len(dominant)==1 else None,'economics_comparable':len(currencies)==1 and None not in currencies,'note':'区间重叠或证据不足不强排名；经济金额跨币种需先有来源的换汇'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('--compare',action='store_true');p.add_argument('--sensitivity',action='store_true');a=p.parse_args()
    try:print(dump((compare if a.compare else sensitivity if a.sensitivity else score)(read(a.input))))
    except (ValueError,KeyError,TypeError,OSError) as e:p.exit(2,f'Invalid input: {e}\n')
