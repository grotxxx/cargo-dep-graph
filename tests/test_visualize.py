"""Тесты модуля visualize (Этап 5)."""

import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from graph import build_graph
from sources import TestRepoSource
from visualize import save_svg, to_plantuml, to_svg


def _make_source(text):
    """_make_source"""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    tmp.write(text)
    tmp.close()
    return tmp.name


class TestVisualize(unittest.TestCase):
    """Тесты генерации PlantUML и SVG."""

    def setUp(self):
        """setUp"""
        self.path = _make_source("A B C\nB D\nC\nD\n")
        self.graph = build_graph(TestRepoSource(self.path), "A", 5)

    def tearDown(self):
        """tearDown"""
        os.unlink(self.path)

    def test_plantuml_markers(self):
        """test_plantuml_markers"""
        text = to_plantuml(self.graph)
        self.assertTrue(text.startswith("@startuml"))
        self.assertTrue(text.endswith("@enduml"))

    def test_plantuml_contains_edges(self):
        """test_plantuml_contains_edges"""
        text = to_plantuml(self.graph)
        self.assertIn("-->", text)

    def test_svg_root_tag(self):
        """test_svg_root_tag"""
        svg = to_svg(self.graph, "A")
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)

    def test_svg_contains_nodes(self):
        """test_svg_contains_nodes"""
        svg = to_svg(self.graph, "A")
        for name in ("A", "B", "C", "D"):
            self.assertIn(f">{name}<", svg)

    def test_save_svg_file(self):
        """test_save_svg_file"""
        out = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
        out.close()
        try:
            save_svg(self.graph, "A", out.name)
            with open(out.name, encoding="utf-8") as handle:
                content = handle.read()
            self.assertIn("<svg", content)
        finally:
            os.unlink(out.name)


if __name__ == "__main__":
    unittest.main()
