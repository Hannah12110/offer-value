"""Cash scenarios. Unknowns stay null; policies must be supplied explicitly."""
from datetime import date
from urllib.parse import urlparse
from common import number,cli,currency_code


def annual_tax(taxable):
    number(taxable,'taxable')
    for limit,rate,deduction in [(36000,.03,0),(144000,.10,2520),(300000,.20,16920),(420000,.25,31920),(660000,.30,52920),(960000,.35,85920),(float('inf'),.45,181920)]:
        if taxable<=limit:return max(0,taxable*rate-deduction)


def calculate(d):
    if not isinstance(d,dict):raise ValueError('input must be an object')
    currency=currency_code(d.get('currency'))
    if not isinstance(currency,str) or len(currency)!=3 or not currency.isalpha() or currency!=currency.upper():raise ValueError('currency must be uppercase ISO code')
    # No implicit FX, bonus, contribution, hours or living-cost defaults.
    fields=('fixed_monthly','guaranteed_months','guaranteed_allowance_annual','target_variable_annual','monthly_employee_contributions','annual_additional_deduction','annual_net_override','actual_hours_week','commute_hours_week','relocation_cost','refundable_deposit')
    for k in fields:
        if d.get(k) is not None:number(d[k],k)
    if d.get('guaranteed_months') is not None and not 1<=d['guaranteed_months']<=24:raise ValueError('guaranteed_months must be 1..24')
    if d.get('actual_hours_week') is not None and not 0<d['actual_hours_week']<=168:raise ValueError('hours must be 0..168')
    if d.get('actual_hours_week') and d.get('commute_hours_week') is not None and d['actual_hours_week']+d['commute_hours_week']>168:raise ValueError('work+commute exceeds week')
    for k in ('budget_currency','contribution_currency'):
        if d.get(k,currency)!=currency:raise ValueError('mixed currencies; convert explicitly with source first')
    budgets=d.get('monthly_budgets',{})
    if not isinstance(budgets,dict) or set(budgets)-{'conservative','baseline','comfortable'}:raise ValueError('invalid budget scenarios')
    for k,v in budgets.items():
        if v is not None:number(v,k)
    fixed_base=d['fixed_monthly']*d['guaranteed_months'] if d.get('fixed_monthly') is not None and d.get('guaranteed_months') is not None else None
    gross=None
    if all(d.get(k) is not None for k in ('fixed_monthly','guaranteed_months','guaranteed_allowance_annual')):
        gross=d['fixed_monthly']*d['guaranteed_months']+d['guaranteed_allowance_annual']
    target=gross+d['target_variable_annual'] if gross is not None and d.get('target_variable_annual') is not None else None
    tax_model=d.get('tax_model','generic')
    if tax_model not in {'generic','CN_resident_annual'}:raise ValueError('unsupported tax model')
    if tax_model=='CN_resident_annual':
        policy=d.get('tax_policy',{})
        if currency!='CNY' or not policy.get('source_url') or not policy.get('as_of'):raise ValueError('CNY and dated tax source required')
        u=urlparse(policy['source_url'])
        if u.scheme not in {'http','https'} or not u.netloc:raise ValueError('invalid policy URL')
        if date.fromisoformat(policy['as_of'])>date.today():raise ValueError('future policy date')
        allowance=number(policy.get('annual_basic_deduction'),'annual_basic_deduction')
    def net(g):
        if g is None:return None
        if tax_model=='generic':return None
        if d.get('monthly_employee_contributions') is None or d.get('annual_additional_deduction') is None:return None
        contributions=d['monthly_employee_contributions']*12
        if contributions>g:raise ValueError('employee contributions exceed income')
        tax=annual_tax(max(0,g-contributions-allowance-d['annual_additional_deduction']))
        return g-contributions-tax
    guaranteed_net=net(gross);target_net=net(target)
    if tax_model=='generic':
        guaranteed_net=d.get('annual_net_override')
        if guaranteed_net is not None and gross is not None and guaranteed_net>gross:raise ValueError('guaranteed net override exceeds guaranteed gross')
    scenarios={}
    for name,cost in budgets.items():
        items={}
        for label,n in [('guaranteed',guaranteed_net),('target',target_net)]:
            recurring=n-cost*12 if n is not None and cost is not None else None
            relocation=d.get('relocation_cost')
            first=recurring-relocation if recurring is not None and relocation is not None else None
            hours=d.get('actual_hours_week');commute=d.get('commute_hours_week')
            items[label]={'monthly_average_net':round(n/12,2) if n is not None else None,'monthly_recurring_savings':round(recurring/12,2) if recurring is not None else None,'annual_savings_first_year':round(first,2) if first is not None else None,'savings_2y':round(recurring*2-relocation,2) if first is not None else None,'savings_3y':round(recurring*3-relocation,2) if first is not None else None,'net_hourly':round(n/(hours*52),2) if n is not None and hours else None,'net_hourly_including_commute':round(n/((hours+commute)*52),2) if n is not None and hours and commute is not None else None}
        scenarios[name]=items
    missing=[k for k in ('fixed_monthly','guaranteed_months','guaranteed_allowance_annual','target_variable_annual','relocation_cost') if d.get(k) is None]
    return {'currency':currency,'known_fixed_gross_annual':fixed_base,'guaranteed_gross_lower_bound':gross if gross is not None else fixed_base,'guaranteed_gross_annual':gross,'target_gross_annual':target,'guaranteed_net_annual':round(guaranteed_net,2) if guaranteed_net is not None else None,'target_net_annual':round(target_net,2) if target_net is not None else None,'refundable_deposit_cash_locked':d.get('refundable_deposit'),'scenarios':scenarios,'unknown_fields':missing,'assumptions':d.get('assumptions',[]),'limitations':['年度居民综合所得估计，全年一致工资/连续就业；月均并非每月到账。','奖金并入年度综合所得；不支持股权税、跨境税、非居民或奖金单独计税。','公积金账户与可退押金不当自由现金；累计储蓄不含涨薪、通胀、投资收益。','政策有效性及扣款数由操作者核实；公式精度不代表输入可靠性。']}
if __name__=='__main__':cli(calculate)
