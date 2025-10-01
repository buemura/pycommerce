test:
	pytest

format:
	black .

lint:
	ruff check .

mig_gen:
	alembic revision --autogenerate -m "$(m)"

mig_push:
	alembic upgrade head

seed_products:
	python -m scripts.seed.seed_products

run_dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
