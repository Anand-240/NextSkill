import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.build_data import redact, BuildClient

class BuildDataTests(unittest.TestCase):
    def test_redaction_preserves_source_urls(self):
        source='https://example.org/jobs/9876543210'
        clean=redact({'description':'Contact candidate@example.org +91 98765 43210', 'link':source,'api_key':'unit-test-placeholder'})
        self.assertNotIn('api_key',clean)
        self.assertNotIn('candidate@',clean['description'])
        self.assertNotIn('98765',clean['description'])
        self.assertEqual(clean['link'],source)

    def test_phase_cap_stops_before_request(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'ledger.json'
            path.write_text(json.dumps({'attempts':[{'phase':'C','category':'jobs'}]*105,'accounts':[]}))
            with patch('scripts.build_data.LEDGER',path), patch('scripts.build_data._request',side_effect=AssertionError('network')):
                with self.assertRaisesRegex(RuntimeError,'STOP'):
                    BuildClient('C').search({'engine':'google','q':'unique cap test query not cached'})
