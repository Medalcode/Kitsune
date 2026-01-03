run:
	uvicorn src.app.main:app --reload

docker-up:
	docker-compose up --build

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	./.venv/bin/ruff check .

format:
	./.venv/bin/ruff check --fix .
	./.venv/bin/ruff format .
