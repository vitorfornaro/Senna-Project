# -----------------------------
# Configurações
# -----------------------------
PYTHON      := python3
SRC         := senna-project/src
VENV        := venv
PIP         := $(VENV)/bin/pip
ACTIVATE    := . $(VENV)/bin/activate

# -----------------------------
# Comandos principais
# -----------------------------

help:        ## Mostrar ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-15s %s\n", $$1, $$2}'

setup:       ## Criar venv e instalar dependências
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

start:       ## Executar em modo produção
	$(PYTHON) $(SRC)/main.py

dev:         ## Executar API Flask em modo desenvolvimento
	$(PYTHON) $(SRC)/api/app.py

streamlit:   ## Executar interface em Streamlit
	streamlit run app_streamlit.py

stop:        ## Placeholder para parar serviços
	@echo ">> (Aqui você pode adicionar lógica para parar processos/containers)"

restart:     ## Reiniciar serviços
	$(MAKE) stop
	$(MAKE) start

logs:        ## Mostrar logs (placeholder)
	@echo ">> (Aqui você pode adicionar comando de logs, ex: docker logs)"

shell:       ## Abrir shell no venv
	$(ACTIVATE) && bash

# -----------------------------
# Testes
# -----------------------------

test:        ## Executar testes
	pytest -v

test-verbose: ## Executar testes com detalhes
	pytest -vv

test-coverage: ## Executar testes com relatório de cobertura
	pytest --cov=$(SRC) --cov-report=term-missing

# -----------------------------
# Utilitários
# -----------------------------

clean:       ## Limpar caches e arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(VENV)