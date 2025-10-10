#!/bin/bash
# Development environment setup script

set -e

echo "Setting up ScaleBox Python SDK development environment..."

# Check if Python 3.8+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8+ is required, but found Python $python_version"
    exit 1
fi

echo "Python version: $python_version ✓"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "Installing development dependencies..."
pip install -e .[dev]

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run initial checks
echo "Running initial checks..."
echo "Checking code formatting..."
black --check scalebox || echo "Code formatting issues found. Run 'black scalebox' to fix."

echo "Checking import sorting..."
isort --check-only scalebox || echo "Import sorting issues found. Run 'isort scalebox' to fix."

echo "Running type checks..."
mypy scalebox --ignore-missing-imports || echo "Type check issues found."

echo "Running linting..."
flake8 scalebox || echo "Linting issues found."

echo ""
echo "Development environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest scalebox/test -v"
echo ""
echo "To build the package:"
echo "  python -m build"
echo ""
echo "To check the package:"
echo "  twine check dist/*"
echo ""
echo "To publish to PyPI:"
echo "  twine upload dist/*"
echo ""
echo "Happy coding! 🚀"
