import os
import sys
import types
import unittest
from unittest.mock import Mock, patch

from ai_security import config


class ConfigTests(unittest.TestCase):
    def test_project_env_path_without_overriding_environment(self):
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = Mock()
        with patch.dict(sys.modules, {"dotenv": dotenv}):
            config.load_environment()
        dotenv.load_dotenv.assert_called_once_with(
            config.PROJECT_ROOT / ".env", override=False
        )

    def test_default_model(self):
        with (
            patch.object(config, "load_environment"),
            patch.dict(os.environ, {}, clear=True),
        ):
            self.assertEqual(config.get_model_name(), "deepseek-flash")

    def test_configured_model(self):
        with (
            patch.object(config, "load_environment"),
            patch.dict(os.environ, {"MODEL": "MODEL"}),
        ):
            self.assertEqual(config.get_model_name(), "MODEL")

    def test_missing_key_fails_only_when_client_requested(self):
        with (
            patch.object(config, "load_environment"),
            patch.dict(os.environ, {}, clear=True),
        ):
            with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
                config.get_client()

    def test_client_creation_is_mocked_and_preserves_variable_names(self):
        sdk = types.ModuleType("openai")
        sdk.OpenAI = Mock(return_value=object())
        environment = {"DEEPSEEK_API_KEY": "TOKEN", "base_url": "https://HOST.invalid"}
        with (
            patch.object(config, "load_environment"),
            patch.dict(os.environ, environment, clear=True),
            patch.dict(sys.modules, {"openai": sdk}),
        ):
            client = config.get_client()
        self.assertIs(client, sdk.OpenAI.return_value)
        sdk.OpenAI.assert_called_once_with(
            api_key="TOKEN", base_url="https://HOST.invalid"
        )
