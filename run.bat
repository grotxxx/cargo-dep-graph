@echo off
REM Запуск инструмента визуализации зависимостей Cargo.
REM Аргументы передаются напрямую в main.py.
REM Пример: run.bat --package serde --source https://crates.io/api/v1/crates --depth 2

set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%src\main.py" %*
