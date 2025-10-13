# Contributing to ScaleBox Python SDK

Thank you for your interest in contributing to ScaleBox Python SDK! We welcome contributions from the community and appreciate your help in making this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@scalebox.dev.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
- Basic knowledge of Python development

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/scalebox-sdk-python.git
   cd scalebox-sdk-python
   ```

3. **Set up development environment**:
   ```bash
   # Run the setup script
   ./scripts/setup-dev.sh
   
   # Or manually:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]
   pre-commit install
   ```

4. **Create a development branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Making Changes

### Code Style

We follow these coding standards:

- **PEP 8**: Python style guide
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer(s)]
```

Examples:
- `feat(sandbox): add support for custom timeouts`
- `fix(api): resolve authentication issue`
- `docs(readme): update installation instructions`
- `test(ci): add integration tests`

### Code Structure

```
scalebox/
├── __init__.py          # Main package exports
├── cli.py               # Command-line interface
├── version.py           # Version information
├── connection_config.py # Connection configuration
├── exceptions.py        # Custom exceptions
├── api/                 # API client
├── code_interpreter/    # Code execution engine
├── sandbox/             # Sandbox management
└── test/               # Test suite
```

## Testing

### Running Tests

```bash
# Run all tests
pytest scalebox/test -v

# Run specific test file
pytest scalebox/test/test_sandbox_sync_comprehensive.py -v

# Run with coverage
pytest scalebox/test --cov=scalebox --cov-report=html

# Run linting
flake8 scalebox
black --check scalebox
isort --check-only scalebox
mypy scalebox
```

### Writing Tests

- Write tests for new functionality
- Include both unit tests and integration tests
- Use descriptive test names
- Test edge cases and error conditions
- Aim for high test coverage

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange
    sandbox = Sandbox.create()
    
    # Act
    result = sandbox.run_code("print('hello')")
    
    # Assert
    assert result.logs.stdout == "hello\n"
    sandbox.close()
```

## Submitting Changes

### Pull Request Process

1. **Ensure tests pass**:
   ```bash
   pytest scalebox/test -v
   ```

2. **Run pre-commit hooks**:
   ```bash
   pre-commit run --all-files
   ```

3. **Update documentation** if needed

4. **Create a pull request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots (if applicable)
   - Breaking changes (if any)

### Pull Request Template

We use a pull request template. Please fill out all relevant sections:

- Description of changes
- Type of change (bug fix, feature, etc.)
- Testing performed
- Documentation updates
- Breaking changes

### Review Process

- All pull requests require review
- Address feedback promptly
- Keep pull requests focused and small
- Respond to review comments

## Release Process

### Version Bumping

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Automated Version Management

We use automated version management scripts with support for semantic versioning:

```bash
# Patch version (0.1.0 -> 0.1.1) - Bug fixes
python scripts/bump_version.py patch

# Minor version (0.1.0 -> 0.2.0) - New features
python scripts/bump_version.py minor

# Major version (0.1.0 -> 1.0.0) - Breaking changes
python scripts/bump_version.py major

# Preview changes (dry run)
python scripts/bump_version.py patch --dry-run

# Don't create Git tag
python scripts/bump_version.py patch --no-tag

# Don't update CHANGELOG
python scripts/bump_version.py patch --no-changelog
```

### Automatic Version File Synchronization

The script automatically updates version numbers in the following files:
- `scalebox/__init__.py` - Main package version
- `scalebox/version.py` - Version information module
- `pyproject.toml` - Project configuration
- `CHANGELOG.md` - Changelog (optional)

### GitHub Actions Automated Publishing

After version bump, GitHub Actions automatically handles the publishing process:

1. **Trigger Conditions**:
   - Push to `main` branch
   - Create `v*` tag (e.g., `v0.1.2`)

2. **Automated Process**:
   - Run test suite
   - Build Python package
   - Publish to PyPI
   - Create GitHub Release

3. **Publishing Steps**:
   ```bash
   # 1. Bump version
   python scripts/bump_version.py patch
   
   # 2. Check changes
   git diff
   
   # 3. Commit changes
   git add .
   git commit -m "Bump version to 0.1.2"
   
   # 4. Push and create tag
   git push origin main
   git push origin --tags
   
   # 5. GitHub Actions will automatically publish to PyPI
   ```

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Git tag created
- [ ] Package built and tested
- [ ] Published to PyPI

## Development Guidelines

### Adding New Features

1. **Create an issue** to discuss the feature
2. **Design the API** before implementing
3. **Write tests first** (TDD approach)
4. **Update documentation**
5. **Add examples** in README

### Bug Fixes

1. **Reproduce the bug** with a test case
2. **Fix the issue**
3. **Ensure the test passes**
4. **Add regression test**

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation
- Include code examples

## Getting Help

### Resources

- **Documentation**: https://docs.scalebox.dev/python-sdk
- **Issues**: https://github.com/scalebox-dev/scalebox-sdk-python/issues
- **Discussions**: https://github.com/scalebox-dev/scalebox-sdk-python/discussions
- **Email**: dev@scalebox.dev

### Community

- Join our Discord server
- Follow us on Twitter
- Star the repository

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to ScaleBox Python SDK! 🚀
