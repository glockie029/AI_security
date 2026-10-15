import sys
import types
import unittest
from unittest.mock import Mock, patch

from ai_security.mcp import client, server


class McpStructureTests(unittest.TestCase):
    def test_stdio_path_uses_current_absolute_interpreter(self):
        sdk = types.ModuleType("mcp")
        sdk.StdioServerParameters = Mock()
        with patch.dict(sys.modules, {"mcp": sdk}):
            client.get_server_params()
        sdk.StdioServerParameters.assert_called_once_with(
            command=sys.executable, args=[str(client.SERVER_PATH)]
        )
        self.assertTrue(client.SERVER_PATH.is_absolute())
        self.assertTrue(client.SERVER_PATH.is_file())

    def test_server_data_lookup_without_sdk_or_service(self):
        self.assertEqual(
            server.get_vulnerability("CVE-2021-44228")["severity"], "Critical"
        )
        self.assertEqual(
            server.get_vulnerability("invalid"), {"error": "Invalid CVE ID"}
        )
