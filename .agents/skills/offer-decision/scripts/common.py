"""Strict JSON and numeric helpers, no network."""
import argparse
import json
import math
from pathlib import Path


def number(v, name, minimum=0, maximum=None):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f'{name}: finite number required')
    if v<minimum or (maximum is not None and v>maximum): raise ValueError(f'{name}: out of range')
    return float(v)


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(d): return json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)


def cli(fn):
    p=argparse.ArgumentParser(description=fn.__doc__);p.add_argument('input');a=p.parse_args()
    try: print(dump(fn(read(a.input))))
    except (ValueError,KeyError,TypeError,OSError) as e: p.exit(2,f'Invalid input: {e}\n')

SUPPORTED_CURRENCIES={'CNY','USD','EUR','GBP','HKD','JPY','SGD','AUD','CAD','CHF','NZD','INR','KRW','TWD'}

def currency_code(value):
    if not isinstance(value,str) or value not in SUPPORTED_CURRENCIES:
        raise ValueError('unsupported currency; use a documented ISO code or convert explicitly')
    return value

PLAIN_DECISION={'ACCEPT':'可以签','CONDITIONAL_ACCEPT':'可以有条件地签','NEGOTIATE':'继续谈薪，暂不签','HOLD':'先别签，先谈条件','DECLINE':'建议放弃'}
PLAIN_STATUS={'SUFFICIENT_EVIDENCE':'证据充分','INSUFFICIENT_EVIDENCE':'证据不足'}
PLAIN_BLOCKER={'entity':'签约主体','salary':'书面薪资','duties':'岗位职责','legal_safety':'诉讼与处罚','constraints':'个人取舍'}
PLAIN_BLOCKER_STATUS={'clear':'已确认','unknown':'未知','blocked':'受阻'}


PLAIN_EVIDENCE_TYPE={'A':'监管/政府/统计','B':'企业自报','C':'独立研究/媒体','D':'员工匿名','E':'模型推断','USER':'用户自报'}
PLAIN_VERIFY={'verified':'已核实','self_reported':'企业自报','unverified':'未核实','conflicted':'存在冲突'}
PLAIN_CRED={'high':'高','medium':'中','low':'低','unknown':'未知'}
PLAIN_FRESH={'current':'当前','stale':'已过期','unknown':'未知'}


def plain_decision(value):
    """Reader-facing sentence; internal enum stays available for scripts."""
    if value not in PLAIN_DECISION: raise ValueError(f'unknown decision: {value}')
    return PLAIN_DECISION[value]
