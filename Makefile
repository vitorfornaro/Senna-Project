# -----------------------------
# Configurações
# -----------------------------
PY          ?= python3
SRC         := senna-project/src
VENV        := venv
VENV_PY     := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip

.DEFAULT_GOAL := help

# -----------------------------
# Helpers
# -----------------------------
.ensure-venv:
	@test -x "$(VENV_PY)" || $(MAKE) setup

# -----------------------------
# Comandos principais
# -----------------------------

help:        ## Mostrar ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-18s %s\n", $$1, $$2}'

setup:       ## Criar venv e instalar dependências
	$(PY) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -r requirements.txt

start: .ensure-venv ## Executar em modo produção
	$(VENV_PY) $(SRC)/main.py

dev: .ensure-venv   ## Executar API Flask em modo desenvolvimento
	$(VENV_PY) $(SRC)/api/app.py

streamlit: .ensure-venv ## Executar interface em Streamlit
	$(VENV)/bin/streamlit run app_streamlit.py

stop:        ## Placeholder para parar serviços
	@echo ">> (Aqui você pode adicionar lógica para parar processos/containers)"

restart:     ## Reiniciar serviços
	$(MAKE) stop
	$(MAKE) start

logs:        ## Mostrar logs (placeholder)
	@echo ">> (Aqui você pode adicionar comando de logs, ex: docker logs)"

shell: .ensure-venv ## Abrir shell no venv
	@echo "Ativando venv e abrindo shell..."
	@/bin/bash -c "source $(VENV)/bin/activate && exec $$SHELL"

# -----------------------------
# Testes
# -----------------------------

test: .ensure-venv          ## Executar testes
	$(VENV)/bin/pytest -v

test-verbose: .ensure-venv  ## Executar testes com detalhes
	$(VENV)/bin/pytest -vv

test-coverage: .ensure-venv ## Executar testes com relatório de cobertura
	$(VENV)/bin/pytest --cov=$(SRC) --cov-report=term-missing

# -----------------------------
# Utilitários
# -----------------------------

clean:       ## Limpar caches e arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(VENV)