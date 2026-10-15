import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from ai_security import cli


class CliTests(unittest.TestCase):
    def test_original_ask_command_with_mocked_api(self):
        response = SimpleNamespace(output_text="模拟回答", usage=None)
        create = Mock(return_value=response)
        client = SimpleNamespace(responses=SimpleNamespace(create=create))
        with (
            patch.object(cli, "get_client", return_value=client),
            patch.object(cli, "get_model_name", return_value="MODEL"),
        ):
            result = CliRunner().invoke(cli.app, ["ask", "问题"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("模拟回答", result.output)
        self.assertEqual(create.call_args.kwargs["input"], "问题")
        self.assertFalse(create.call_args.kwargs["store"])

    def test_chat_exit_does_not_request_api(self):
        client = Mock()
        session = Mock()
        session.prompt.return_value = "exit"
        with (
            patch.object(cli, "get_client", return_value=client),
            patch.object(cli, "get_model_name", return_value="MODEL"),
            patch.object(cli, "PromptSession", return_value=session),
            redirect_stdout(io.StringIO()),
        ):
            cli.chat()
        client.chat.completions.create.assert_not_called()
