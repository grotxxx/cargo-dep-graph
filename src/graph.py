"""Построение и анализ графа зависимостей (Этапы 3 и 4).

Граф строится рекурсивным обходом в глубину (DFS) с учётом
максимальной глубины и корректной обработкой циклических зависимостей.
"""


class DependencyGraph:
    """Ориентированный граф зависимостей пакетов.

    Рёбра хранятся в словаре смежности: ключ — пакет, значение —
    отсортированный список его прямых зависимостей.
    """

    def __init__(self):
        """Конструктор"""
        self.edges = {}

    def add_node(self, name):
        """add_node"""
        self.edges.setdefault(name, [])

    def add_edge(self, source, target):
        """add_edge"""
        self.add_node(source)
        self.add_node(target)
        if target not in self.edges[source]:
            self.edges[source].append(target)
            self.edges[source].sort()

    def nodes(self):
        """nodes"""
        return sorted(self.edges.keys())

    def neighbors(self, name):
        """neighbors"""
        return list(self.edges.get(name, []))

    def reverse_dependencies(self, target):
        """reverse_dependencies"""
        result = [node for node, deps in self.edges.items()
                  if target in deps]
        return sorted(result)


def _visit(source, package, depth, max_depth, graph, visited):
    """_visit"""
    graph.add_node(package)
    if depth >= max_depth or package in visited:
        return
    visited.add(package)
    for dep in source.direct_dependencies(package):
        graph.add_edge(package, dep)
        _visit(source, dep, depth + 1, max_depth, graph, visited)


def build_graph(source, root, max_depth):
    """build_graph"""
    graph = DependencyGraph()
    visited = set()
    _visit(source, root, 0, max_depth, graph, visited)
    return graph


def load_order(graph, root):
    """load_order"""
    order = []
    seen = set()
    _collect_order(graph, root, seen, order)
    return order


def _collect_order(graph, node, seen, order):
    """_collect_order"""
    if node in seen:
        return
    seen.add(node)
    for dep in graph.neighbors(node):
        _collect_order(graph, dep, seen, order)
    order.append(node)
