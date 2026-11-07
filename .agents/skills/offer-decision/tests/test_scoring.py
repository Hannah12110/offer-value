import unittest
import sys
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from score_offer import score,sensitivity,compare,WEIGHTS,BLOCKERS


def evidence(eid='E1'):
    return dict(evidence_id=eid,claim='Synthetic test fixture: confirmed criteria',source_title='Test',source_url='https://example.org/test',publisher='Fixture',published_at=None,accessed_at='2026-11-06',evidence_type='A',credibility='high',freshness='current',supports_or_conflicts='supports',related_dimension='test',verification_status='verified',claim_kind='FACT')


def full(value=8):
    return dict(id='a',research_as_of='2026-11-06',rubric_version=1,stage='confirmed',salary_guaranteed_known=True,currency='CNY',evidence=[dict(evidence(),related_dimension='industry')]+[dict(evidence('D_'+k),related_dimension=k) for k in WEIGHTS if k!='industry']+[dict(evidence('B_'+k),related_dimension=k) for k in BLOCKERS],dimensions={k:[dict(id=str(i),score=value,evidence_ids=['E1' if k=='industry' else 'D_'+k],rationale='Fixture justification') for i in range(3)] for k in WEIGHTS},blockers={k:dict(status='clear',evidence_ids=['B_'+k],reason='Test verified') for k in BLOCKERS})


class Scoring(unittest.TestCase):
    def test_complete(self):
        r=score(full());self.assertEqual(r['score'],80);self.assertEqual(r['decision'],'ACCEPT')
    def test_empty(self):
        r=score({});self.assertEqual(r['score_interval'],[0,100]);self.assertIsNone(r['score']);self.assertIsNone(r['known_weighted_score']);self.assertEqual(r['decision'],'HOLD')
    def test_no_salary(self):
        d=full();d['salary_guaranteed_known']=False;self.assertEqual(score(d)['decision'],'HOLD')
    def test_verbal(self):
        d=full();d['stage']='verbal';self.assertEqual(score(d)['decision'],'HOLD')
    def test_weight_sum(self):
        d=full();d['weights']=dict(WEIGHTS,role=21)
        with self.assertRaises(ValueError):score(d)
    def test_nan_bool_negative(self):
        for x in [float('nan'),True,-1,11]:
            d=full();d['dimensions']['fit'][0]['score']=x
            with self.assertRaises(ValueError):score(d)
    def test_interval(self):
        r=score(full([6,8]));self.assertEqual(r['score_interval'],[60,80]);self.assertIsNone(r['score'])
    def test_failure_keeps_denominator(self):
        d=full();del d['dimensions']['company'];r=score(d);self.assertAlmostEqual(r['coverage'],.85);self.assertEqual(r['decision'],'HOLD')
    def test_conflict(self):
        d=full();d['evidence'].append(evidence('E2'));d['evidence'][0]['conflicts_with']=['E2'];r=score(d);self.assertAlmostEqual(r['coverage'],.9)
    def test_anonymous_not_covered(self):
        d=full();d['evidence'][0]['evidence_type']='D';self.assertAlmostEqual(score(d)['coverage'],.9)
    def test_hard_blocker_precedence(self):
        d=full();d['blockers']['constraints']['status']='blocked';self.assertEqual(score(d)['decision'],'DECLINE')
    def test_missing_blocker_evidence(self):
        d=full();d['blockers']['entity']['evidence_ids']=[]
        with self.assertRaises(ValueError):score(d)
    def test_dangling(self):
        d=full();d['dimensions']['role'][0]['evidence_ids']=['missing']
        with self.assertRaises(ValueError):score(d)
    def test_unknown_c_mode(self):
        self.assertEqual(score({'mode':'C'})['decision'],'NEGOTIATE');self.assertEqual(score({'mode':'C'})['evidence_status'],'INSUFFICIENT_EVIDENCE')
    def test_sensitivity(self):
        r=sensitivity(full([6,9]));self.assertGreaterEqual(len(r['variants']),4)
    def test_compare_dominance(self):
        a=full();b=full(6);b['id']='b';self.assertEqual(compare({'offers':[a,b]})['robust_leader'],'a')
    def test_compare_overlap(self):
        a=full([6,9]);b=full(7);b['id']='b';self.assertIsNone(compare({'offers':[a,b]})['robust_leader'])
    def test_compare_currency(self):
        a=full();b=full();b.update(id='b',currency='USD');self.assertFalse(compare({'offers':[a,b]})['economics_comparable'])
    def test_compare_mismatch(self):
        a=full();b=full();b['id']='b';b['weights']=dict(WEIGHTS,role=25,industry=5)
        with self.assertRaises(ValueError):compare({'offers':[a,b]})
    def test_omitted_indicator_rejected(self):
        d=full();d['dimensions']['capital'].pop()
        with self.assertRaises(ValueError):score(d)

    def test_goal_conflict(self):
        d=full();d['weights']=dict(industry=10,role=10,company=15,capital=15,fit=35,economics=10,location=2.5,conditions=2.5)
        for r in d['dimensions']['fit']:r['score']=1
        self.assertEqual(score(d)['decision'],'HOLD')
    def test_endpoint_changes_decision(self):
        r=sensitivity(full([6,9]));self.assertTrue(r['decision_changes'])
    def test_missing_salary_flag_even_full_scores(self):
        d=full();d.pop('salary_guaranteed_known');self.assertEqual(score(d)['evidence_status'],'INSUFFICIENT_EVIDENCE')
    def test_unverified_blocker_cannot_clear(self):
        d=full();next(e for e in d['evidence'] if e['evidence_id']=='B_entity')['verification_status']='unverified';self.assertIn('entity',score(d)['unresolved_blockers'])

    def test_one_way_conflict_excludes_both(self):
        d=full();other=evidence('E2');other['conflicts_with']=['E1'];d['evidence'].append(other)
        self.assertAlmostEqual(score(d)['coverage'],.9)
    def test_bad_top_level(self):
        with self.assertRaises(ValueError):score([])

    def test_goal_cannot_clear_employer_blockers(self):
        d=full();e=dict(evidence('GOAL'),evidence_type='USER',verification_status='self_reported',related_dimension='fit');d['evidence'].append(e)
        for b in d['blockers'].values():b['evidence_ids']=['GOAL']
        r=score(d);self.assertEqual(r['decision'],'HOLD');self.assertIn('salary',r['unresolved_blockers'])
    def test_unrelated_public_fact_cannot_clear(self):
        d=full()
        for b in d['blockers'].values():b['evidence_ids']=['E1']
        self.assertEqual(score(d)['decision'],'HOLD')
    def test_verbal_consistent_at_seventy(self):
        d=full(7);d['stage']='verbal';self.assertEqual(score(d)['decision'],'HOLD')
    def test_empty_currency_rejected(self):
        a=full();b=full(6);b['id']='b';a['currency']=b['currency']=''
        with self.assertRaises(ValueError):compare({'offers':[a,b]})

    def test_wrong_dimension_not_covered(self):
        d=full()
        for rows in d['dimensions'].values():
            for row in rows:row['evidence_ids']=['D_role']
        r=score(d);self.assertEqual(r['coverage'],.2);self.assertEqual(r['decision'],'HOLD')
    def test_comparison_cutoff_mismatch(self):
        a=full();b=full();b.update(id='b',research_as_of='2026-11-07')
        with self.assertRaises(ValueError):compare({'offers':[a,b]})
    def test_comparison_cutoff_required(self):
        a=full();b=full();b['id']='b';a.pop('research_as_of');b.pop('research_as_of')
        with self.assertRaises(ValueError):compare({'offers':[a,b]})
