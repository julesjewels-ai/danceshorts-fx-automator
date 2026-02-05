.PHONY: install run test clean

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	@if [ ! -d "$(VENV)" ]; then echo "Virtualenv not found. Run 'make install' first."; exit 1; fi
	$(PYTHON) main.py

test:
	@if [ ! -d "$(VENV)" ]; then echo "Virtualenv not found. Run 'make install' first."; exit 1; fi
	$(VENV)/bin/pytest

clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/core/__pycache__
	rm -rf tests/__pycache__
	rm -f *.mp4
	rm -f veo_instructions.json
	rm -f metadata_options.json
	rm -rf .pytest_cache