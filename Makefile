SHELL := /bin/bash

V ?= 1

_PYTEST_FLAGS_0 := -q --tb=short
_PYTEST_FLAGS_1 :=
_PYTEST_FLAGS_2 := -v --tb=long
PYTEST_FLAGS     = $(_PYTEST_FLAGS_$(V))

_LOG_TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)

.PHONY: check-format check-types ci fix format help install lint mutate test

help:
	@echo "Usage: make <target> [V=0|1|2]"
	@echo ""
	@echo "  V=0  quiet   - failures only"
	@echo "  V=1  default - normal output (default)"
	@echo "  V=2  verbose - full output"
	@echo ""
	@echo "Read-only"
	@echo "  check-format  check formatting without modifying files"
	@echo "  check-types   run pyright type checker"
	@echo "  lint          run ruff linter without modifying files"
	@echo "  test          run pytest with coverage"
	@echo ""
	@echo "Modifying"
	@echo "  fix           auto-fix lint violations then format"
	@echo "  format        auto-format source files"
	@echo ""
	@echo "Pipelines"
	@echo "  ci            run check-format, lint, check-types, test"
	@echo "  mutate        run mutation tests (mutmut)"
	@echo ""
	@echo "Setup"
	@echo "  install       install git hooks"

check-format:
	uv run ruff format --check .

check-types:
	uv run pyright

ci:
	@mkdir -p logs
	@logfile="logs/ci-$(_LOG_TIMESTAMP).log"; \
	$(MAKE) check-format lint check-types test V=$(V) 2>&1 | tee "$$logfile"; \
	status=$${PIPESTATUS[0]}; \
	ln -sf "$$(basename $$logfile)" logs/ci.log; \
	exit $$status

fix:
	uv run ruff check --fix .
	uv run ruff format .

format:
	uv run ruff format .

install:
	@for hook in scripts/hooks/*; do \
		name=$$(basename $$hook); \
		chmod +x $$hook; \
		ln -sf "$(CURDIR)/$$hook" ".git/hooks/$$name"; \
		echo "Installed hook: $$name"; \
	done

lint:
	uv run ruff check .

mutate:
	@mkdir -p logs
	@logfile="logs/mutate-$(_LOG_TIMESTAMP).log"; \
	uv run mutmut run 2>&1 | tee "$$logfile"; \
	uv run mutmut results 2>&1 | tee -a "$$logfile"; \
	ln -sf "$$(basename $$logfile)" logs/mutate.log; \

test:
	@mkdir -p logs
	@logfile="logs/test-$(_LOG_TIMESTAMP).log"; \
	uv run pytest $(PYTEST_FLAGS) 2>&1 | tee "$$logfile"; \
	status=$${PIPESTATUS[0]}; \
	ln -sf "$$(basename $$logfile)" logs/test.log; \
	exit $$([ $$status -eq 5 ] && echo 0 || echo $$status)
