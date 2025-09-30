test:
	pytest

format:
	black .

lint:
	ruff check .

run-dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000