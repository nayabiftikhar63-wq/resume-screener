.DEFAULT_GOAL := help
.PHONY: help install install-backend install-frontend \
        dev dev-backend dev-frontend \
        build run test clean seed \
        docker-build docker-up docker-down docker-logs

# ── Config ────────────────────────────────────────────────────────
# Override on the command line, e.g. `make dev BACKEND_PORT=9000`.
VENV          ?= venv
PYTHON        ?= $(CURDIR)/$(VENV)/bin/python
PIP           ?= $(CURDIR)/$(VENV)/bin/pip
UVICORN       ?= $(CURDIR)/$(VENV)/bin/uvicorn
BACKEND_PORT  ?= 8000
FRONTEND_PORT ?= 5173

# ── Help ──────────────────────────────────────────────────────────
help:  ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nAI Resume Screener — make targets\n\n"} \
	      /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' \
	      $(MAKEFILE_LIST)
	@echo

# ── Setup ─────────────────────────────────────────────────────────
$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: install-backend install-frontend  ## Install backend + frontend dependencies

install-backend: $(VENV)/bin/activate  ## Create venv and install Python deps
	$(PIP) install -r backend/requirements.txt

install-frontend:  ## Install Node deps for the React app
	cd frontend && npm install

# ── Dev ───────────────────────────────────────────────────────────
dev-backend:  ## Run FastAPI on :$(BACKEND_PORT) with auto-reload
	cd backend && $(UVICORN) app.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)

dev-frontend:  ## Run Vite dev server on :$(FRONTEND_PORT)
	cd frontend && npm run dev

dev:  ## Run backend + Vite dev servers concurrently (Ctrl+C stops both)
	@trap 'kill 0' EXIT INT; \
	  $(MAKE) dev-backend & \
	  $(MAKE) dev-frontend & \
	  wait

# ── Build & Production ────────────────────────────────────────────
build:  ## Build the React SPA into frontend/dist
	cd frontend && npm run build

run: build  ## Build the SPA and run FastAPI serving it on a single origin
	cd backend && $(UVICORN) app.main:app --host 0.0.0.0 --port $(BACKEND_PORT)

# ── Seed Data ────────────────────────────────────────────────────
seed:  ## Seed sample applications with pre-filled screening results
	cd backend && $(PYTHON) -m app.services.seed_applications

# ── Tests ────────────────────────────────────────────────────────
test:  ## Run the test suite
	cd backend && $(PYTHON) -m pytest tests/ -v

# ── Docker ───────────────────────────────────────────────────────
docker-build:  ## Build the Docker image
	docker compose build

docker-up:  ## Build and start the container
	docker compose up --build -d
	@echo ""
	@echo "AI Resume Screener is running at http://localhost:8000"
	@echo "Run 'make docker-logs' to follow logs."

docker-down:  ## Stop the container
	docker compose down

docker-logs:  ## Follow container logs
	docker compose logs -f

# ── Cleanup ───────────────────────────────────────────────────────
clean:  ## Remove venv, node_modules, dist, and Python caches
	rm -rf $(VENV) frontend/node_modules frontend/dist
	find backend -type d -name "__pycache__" -prune -exec rm -rf {} +
