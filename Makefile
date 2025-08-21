# Makefile

PYTHON = python
SRC = senna-project/src

start:
	$(PYTHON) $(SRC)/main.py

dev:
	$(PYTHON) $(SRC)/app.py

test:
	pytest -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +