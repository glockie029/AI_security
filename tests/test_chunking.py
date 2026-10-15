import unittest

from ai_security.rag.chunking import chunk_text, split_by_headings


class ChunkingTests(unittest.TestCase):
    def test_overlap_and_offsets(self):
        self.assertEqual(
            chunk_text("abcdefghij", size=4, overlap=1),
            [
                {"start": 0, "end": 4, "content": "abcd"},
                {"start": 3, "end": 7, "content": "defg"},
                {"start": 6, "end": 10, "content": "ghij"},
            ],
        )

    def test_no_overlap(self):
        self.assertEqual(
            [chunk["content"] for chunk in chunk_text("abcde", 3, 0)],
            ["abc", "de"],
        )

    def test_empty_and_blank_text(self):
        self.assertEqual(chunk_text(""), [])
        self.assertEqual(chunk_text("   "), [])

    def test_invalid_parameters(self):
        for size, overlap in [(0, 0), (-1, 0), (3, -1), (3, 3), (3, 4)]:
            with self.subTest(size=size, overlap=overlap):
                with self.assertRaises(ValueError):
                    chunk_text("abc", size, overlap)

    def test_split_by_headings_keeps_cve(self):
        text = "# 文档\n\n## 描述\n内容一\n\n## 修复\n内容二\n"
        self.assertEqual(
            split_by_headings(text, "CVE-2021-44228"),
            [
                {"cve_id": "CVE-2021-44228", "section": "描述", "content": "内容一"},
                {"cve_id": "CVE-2021-44228", "section": "修复", "content": "内容二"},
            ],
        )

    def test_document_without_sections(self):
        self.assertEqual(split_by_headings("# 标题\n正文", "CVE-2021-44228"), [])
