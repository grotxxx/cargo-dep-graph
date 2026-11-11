#!/usr/bin/env bash
# Запуск инструмента визуализации зависимостей Cargo.
# Аргументы передаются напрямую в main.py.
# Пример: ./run.sh --package serde --source https://crates.io/api/v1/crates --depth 2

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/src/main.py" "$@"
