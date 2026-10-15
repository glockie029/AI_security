import unittest

from ai_security.evaluation.citations import validate_citations


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.results = [{"source": "DOC-1"}, {"source": "DOC-2"}]

    def test_valid_citations(self):
        self.assertEqual(
            validate_citations("依据 [DOC-2] 与 [DOC-1]。", self.results),
            {"cited_ids": ["DOC-1", "DOC-2"], "invalid_ids": [], "valid": True},
        )

    def test_unknown_citation(self):
        result = validate_citations("依据 [DOC-1] 和 [DOC-9]", self.results)
        self.assertEqual(result["invalid_ids"], ["DOC-9"])
        self.assertFalse(result["valid"])

    def test_missing_citation(self):
        self.assertFalse(validate_citations("没有引用", self.results)["valid"])

    def test_duplicate_citations_are_deduplicated(self):
        result = validate_citations("[DOC-1] [DOC-1]", self.results)
        self.assertEqual(result["cited_ids"], ["DOC-1"])

    def test_empty_results(self):
        self.assertFalse(validate_citations("[DOC-1]", [])["valid"])
