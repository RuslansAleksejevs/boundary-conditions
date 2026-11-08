"""Publication boundary tests only: no new task bundle or model acquisition."""

import tempfile
import unittest
from pathlib import Path

from export_campaign import export_campaign, privacy_check


class PublicationTests(unittest.TestCase):
    def test_ordinary_synthetic_records_and_technical_generation_id_are_allowed(self):
        privacy_check({"case": "holdout-fault-001", "variables": ["p", "q"],
                       "provider_id": "gen-fictional-interface-test-only", "cost_usd": .001})

    def test_host_paths_block_publication_without_echoing_values(self):
        for path in ("/Users/FICTIONAL_TEST/path", "/home/FICTIONAL_TEST/path"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "host path") as caught:
                privacy_check({"unexpected": path})
            self.assertNotIn(path, str(caught.exception))

    def test_literal_fake_token_and_private_id_are_blocked(self):
        for value in ("sk-" + "or-v1-" + "FICTIONAL-NOT-A-KEY", "s" + "1"*21):
            with self.assertRaises(ValueError):
                privacy_check({"unexpected": value})

    def test_arbitrary_bearer_authorization_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "authorization header"):
            privacy_check({"Authorization": "Bearer FICTIONAL-TEST-NOT-A-SECRET"})

    def test_unfinished_main_cannot_release_the_corpus_or_create_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / "unfinished", Path(directory) / "public"
            source.mkdir()
            with self.assertRaisesRegex(ValueError, "before main acquisition ends"):
                export_campaign(source, target)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()