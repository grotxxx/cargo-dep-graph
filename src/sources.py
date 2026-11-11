"""Получение прямых зависимостей пакетов (Этап 2).

Данные берутся либо из реального API crates.io по HTTP, либо из
локального файла описания тестового графа. Сторонние библиотеки для
получения зависимостей не используются: только стандартная библиотека.
"""

import json
import urllib.error
import urllib.request

CRATES_API = "https://crates.io/api/v1/crates"
HTTP_TIMEOUT = 15
USER_AGENT = "cargo-dep-graph (educational project)"
NORMAL_KINDS = ("normal", None)


class SourceError(Exception):
    """Ошибка получения данных об зависимостях."""


class DependencySource:
    """Базовый интерфейс источника прямых зависимостей."""

    def direct_dependencies(self, package, version=None):
        """direct_dependencies"""
        raise NotImplementedError

    def all_packages(self):
        """all_packages"""
        raise NotImplementedError


def _http_get_json(url):
    """_http_get_json"""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise SourceError(f"HTTP {error.code} при запросе {url}")
    except urllib.error.URLError as error:
        raise SourceError(f"Сетевая ошибка при запросе {url}: {error.reason}")
    except json.JSONDecodeError:
        raise SourceError(f"Некорректный JSON в ответе {url}")


class CratesIoSource(DependencySource):
    """Источник прямых зависимостей на основе API crates.io."""

    def __init__(self, base_url=CRATES_API):
        """Конструктор"""
        self.base_url = base_url.rstrip("/")

    def _resolve_version(self, package, version):
        """_resolve_version"""
        data = _http_get_json(f"{self.base_url}/{package}")
        crate = data.get("crate", {})
        if version:
            return version
        newest = crate.get("newest_version") or crate.get("max_version")
        if not newest:
            raise SourceError(f"Не удалось определить версию пакета {package}")
        return newest

    def direct_dependencies(self, package, version=None):
        """direct_dependencies"""
        resolved = self._resolve_version(package, version)
        url = f"{self.base_url}/{package}/{resolved}/dependencies"
        payload = _http_get_json(url)
        result = []
        for item in payload.get("dependencies", []):
            if item.get("kind") in NORMAL_KINDS and not item.get("optional"):
                result.append(item["crate_id"])
        return sorted(set(result))

    def all_packages(self):
        """all_packages"""
        raise SourceError("Перебор всех пакетов crates.io не поддерживается")


class TestRepoSource(DependencySource):
    """Источник зависимостей из локального файла тестового графа.

    Формат файла: на каждой строке пакет и его прямые зависимости,
    разделённые пробелами, например ``A B C``. Пакеты именуются
    большими латинскими буквами.
    """

    def __init__(self, path):
        """Конструктор"""
        self.path = path
        self.graph = self._load(path)

    def _load(self, path):
        """_load"""
        graph = {}
        with open(path, "r", encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                name, *deps = line.split()
                graph.setdefault(name, [])
                for dep in deps:
                    graph.setdefault(dep, [])
                graph[name] = sorted(set(deps))
        return graph

    def direct_dependencies(self, package, version=None):
        """direct_dependencies"""
        if package not in self.graph:
            raise SourceError(f"Пакет {package} отсутствует в тестовом графе")
        return list(self.graph[package])

    def all_packages(self):
        """all_packages"""
        return sorted(self.graph.keys())


def create_source(config):
    """create_source"""
    if config.mode == "test":
        return TestRepoSource(config.source)
    return CratesIoSource()
