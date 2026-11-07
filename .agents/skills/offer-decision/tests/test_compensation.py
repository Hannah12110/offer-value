import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from calculate_compensation import calculate,annual_tax


def sample():
    return dict(currency='CNY',fixed_monthly=10000,guaranteed_months=12,guaranteed_allowance_annual=0,target_variable_annual=20000,tax_model='CN_resident_annual',tax_policy={'source_url':'https://www.chinatax.gov.cn/policy','as_of':'2026-11-06','annual_basic_deduction':60000},monthly_employee_contributions=1000,annual_additional_deduction=0,actual_hours_week=40,commute_hours_week=5,relocation_cost=3000,refundable_deposit=2000,monthly_budgets={'baseline':4000})


class Compensation(unittest.TestCase):
    def test_unknown(self):
        r=calculate({'currency':'CNY'});self.assertIsNone(r['guaranteed_gross_annual']);self.assertIsNone(r['guaranteed_net_annual'])
    def test_separation(self):
        d=sample();r=calculate(d);self.assertEqual(r['guaranteed_gross_annual'],120000);self.assertEqual(r['target_gross_annual'],140000)
    def test_tax_savings(self):
        r=calculate(sample());self.assertEqual(r['guaranteed_net_annual'],105720);self.assertEqual(r['scenarios']['baseline']['guaranteed']['annual_savings_first_year'],54720);self.assertEqual(r['scenarios']['baseline']['guaranteed']['savings_2y'],112440)
    def test_unknown_bonus(self):
        d=sample();d['target_variable_annual']=None;r=calculate(d);self.assertIsNone(r['target_gross_annual']);self.assertEqual(r['guaranteed_gross_annual'],120000)
    def test_unknown_contributions(self):
        d=sample();d['monthly_employee_contributions']=None;self.assertIsNone(calculate(d)['guaranteed_net_annual'])
    def test_foreign_no_chinese_tax(self):
        d=sample();d['currency']='USD'
        with self.assertRaises(ValueError):calculate(d)
    def test_mixed_currency(self):
        d=sample();d['budget_currency']='USD'
        with self.assertRaises(ValueError):calculate(d)
    def test_generic_foreign(self):
        r=calculate({'currency':'USD','annual_net_override':50000,'monthly_budgets':{'baseline':2000},'relocation_cost':0});self.assertEqual(r['scenarios']['baseline']['guaranteed']['annual_savings_first_year'],26000)
    def test_invalid_values(self):
        for k,v in [('fixed_monthly',-10),('actual_hours_week',0),('guaranteed_months',0),('target_variable_annual',float('inf'))]:
            d=sample();d[k]=v
            with self.assertRaises(ValueError):calculate(d)
    def test_zero_unknown_distinct(self):
        d=sample();d['target_variable_annual']=0;self.assertEqual(calculate(d)['target_gross_annual'],120000)
    def test_tax_boundaries(self):
        for t,expected in [(0,0),(36000,1080),(144000,11880),(300000,43080),(420000,73080),(660000,145080),(960000,250080)]:self.assertAlmostEqual(annual_tax(t),expected)
    def test_unverified_policy(self):
        d=sample();d.pop('tax_policy')
        with self.assertRaises(ValueError):calculate(d)

    def test_fake_iso_rejected(self):
        with self.assertRaises(ValueError):calculate({'currency':'ZZZ'})
    def test_override_above_gross(self):
        d=sample();d.update(tax_model='generic',annual_net_override=200000)
        with self.assertRaises(ValueError):calculate(d)
    def test_unknown_allowance_keeps_known_floor(self):
        d=sample();d['guaranteed_allowance_annual']=None;r=calculate(d)
        self.assertEqual(r['known_fixed_gross_annual'],120000);self.assertEqual(r['guaranteed_gross_lower_bound'],120000);self.assertIsNone(r['guaranteed_gross_annual'])
