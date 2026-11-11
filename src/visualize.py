"""Визуализация графа зависимостей (Этап 5).

Сначала строится текстовое представление графа на языке диаграмм
PlantUML, затем граф сохраняется в файл SVG. Отрисовка SVG выполнена
вручную средствами стандартной библиотеки, без внешних движков.
"""

NODE_WIDTH = 140
NODE_HEIGHT = 40
LAYER_GAP = 110
NODE_GAP = 30
MARGIN = 40
CHAR_WIDTH = 8


def to_plantuml(graph):
    """to_plantuml"""
    lines = ["@startuml", "left to right direction"]
    for node in graph.nodes():
        lines.append(f'component "{node}" as {_alias(node)}')
    for node in graph.nodes():
        for dep in graph.neighbors(node):
            lines.append(f"{_alias(node)} --> {_alias(dep)}")
    lines.append("@enduml")
    return "\n".join(lines)


def _alias(name):
    """_alias"""
    return "n_" + "".join(ch if ch.isalnum() else "_" for ch in name)


def _assign_layers(graph, root):
    """_assign_layers"""
    layers = {root: 0}
    queue = [root]
    while queue:
        current = queue.pop(0)
        for dep in graph.neighbors(current):
            if dep not in layers:
                layers[dep] = layers[current] + 1
                queue.append(dep)
    for node in graph.nodes():
        layers.setdefault(node, 0)
    return layers


def _layout_positions(graph, root):
    """_layout_positions"""
    layers = _assign_layers(graph, root)
    buckets = {}
    for node in graph.nodes():
        buckets.setdefault(layers[node], []).append(node)
    positions = {}
    for depth, names in sorted(buckets.items()):
        for index, name in enumerate(sorted(names)):
            x = MARGIN + depth * (NODE_WIDTH + LAYER_GAP)
            y = MARGIN + index * (NODE_HEIGHT + NODE_GAP)
            positions[name] = (x, y)
    return positions


def _svg_header(width, height):
    """_svg_header"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )


def _svg_node(name, position):
    """_svg_node"""
    x, y = position
    text_x = x + NODE_WIDTH // 2
    text_y = y + NODE_HEIGHT // 2 + 5
    return (
        f'<rect x="{x}" y="{y}" width="{NODE_WIDTH}" '
        f'height="{NODE_HEIGHT}" rx="6" fill="#e8f0fe" '
        f'stroke="#1a73e8"/>'
        f'<text x="{text_x}" y="{text_y}" font-size="13" '
        f'text-anchor="middle" font-family="sans-serif">{name}</text>'
    )


def _svg_edge(start, end):
    """_svg_edge"""
    x1 = start[0] + NODE_WIDTH
    y1 = start[1] + NODE_HEIGHT // 2
    x2 = end[0]
    y2 = end[1] + NODE_HEIGHT // 2
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="#5f6368" marker-end="url(#arrow)"/>'
    )


def _svg_defs():
    """_svg_defs"""
    return (
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" '
        'refX="8" refY="3" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,0 L8,3 L0,6 Z" fill="#5f6368"/></marker></defs>'
    )


def _canvas_size(positions):
    """_canvas_size"""
    max_x = max((p[0] for p in positions.values()), default=0)
    max_y = max((p[1] for p in positions.values()), default=0)
    width = max_x + NODE_WIDTH + MARGIN
    height = max_y + NODE_HEIGHT + MARGIN
    return width, height


def to_svg(graph, root):
    """to_svg"""
    positions = _layout_positions(graph, root)
    width, height = _canvas_size(positions)
    parts = [_svg_header(width, height), _svg_defs()]
    for node in graph.nodes():
        for dep in graph.neighbors(node):
            parts.append(_svg_edge(positions[node], positions[dep]))
    for node in graph.nodes():
        parts.append(_svg_node(node, positions[node]))
    parts.append("</svg>")
    return "\n".join(parts)


def save_svg(graph, root, path):
    """save_svg"""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(to_svg(graph, root))
