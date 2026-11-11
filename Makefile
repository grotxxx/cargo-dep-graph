.PHONY: run test lint clean help

PYTHON := python3
SRC := src/main.py

## help: показать список команд
help:
	@grep -E '^##' Makefile | sed 's/## //'

## run: запустить инструмент (передать аргументы через ARGS=)
run:
	$(PYTHON) $(SRC) $(ARGS)

## test: запустить все тесты
test:
	$(PYTHON) -m pytest tests/ -v 2>/dev/null || $(PYTHON) -m unittest discover -s tests -p "test_*.py" -v

## example-test: демонстрация в тестовом режиме (пакет A, файл-граф)
example-test:
	$(PYTHON) $(SRC) \
		--package A \
		--source examples/test_repo.txt \
		--mode test \
		--output graph_A.svg \
		--depth 5

## example-real: демонстрация с реальным crates.io (пакет serde, глубина 2)
example-real:
	$(PYTHON) $(SRC) \
		--package serde \
		--source https://crates.io/api/v1/crates \
		--mode real \
		--output graph_serde.svg \
		--depth 2

## clean: удалить сгенерированные файлы
clean:
	rm -f *.svg
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true
