"""Тесты модуля graph (Этапы 3 и 4)."""

import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from graph import DependencyGraph, build_graph, load_order
from sources import TestRepoSource


class TestDependencyGraph(unittest.TestCase):
    """Тесты базовой структуры графа."""

    def test_add_node(self):
        """test_add_node"""
        g = DependencyGraph()
        g.add_node("A")
        self.assertIn("A", g.nodes())

    def test_add_edge(self):
        """test_add_edge"""
        g = DependencyGraph()
        g.add_edge("A", "B")
        self.assertIn("B", g.neighbors("A"))

    def test_no_duplicate_edges(self):
        """test_no_duplicate_edges"""
        g = DependencyGraph()
        g.add_edge("A", "B")
        g.add_edge("A", "B")
        self.assertEqual(g.neighbors("A").count("B"), 1)

    def test_reverse_dependencies(self):
        """test_reverse_dependencies"""
        g = DependencyGraph()
        g.add_edge("A", "C")
        g.add_edge("B", "C")
        self.assertEqual(g.reverse_dependencies("C"), ["A", "B"])

    def test_reverse_dependencies_empty(self):
        """test_reverse_dependencies_empty"""
        g = DependencyGraph()
        g.add_node("A")
        self.assertEqual(g.reverse_dependencies("A"), [])


def _make_test_source(text):
    """_make_test_source"""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    tmp.write(text)
    tmp.close()
    return tmp.name


class TestBuildGraph(unittest.TestCase):
    """Тесты построения графа через DFS."""

    def _source(self):
        """Создаёт временный тестовый граф и источник на его основе.

        Временный файл удаляется автоматически после теста через addCleanup.
        """
        path = _make_test_source("A B C\nB D\nC D\nD\n")
        self.addCleanup(os.unlink, path)
        return TestRepoSource(path)

    def test_builds_all_nodes(self):
        """test_builds_all_nodes"""
        graph = build_graph(self._source(), "A", max_depth=5)
        nodes = graph.nodes()
        for name in ("A", "B", "C", "D"):
            self.assertIn(name, nodes)

    def test_respects_max_depth(self):
        """При глубине 1 от A доходим до B и C, но не до D."""
        graph = build_graph(self._source(), "A", max_depth=1)
        self.assertIn("B", graph.nodes())
        self.assertNotIn("D", graph.nodes())

    def test_cycle_handling(self):
        """test_cycle_handling"""
        path = _make_test_source("A B\nB A\n")
        try:
            graph = build_graph(TestRepoSource(path), "A", max_depth=10)
            self.assertIn("B", graph.nodes())
        finally:
            os.unlink(path)

    def test_linear_chain(self):
        """test_linear_chain"""
        path = _make_test_source("A B\nB C\nC\n")
        try:
            graph = build_graph(TestRepoSource(path), "A", max_depth=10)
            self.assertEqual(graph.nodes(), ["A", "B", "C"])
        finally:
            os.unlink(path)


class TestLoadOrder(unittest.TestCase):
    """Тесты топологического порядка загрузки."""

    def test_leaf_first(self):
        """test_leaf_first"""
        path = _make_test_source("A B\nB\n")
        try:
            graph = build_graph(TestRepoSource(path), "A", max_depth=5)
            order = load_order(graph, "A")
            self.assertLess(order.index("B"), order.index("A"))
        finally:
            os.unlink(path)

    def test_no_duplicates(self):
        """test_no_duplicates"""
        path = _make_test_source("A B C\nB C\nC\n")
        try:
            graph = build_graph(TestRepoSource(path), "A", max_depth=5)
            order = load_order(graph, "A")
            self.assertEqual(len(order), len(set(order)))
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
