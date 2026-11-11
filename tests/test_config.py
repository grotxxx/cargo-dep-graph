"""Тесты модуля config (Этап 1)."""

import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import ConfigError, parse_config


class TestParseConfig(unittest.TestCase):
    """Тесты разбора и валидации опций командной строки."""

    def _make_test_file(self):
        """_make_test_file"""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                         delete=False)
        tmp.write("A B\n")
        tmp.close()
        return tmp.name

    def test_valid_config_real(self):
        """test_valid_config_real"""
        cfg = parse_config([
            "--package", "serde",
            "--source", "https://crates.io/api/v1/crates",
            "--mode", "real",
            "--output", "out.svg",
            "--depth", "3",
        ])
        self.assertEqual(cfg.package, "serde")
        self.assertEqual(cfg.mode, "real")
        self.assertEqual(cfg.depth, 3)

    def test_valid_config_test_mode(self):
        """test_valid_config_test_mode"""
        path = self._make_test_file()
        try:
            cfg = parse_config([
                "--package", "A",
                "--source", path,
                "--mode", "test",
                "--output", "graph.svg",
                "--depth", "2",
            ])
            self.assertEqual(cfg.mode, "test")
            self.assertEqual(cfg.source, path)
        finally:
            os.unlink(path)

    def test_invalid_mode(self):
        """test_invalid_mode"""
        with self.assertRaises(ConfigError):
            parse_config([
                "--package", "serde",
                "--source", "http://example.com",
                "--mode", "unknown",
            ])

    def test_invalid_depth_string(self):
        """test_invalid_depth_string"""
        with self.assertRaises(ConfigError):
            parse_config([
                "--package", "serde",
                "--source", "http://example.com",
                "--depth", "abc",
            ])

    def test_invalid_depth_zero(self):
        """test_invalid_depth_zero"""
        with self.assertRaises(ConfigError):
            parse_config([
                "--package", "serde",
                "--source", "http://example.com",
                "--depth", "0",
            ])

    def test_test_mode_missing_file(self):
        """test_test_mode_missing_file"""
        with self.assertRaises(ConfigError):
            parse_config([
                "--package", "A",
                "--source", "/nonexistent/path.txt",
                "--mode", "test",
            ])

    def test_config_as_items(self):
        """test_config_as_items"""
        cfg = parse_config([
            "--package", "tokio",
            "--source", "http://example.com",
        ])
        keys = [k for k, _ in cfg.as_items()]
        self.assertIn("package", keys)
        self.assertIn("depth", keys)


if __name__ == "__main__":
    unittest.main()
