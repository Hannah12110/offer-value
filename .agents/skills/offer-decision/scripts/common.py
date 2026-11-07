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
