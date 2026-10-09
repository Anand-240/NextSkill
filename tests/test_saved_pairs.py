import json
import unittest
from unittest.mock import patch
from engine import ROOT,run,SerpClient
from personas import saved_pairs

class SavedPairTests(unittest.TestCase):
    def test_every_saved_pair_runs_without_network(self):
        manifest=saved_pairs()
        self.assertGreaterEqual(len(manifest),8)
        with patch('engine._request',side_effect=AssertionError('network')):
            for pair in manifest:
                with self.subTest(pair=pair['id']):
                    r=run(pair['role'],pair['city'],resume=pair['resume'],pages=pair['pages'],client=SerpClient(use_fixtures=True,cache_only=True),experience_level='Fresher')
                    self.assertGreater(r['eligible_count'],0)
                    self.assertTrue(r['retrieved_dates'])
                    if pair['low_data_case']:self.assertTrue(r['limited_data'])
