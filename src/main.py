"""Точка входа CLI-приложения визуализации зависимостей Cargo.

Связывает все этапы работы: разбор конфигурации, сбор прямых
зависимостей, построение графа обходом в глубину, дополнительные
операции и визуализацию в PlantUML и SVG.
"""

import sys

from config import ConfigError, parse_config
from graph import build_graph, load_order
from sources import SourceError, create_source
from visualize import save_svg, to_plantuml


def _print_config(config):
    """_print_config"""
    print("Параметры запуска:")
    for key, value in config.as_items():
        print(f"  {key} = {value}")


def _print_direct(source, package):
    """_print_direct"""
    deps = source.direct_dependencies(package)
    print(f"Прямые зависимости пакета {package}:")
    for dep in deps:
        print(f"  - {dep}")
    if not deps:
        print("  (нет прямых зависимостей)")


def _print_reverse(graph, package):
    """_print_reverse"""
    reverse = graph.reverse_dependencies(package)
    print(f"Обратные зависимости пакета {package}:")
    for dep in reverse:
        print(f"  - {dep}")
    if not reverse:
        print("  (нет обратных зависимостей)")


def _print_order(graph, package):
    """_print_order"""
    order = load_order(graph, package)
    print(f"Порядок загрузки зависимостей для {package}:")
    for index, node in enumerate(order, start=1):
        print(f"  {index}. {node}")


def run(config):
    """run"""
    _print_config(config)
    source = create_source(config)
    _print_direct(source, config.package)
    graph = build_graph(source, config.package, config.depth)
    _print_reverse(graph, config.package)
    _print_order(graph, config.package)
    save_svg(graph, config.package, config.output)
    print(f"Изображение графа сохранено в файл: {config.output}")
    print("Представление PlantUML:")
    print(to_plantuml(graph))


def main(argv):
    """main"""
    try:
        config = parse_config(argv)
        run(config)
        return 0
    except (ConfigError, SourceError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
