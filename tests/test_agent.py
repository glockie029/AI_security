import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ai_security import agent


def message(tool_calls=None, content=None):
    return SimpleNamespace(
        tool_calls=tool_calls,
        content=content,
        model_dump=lambda **_: {"role": "assistant", "tool_calls": []},
    )


def tool_call(name, arguments):
    return SimpleNamespace(
        id="CALL", function=SimpleNamespace(name=name, arguments=arguments)
    )


class AgentTests(unittest.TestCase):
    def run_with_messages(self, messages, max_steps=3):
        create = Mock(
            side_effect=[
                SimpleNamespace(choices=[SimpleNamespace(message=item)])
                for item in messages
            ]
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )
        with (
            patch.object(agent, "get_client", return_value=client),
            patch.object(agent, "get_model_name", return_value="MODEL"),
            redirect_stdout(io.StringIO()),
        ):
            result = agent.run_agent("查询漏洞", max_steps=max_steps)
        return result, create

    def test_final_answer_without_tools(self):
        result, create = self.run_with_messages([message(content="回答")])
        self.assertEqual(result, "回答")
        self.assertEqual(create.call_count, 1)

    def test_allowed_read_only_tool(self):
        call = tool_call("get_vulnerability", '{"cve_id": "CVE-2021-44228"}')
        with patch.object(
            agent, "get_vulnerability", return_value={"severity": "Critical"}
        ) as read:
            result, create = self.run_with_messages(
                [message([call]), message(content="完成")]
            )
        read.assert_called_once_with("CVE-2021-44228")
        self.assertEqual(result, "完成")
        replies = [
            item for item in create.call_args.kwargs["messages"]
            if item["role"] == "tool"
        ]
        self.assertEqual(replies[0]["tool_call_id"], "CALL")
        self.assertEqual(json.loads(replies[0]["content"])["severity"], "Critical")

    def test_write_tool_stays_blocked(self):
        call = tool_call("update_vulnerability_status", '{"status": "resolved"}')
        with patch.object(agent, "get_vulnerability") as read:
            _, create = self.run_with_messages(
                [message([call]), message(content="已拦截")]
            )
        read.assert_not_called()
        replies = [
            item for item in create.call_args.kwargs["messages"]
            if item["role"] == "tool"
        ]
        self.assertEqual(
            json.loads(replies[0]["content"]), {"error": "Tool not allowed"}
        )

    def test_invalid_json_stays_rejected(self):
        call = tool_call("get_vulnerability", "not-json")
        _, create = self.run_with_messages([message([call]), message(content="参数错误")])
        replies = [
            item for item in create.call_args.kwargs["messages"]
            if item["role"] == "tool"
        ]
        self.assertEqual(
            json.loads(replies[0]["content"]), {"error": "Invalid tool arguments"}
        )

    def test_step_limit_is_preserved(self):
        call = tool_call("unsupported_tool", "{}")
        result, create = self.run_with_messages([message([call])], max_steps=1)
        self.assertEqual(result, "Agent 达到最大工具调用轮数，已安全停止。")
        self.assertEqual(create.call_count, 1)
