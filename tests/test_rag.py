import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from ai_security.rag import retrieval


class ScoreVectors:
    def __matmul__(self, query_vector):
        return [0.8, 0.7, 0.4, 0.1]


class RagTests(unittest.TestCase):
    def test_top_k_and_threshold_without_loading_embedding_model(self):
        numpy = types.ModuleType("numpy")
        numpy.argsort = lambda scores: sorted(
            range(len(scores)), key=scores.__getitem__
        )
        model = Mock()
        model.encode.return_value = [[1.0]]
        with (
            patch.dict(sys.modules, {"numpy": numpy}),
            patch.object(retrieval, "get_embedding_model", return_value=model),
            patch.object(
                retrieval, "get_document_vectors", return_value=ScoreVectors()
            ),
        ):
            results = retrieval.retrieve("查询", top_k=3, threshold=0.6)
        self.assertEqual([r["source"] for r in results], ["DOC-1", "DOC-2"])
        self.assertEqual([r["score"] for r in results], [0.8, 0.7])
        model.encode.assert_called_once_with(["查询"], normalize_embeddings=True)

    def test_no_evidence_does_not_create_client(self):
        with (
            patch.object(retrieval, "retrieve", return_value=[]),
            patch.object(retrieval, "get_client") as create_client,
        ):
            result = retrieval.rag_answer("未知问题")
        self.assertEqual(result, "知识库中没有足够的相关资料")
        create_client.assert_not_called()

    def test_rag_answer_preserves_model_and_citation_flow(self):
        results = [{"source": "DOC-1", "content": "模拟资料", "score": 0.8}]
        response = types.SimpleNamespace(
            choices=[
                types.SimpleNamespace(
                    message=types.SimpleNamespace(content="回答 [DOC-1]")
                )
            ]
        )
        create = Mock(return_value=response)
        client = types.SimpleNamespace(
            chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=create))
        )
        with (
            patch.object(retrieval, "retrieve", return_value=results),
            patch.object(retrieval, "get_client", return_value=client),
            redirect_stdout(io.StringIO()),
        ):
            answer = retrieval.rag_answer("问题")
        self.assertEqual(answer, "回答 [DOC-1]")
        self.assertEqual(create.call_args.kwargs["model"], "deepseek-chat")
        context = create.call_args.kwargs["messages"][1]["content"]
        self.assertIn("[DOC-1] 模拟资料", context)
