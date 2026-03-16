PYTHON ?= .venv/bin/python
PIP := $(PYTHON) -m pip
APP_MODULE := app.main:app
HOST ?= 0.0.0.0
PORT ?= 8000
API_URL ?= http://127.0.0.1:$(PORT)

.DEFAULT_GOAL := help

.PHONY: help venv install init-db bootstrap run stop restart status smoke logs reingest re-enrich

help:
	@printf "\nAI Signals API - Make targets\n\n"
	@printf "1. make venv       Create .venv if missing\n"
	@printf "2. make install    Install Python dependencies into .venv\n"
	@printf "3. make init-db    Create database tables\n"
	@printf "4. make run        Start FastAPI server on port $(PORT)\n"
	@printf "5. make status     Check whether the API is listening\n"
	@printf "6. make smoke      Call /api/v1/signals endpoint\n"
	@printf "7. make stop       Stop the running API server\n"
	@printf "8. make restart    Restart the API server\n"
	@printf "9. make reingest   Trigger crawler once manually\n"
	@printf "10. make re-enrich Trigger enrichment jobs manually\n\n"
	@printf "Shortcut: make bootstrap  # venv + install + init-db\n\n"

venv:
	@test -x $(PYTHON) || python3 -m venv .venv
	@$(PYTHON) -m ensurepip --upgrade >/dev/null 2>&1 || true

install: venv
	$(PYTHON) -m ensurepip --upgrade
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

init-db: venv
	$(PYTHON) -m app.database.init_db

bootstrap: install init-db

run: venv
	$(PYTHON) -m uvicorn $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

stop:
	pkill -f "uvicorn $(APP_MODULE)" || true

restart: stop run

status:
	lsof -nP -iTCP:$(PORT) -sTCP:LISTEN

smoke:
	curl -fsS "$(API_URL)/api/v1/signals?page=1&size=3" | head -c 600 && printf "\n"

logs:
	@printf "Run 'make run' in a dedicated terminal to see live server logs.\n"

reingest: venv
	$(PYTHON) -c "import asyncio; from app.ingestion.workers.pipeline import run_crawler; asyncio.run(run_crawler())"

re-enrich: venv
	$(PYTHON) -c "from app.database.db import SessionLocal; from app.services.ingestion_service import run_enrichment_jobs; db = SessionLocal(); stats = run_enrichment_jobs(db=db, pending_limit=500, failed_retry_limit=500); db.commit(); print(stats); db.close()"
