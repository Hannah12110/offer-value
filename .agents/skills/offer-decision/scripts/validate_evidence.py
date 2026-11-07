"""Validate traceability structure, not factual truth or source independence."""
from datetime import date
from urllib.parse import urlparse
from common import cli
REQUIRED={'evidence_id','claim','source_title','source_url','publisher','published_at','accessed_at','evidence_type','credibility','freshness','supports_or_conflicts','related_dimension','verification_status'}
ENUMS={'evidence_type':{'A','B','C','D','E','USER'},'credibility':{'high','medium','low','unknown'},'freshness':{'current','stale','unknown'},'supports_or_conflicts':{'supports','conflicts','context'},'verification_status':{'verified','self_reported','unverified','conflicted'},'claim_kind':{'FACT','ESTIMATE','OPINION','INFERENCE','UNKNOWN'}}


def validate(rows):
    if not isinstance(rows,list): raise ValueError('ledger must be array')
    errors=[];ids=set()
    for i,e in enumerate(rows):
        if not isinstance(e,dict): errors.append(f'{i}: object required');continue
        if REQUIRED-e.keys(): errors.append(f'{i}: missing {sorted(REQUIRED-e.keys())}')
        eid=e.get('evidence_id')
        if not isinstance(eid,str) or not eid.strip() or eid in ids: errors.append(f'{i}: duplicate/empty ID')
        else: ids.add(eid)
        for k in ('claim','source_title','publisher','related_dimension'):
            if not isinstance(e.get(k),str) or not e[k].strip(): errors.append(f'{i}: {k} required')
        for k,allowed in ENUMS.items():
            if k in e and (not isinstance(e[k],str) or e[k] not in allowed): errors.append(f'{i}: invalid {k}')
        try:
            accessed=date.fromisoformat(e['accessed_at'])
            if accessed>date.today(): errors.append(f'{i}: future access date')
            if e.get('published_at') and date.fromisoformat(e['published_at'])>accessed: errors.append(f'{i}: published after access')
        except (KeyError,ValueError,TypeError): errors.append(f'{i}: invalid date')
        u=urlparse(str(e.get('source_url','')))
        valid=(u.scheme in {'http','https'} and bool(u.netloc)) or (u.scheme in {'user','local'} and e.get('private') is True and bool(u.netloc or u.path)) or (u.scheme=='inference' and e.get('evidence_type')=='E' and bool(u.netloc))
        if not valid: errors.append(f'{i}: invalid URL/private flag')
        if not isinstance(e.get('conflicts_with',[]),list): errors.append(f'{i}: conflicts_with must be array')
    for i,e in enumerate(rows):
        if not isinstance(e,dict):continue
        refs=e.get('conflicts_with',[])
        if isinstance(refs,list):
            for ref in refs:
                if ref not in ids or ref==e.get('evidence_id'):errors.append(f'{i}: dangling/self conflict')
    return {'valid':not errors,'errors':errors,'count':len(rows),'scope':'structure only; not content verification'}


def qualified(e,dimension):
    if e.get('conflicts_with') or e.get('supports_or_conflicts')!='supports' or e.get('claim_kind','FACT')!='FACT' or e.get('freshness')!='current': return False
    if dimension=='fit' and e.get('evidence_type')=='USER': return e.get('verification_status')=='self_reported'
    return e.get('verification_status')=='verified' and e.get('evidence_type') not in {'D','E','USER'} and e.get('credibility') in {'high','medium'}


def main(rows):
    """Validate ledger, exit 2 on invalid structure."""
    r=validate(rows)
    if not r['valid']:raise ValueError('; '.join(r['errors']))
    return r
if __name__=='__main__':cli(main)
