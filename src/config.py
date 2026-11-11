"""Разбор и валидация параметров командной строки (Этап 1)."""

import argparse
import os

DEFAULT_DEPTH = 3
MIN_DEPTH = 1
MAX_ALLOWED_DEPTH = 100
VALID_MODES = ("real", "test")


class ConfigError(Exception):
    """Ошибка конфигурации с понятным пользователю сообщением."""


class Config:
    """Набор настраиваемых пользователем параметров приложения."""

    def __init__(self, package, source, mode, output, depth):
        """Конструктор"""
        self.package = package
        self.source = source
        self.mode = mode
        self.output = output
        self.depth = depth

    def as_items(self):
        """as_items"""
        return (
            ("package", self.package),
            ("source", self.source),
            ("mode", self.mode),
            ("output", self.output),
            ("depth", self.depth),
        )


def build_parser():
    """build_parser"""
    parser = argparse.ArgumentParser(
        prog="cargo-dep-graph",
        description="Визуализация графа зависимостей Cargo-пакета.",
    )
    parser.add_argument("--package", required=True,
                        help="Имя анализируемого пакета")
    parser.add_argument("--source", required=True,
                        help="URL репозитория или путь к файлу графа")
    parser.add_argument("--mode", default="real",
                        help="Режим работы: real или test")
    parser.add_argument("--output", default="graph.svg",
                        help="Имя файла с изображением графа")
    parser.add_argument("--depth", default=str(DEFAULT_DEPTH),
                        help="Максимальная глубина анализа")
    return parser


def _validate_package(name):
    """_validate_package"""
    if not name or not name.strip():
        raise ConfigError("Имя пакета не может быть пустым")
    return name.strip()


def _validate_mode(mode):
    """_validate_mode"""
    if mode not in VALID_MODES:
        allowed = ", ".join(VALID_MODES)
        raise ConfigError(f"Недопустимый режим '{mode}'. Разрешено: {allowed}")
    return mode


def _validate_source(source, mode):
    """_validate_source"""
    if not source or not source.strip():
        raise ConfigError("Источник данных не может быть пустым")
    if mode == "test" and not os.path.isfile(source):
        raise ConfigError(f"Файл тестового репозитория не найден: {source}")
    return source.strip()


def _validate_output(output):
    """_validate_output"""
    if not output or not output.strip():
        raise ConfigError("Имя выходного файла не может быть пустым")
    return output.strip()


def _validate_depth(raw_depth):
    """_validate_depth"""
    try:
        depth = int(raw_depth)
    except (TypeError, ValueError):
        raise ConfigError(f"Глубина должна быть целым числом: {raw_depth}")
    if depth < MIN_DEPTH or depth > MAX_ALLOWED_DEPTH:
        raise ConfigError(
            f"Глубина должна быть в диапазоне "
            f"[{MIN_DEPTH}, {MAX_ALLOWED_DEPTH}]"
        )
    return depth


def parse_config(argv):
    """parse_config"""
    parser = build_parser()
    args = parser.parse_args(argv)
    mode = _validate_mode(args.mode)
    return Config(
        package=_validate_package(args.package),
        source=_validate_source(args.source, mode),
        mode=mode,
        output=_validate_output(args.output),
        depth=_validate_depth(args.depth),
    )
