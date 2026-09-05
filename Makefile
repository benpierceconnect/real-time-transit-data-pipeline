.PHONY: help configure generate-data build up down reset logs test analyze validate secret-scan secret-scan-all fresh-start export-public

help:
	@echo "Targets: configure generate-data build up down reset logs test analyze validate secret-scan secret-scan-all fresh-start export-public"

configure:
	@test -f .env || cp .env.example .env
	@echo "Review .env and replace every change-me value before running."

generate-data:
	python scripts/generate_synthetic_data.py

build:
	docker compose build

up:
	docker compose up --build

down:
	docker compose down

reset:
	docker compose down -v

logs:
	docker compose logs -f

test:
	python scripts/generate_synthetic_data.py --check
	python scripts/secret_scan.py --public-files
	python scripts/validate_project.py
	python scripts/write_manifest.py --verify
	pytest -q

analyze:
	python analysis/synthetic_trip_analysis.py

validate:
	python scripts/validate_running_stack.py

secret-scan:
	python scripts/secret_scan.py --public-files

secret-scan-all:
	python scripts/secret_scan.py

fresh-start:
	python scripts/validate_fresh_start.py --confirm-reset --keep-running

export-public:
	python scripts/export_public_candidate.py
