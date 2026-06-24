.PHONY: up down test lint run-ingest run-spark

up:
	docker compose up -d

down:
	docker compose down -v

test:
	pytest -q

run-ingest:
	python -m igaming_elt.run_ingest

run-spark:
	python -m igaming_elt.run_spark
