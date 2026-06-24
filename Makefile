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
	spark-submit \
	  --packages com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.44.2,org.postgresql:postgresql:42.7.3 \
	  -m igaming_elt.run_spark

	
