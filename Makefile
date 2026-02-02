.PHONY: help setup data test lint format site serve clean

# Default target
help:
	@echo "Server Monitoring Dashboard - Makefile targets:"
	@echo ""
	@echo "  make setup    - Create virtualenv and install Python dependencies"
	@echo "  make data     - Generate _data/*.json files from logs"
	@echo "  make test     - Run Python unit tests with coverage"
	@echo "  make lint     - Run linting checks (ruff)"
	@echo "  make format   - Auto-format code with ruff"
	@echo "  make site     - Build Jekyll site (requires Ruby/bundler)"
	@echo "  make serve    - Serve Jekyll site locally at http://localhost:4000"
	@echo "  make clean    - Remove build artifacts and generated files"
	@echo ""

# Python setup
setup:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo "Installing dependencies..."
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .
	@echo "Setup complete! Activate with: source .venv/bin/activate"

# Generate data
data:
	@echo "Generating data files..."
	.venv/bin/python scripts/build_data.py
	@echo "Data generation complete!"

# Run tests
test:
	@echo "Running tests..."
	.venv/bin/pytest tests/ -v --cov=src/servermonitoring --cov-report=term-missing

# Lint code
lint:
	@echo "Running linting checks..."
	.venv/bin/ruff check src/ tests/ scripts/

# Format code
format:
	@echo "Formatting code..."
	.venv/bin/ruff check --fix src/ tests/ scripts/
	.venv/bin/ruff format src/ tests/ scripts/

# Jekyll site build
site:
	@echo "Building Jekyll site..."
	@if ! command -v bundle >/dev/null 2>&1; then \
		echo "Error: bundler not found. Install with: gem install bundler"; \
		exit 1; \
	fi
	bundle install --quiet
	bundle exec jekyll build
	@echo "Site built to _site/"

# Serve Jekyll locally
serve:
	@echo "Starting Jekyll server..."
	@if ! command -v bundle >/dev/null 2>&1; then \
		echo "Error: bundler not found. Install with: gem install bundler"; \
		exit 1; \
	fi
	bundle install --quiet
	bundle exec jekyll serve --livereload

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf _site .sass-cache .jekyll-cache .jekyll-metadata
	rm -rf htmlcov .coverage .pytest_cache
	rm -rf src/*.egg-info build dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"
