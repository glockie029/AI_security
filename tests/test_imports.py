import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


class ImportTests(unittest.TestCase):
    def test_core_and_examples_import_without_optional_sdks_or_side_effects(self):
        code = textwrap.dedent(
            """
            import builtins
            import importlib

            original = builtins.__import__
            forbidden = {'openai', 'dotenv', 'mcp', 'numpy', 'sentence_transformers'}

            def guarded(name, *args, **kwargs):
                if name.split('.')[0] in forbidden:
                    raise AssertionError('导入时加载了可选依赖：' + name)
                return original(name, *args, **kwargs)

            builtins.__import__ = guarded
            for module in (
                'ai_security', 'ai_security.config', 'ai_security.agent',
                'ai_security.tools.definitions', 'ai_security.tools.validation',
                'ai_security.tools.vulnerabilities',
                'ai_security.evaluation.evaluator', 'ai_security.evaluation.citations',
                'ai_security.rag.chunking', 'ai_security.rag.retrieval',
                'ai_security.mcp.client', 'ai_security.mcp.server',
                'examples.attention_demo', 'examples.agent_state_demo',
                'examples.chunking_demo', 'examples.rag_demo',
                'examples.agent_demo', 'examples.agent_mcp_demo',
            ):
                importlib.import_module(module)
            """
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", code],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
