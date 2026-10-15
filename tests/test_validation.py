import unittest

from ai_security.tools.definitions import tool_definitions
from ai_security.tools.validation import validate_cve_id


class ToolValidationTests(unittest.TestCase):
    def test_valid_cve_and_normalization(self):
        self.assertEqual(validate_cve_id("cve-2021-44228"), "CVE-2021-44228")
        self.assertEqual(validate_cve_id("CVE-2024-3094"), "CVE-2024-3094")

    def test_invalid_format(self):
        for value in ("", "CVE-21-44228", "CVE-2021-123", "CVE-2021-44228 extra"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_cve_id(value)

    def test_invalid_type(self):
        for value in (None, 123, {}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_cve_id(value)

    def test_tool_definitions_are_unique_and_unchanged(self):
        names = [item["function"]["name"] for item in tool_definitions]
        self.assertEqual(names, ["get_vulnerability", "update_vulnerability_status"])
        self.assertEqual(len(names), len(set(names)))
