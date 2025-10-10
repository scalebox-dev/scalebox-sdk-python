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

我们使用自动化版本管理脚本，支持语义化版本控制：

```bash
# 补丁版本 (0.1.0 -> 0.1.1) - 错误修复
python scripts/bump_version.py patch

# 次要版本 (0.1.0 -> 0.2.0) - 新功能
python scripts/bump_version.py minor

# 主要版本 (0.1.0 -> 1.0.0) - 破坏性更改
python scripts/bump_version.py major

# 预览更改（不实际修改）
python scripts/bump_version.py patch --dry-run

# 不创建Git标签
python scripts/bump_version.py patch --no-tag

# 不更新CHANGELOG
python scripts/bump_version.py patch --no-changelog
```

### 版本文件自动同步

脚本会自动更新以下文件中的版本号：
- `scalebox/__init__.py` - 主包版本
- `scalebox/version.py` - 版本信息模块
- `pyproject.toml` - 项目配置
- `CHANGELOG.md` - 更新日志（可选）

### GitHub Actions 自动发布

版本升级后，GitHub Actions会自动处理发布流程：

1. **触发条件**：
   - 推送到 `main` 分支
   - 创建 `v*` 标签（如 `v0.1.2`）

2. **自动流程**：
   - 运行测试套件
   - 构建Python包
   - 发布到PyPI
   - 创建GitHub Release

3. **发布步骤**：
   ```bash
   # 1. 升级版本
   python scripts/bump_version.py patch
   
   # 2. 检查更改
   git diff
   
   # 3. 提交更改
   git add .
   git commit -m "Bump version to 0.1.2"
   
   # 4. 推送并创建标签
   git push origin main
   git push origin --tags
   
   # 5. GitHub Actions 会自动发布到 PyPI
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
