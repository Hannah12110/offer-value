import unittest
from copy import deepcopy
from test_scoring import evidence
from validate_evidence import validate,qualified

class Evidence(unittest.TestCase):
    def test_valid(self):self.assertTrue(validate([evidence()])['valid'])
    def test_duplicates(self):self.assertFalse(validate([evidence(),evidence()])['valid'])
    def test_missing_url(self):
        e=evidence();e.pop('source_url');self.assertFalse(validate([e])['valid'])
    def test_private(self):
        e=evidence();e['source_url']='user://case/1';self.assertFalse(validate([e])['valid']);e['private']=True;self.assertTrue(validate([e])['valid'])
    def test_bad_date(self):
        e=evidence();e['accessed_at']='wrong';self.assertFalse(validate([e])['valid'])
    def test_conflict_dangling(self):
        e=evidence();e['conflicts_with']=['E2'];self.assertFalse(validate([e])['valid'])
    def test_stale(self):
        e=evidence();e['freshness']='stale';self.assertFalse(qualified(e,'company'))
    def test_company_self_report(self):
        e=evidence();e.update(evidence_type='B',verification_status='self_reported');self.assertFalse(qualified(e,'company'))
    def test_user_goal(self):
        e=evidence();e.update(evidence_type='USER',verification_status='self_reported');self.assertTrue(qualified(e,'fit'));self.assertFalse(qualified(e,'capital'))
    def test_estimate(self):
        e=evidence();e['claim_kind']='ESTIMATE';self.assertFalse(qualified(e,'location'))

    def test_enum_wrong_type(self):
        e=evidence();e['credibility']=[];self.assertFalse(validate([e])['valid'])
