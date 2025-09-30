test:
	pytest

format:
	black .

lint:
	ruff check .

mig-gen:
	alembic revision --autogenerate -m "$(m)"

mig-push:
	alembic upgrade head

run-dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
