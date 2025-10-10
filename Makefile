.PHONY: help install install-dev test test-cov lint format type-check clean build publish version-bump

help: ## Show this help message
	@echo "ScaleBox Python SDK - Development Commands"
	@echo "=========================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e .[dev]
	pre-commit install

test: ## Run tests
	pytest scalebox/test -v

test-cov: ## Run tests with coverage
	pytest scalebox/test -v --cov=scalebox --cov-report=html --cov-report=term

test-integration: ## Run integration tests
	pytest scalebox/test -v -m integration

test-unit: ## Run unit tests
	pytest scalebox/test -v -m unit

lint: ## Run linting
	flake8 scalebox
	black --check scalebox
	isort --check-only scalebox

format: ## Format code
	black scalebox
	isort scalebox

type-check: ## Run type checking
	mypy scalebox --ignore-missing-imports

check: lint type-check test ## Run all checks

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Build package
	python -m build

check-package: build ## Check built package
	twine check dist/*

publish-test: build ## Publish to test PyPI
	twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	twine upload dist/*

version-patch: ## Bump patch version
	python scripts/bump_version.py patch

version-minor: ## Bump minor version
	python scripts/bump_version.py minor

version-major: ## Bump major version
	python scripts/bump_version.py major

version-dry-run: ## Show what version bump would do
	python scripts/bump_version.py patch --dry-run

setup-dev: ## Setup development environment
	./scripts/setup-dev.sh

docs: ## Generate documentation
	# Add documentation generation commands here
	@echo "Documentation generation not implemented yet"

security: ## Run security checks
	bandit -r scalebox
	safety check

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

ci: check test-cov ## Run CI checks locally

release: version-patch ## Create a new release
	git add .
	git commit -m "Bump version"
	git push origin main
	git push origin --tags

# Development shortcuts
dev: install-dev ## Quick development setup
	@echo "Development environment ready!"

# Testing shortcuts
quick-test: ## Quick test run
	pytest scalebox/test -v -x

# Build shortcuts
wheel: build ## Build wheel only
	sdist: build ## Build source distribution only

# Utility commands
update-deps: ## Update dependencies
	pip install --upgrade pip
	pip install -e .[dev] --upgrade

check-deps: ## Check for outdated dependencies
	pip list --outdated

# Docker commands (if needed)
docker-build: ## Build Docker image
	docker build -t scalebox-sdk .

docker-test: ## Run tests in Docker
	docker run --rm scalebox-sdk pytest scalebox/test -v
