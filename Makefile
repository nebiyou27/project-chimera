IMAGE := chimera:latest

.PHONY: setup build test spec-check

# Install dependencies locally (developer machine)
setup:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

# Build the Docker image used for reproducible tests
build:
	docker build -t $(IMAGE) .

# Run pytest inside the container. Exit code from pytest is propagated.
test: build
	docker run --rm -v "$(PWD)":/app -w /app $(IMAGE) pytest -q

# Run the lightweight spec checker inside the container
spec-check: build
	docker run --rm -v "$(PWD)":/app -w /app $(IMAGE) python scripts/spec_check.py
test:
	python -m pytest -q
