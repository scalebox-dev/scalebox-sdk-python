# Development Guide

> [中文文档](./DEVELOPMENT_CN.md)

## Development Workflow

This project follows the **open-source project standard workflow**, using `main` as the protected branch, with code merging and automated version management through Pull Requests.

### 🎯 Workflow Overview

```
Feature Development Branch (feature/*)
      ↓
  Create Pull Request
      ↓
  Code Review + CI Testing
      ↓
  Merge to main branch
      ↓
  🤖 Automatic Version Bump (based on commit message)
      ↓
  🚀 Automatic Publish to PyPI
```

## Automated Version Management

### 🚀 Recommended: Conventional Commits Trigger Automatic Bumps

**Best Practice**: Use Conventional Commits, and the system will automatically detect and select the correct version type.

#### Conventional Commits Specification

| Commit Prefix | Version Bump | Example | Description |
|--------------|--------------|---------|-------------|
| `feat:` / `feature:` | **minor** | `feat: add user authentication` | New features |
| `fix:` / `bugfix:` / `hotfix:` | **patch** | `fix: resolve memory leak` | Bug fixes |
| `breaking:` / `break:` | **major** | `breaking: change API signature` | Breaking changes |
| `chore:` / `refactor:` / `style:` / `perf:` | **patch** | `chore: update dependencies` | Maintenance changes |
| Others | **patch** | `docs: update README` | Default patch version |

#### Complete Development Flow Example

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/user-auth

# 2. Develop
# ... write code ...

# 3. Use conventional commits
git add .
git commit -m "feat: add user authentication system

- Implement JWT token generation
- Add login/logout endpoints
- Add user session management"

# 4. Push branch
git push origin feature/user-auth

# 5. Create Pull Request
# Create PR to main branch through GitHub interface

# 6. After merge, automatically triggers
# ✅ CI automatically detects "feat:" → minor version bump
# ✅ Version from 0.1.7 → 0.2.0
# ✅ Automatically create tag v0.2.0
# ✅ Automatically publish to PyPI
```

### 🔧 Alternative: Local Scripts (For Testing)

**Note**: Local scripts are only for development testing, not recommended for official releases.

```bash
# Preview version bump (dry run)
python scripts/bump_version.py patch --dry-run

# Test version bump
python scripts/bump_version.py patch --no-tag

# Check changes
git diff
```

### 🔄 Automated Release Process

#### Trigger Conditions

**Primary Trigger Methods**:
- ✅ **PR Merge to main**: Recommended, follows open-source best practices
- ⚠️ **Direct Push to main**: Only for emergency fixes
- 🔧 **Manual Trigger**: Through GitHub Actions interface (backup)

#### Automated Execution Steps

**Phase 1: Intelligent Version Detection**
```yaml
1. Analyze merged commit messages
2. Decide version type based on conventional commit prefix:
   - feat: → minor (0.1.7 → 0.2.0)
   - fix: → patch (0.1.7 → 0.1.8)
   - breaking: → major (0.1.7 → 1.0.0)
3. Execute version bump script
```

**Phase 2: Version File Updates**
```yaml
Automatically update the following files:
- scalebox/__init__.py          (__version__ and __version_info__)
- scalebox/version.py            (__version__ and __version_info__)
- pyproject.toml                 (version field)
- CHANGELOG.md                   (version history)
```

**Phase 3: Commit and Tag**
```yaml
1. Commit version changes: chore: auto-bump version to X.Y.Z
2. Push to main branch
3. Create and push tag: vX.Y.Z
```

**Phase 4: Code Quality Checks**
```yaml
Run in parallel:
- Code formatting check (Black)
- Import sorting check (isort)
- Code quality check (flake8)
- Type checking (mypy)
- Unit tests (pytest)
```

**Phase 5: Build and Publish**
```yaml
1. Checkout latest main branch
2. Pull latest commits (including version bump)
3. Build Python package (using latest version number)
4. Check package quality (twine check)
5. Publish to PyPI
```

#### Version Synchronization Mechanism

**Key Features**:
- ✅ `__version__` and `__version_info__` automatically synced
- ✅ All version files updated in one go
- ✅ Publish job uses latest version for build
- ✅ GitHub version = PyPI version

### 📁 Version File Management

Version information is stored in multiple files across the project, which the script automatically synchronizes:

```
scalebox/
├── __init__.py          # __version__ = "0.1.7"
├── version.py           # __version__ = "0.1.7"
│                        # __version_info__ = (0, 1, 7)
└── ...

pyproject.toml           # version = "0.1.7"
CHANGELOG.md             # Automatically update version log
```

**Important**: `__version_info__` tuple is automatically kept in sync with `__version__` string.

### 🏷️ Version Rules

Following [Semantic Versioning](https://semver.org/) specification:

- **MAJOR (Major version)**: Incompatible API changes
- **MINOR (Minor version)**: Backward-compatible feature additions  
- **PATCH (Patch version)**: Backward-compatible bug fixes

### 🔧 Script Options

The `bump_version.py` script supports the following options:

```bash
# Basic usage
python scripts/bump_version.py {major|minor|patch}

# Advanced options
python scripts/bump_version.py patch --dry-run      # Preview changes
python scripts/bump_version.py patch --no-tag        # Don't create Git tag
python scripts/bump_version.py patch --no-changelog # Don't update CHANGELOG
```

### 📋 Release Checklist

The automated process performs the following checks:

- [ ] All tests pass
- [ ] Code quality checks pass
- [ ] Version files synchronized
- [ ] Package builds successfully
- [ ] Package quality check passes
- [ ] Published to PyPI successfully
- [ ] GitHub Release created successfully

### 🚨 Troubleshooting

#### Common Issues

1. **Version Out of Sync**:
   ```bash
   # Check all versions
   echo "Version in __init__.py:"
   grep "__version__" scalebox/__init__.py
   
   echo "Version in version.py:"
   grep "__version" scalebox/version.py
   
   echo "Version in pyproject.toml:"
   grep "^version" pyproject.toml
   
   # If out of sync, pull latest code
   git pull origin main
   ```

2. **GitHub Version ≠ PyPI Version**:
   ```bash
   # Check GitHub Actions logs
   # 1. Confirm auto-version job succeeded
   # 2. Confirm publish job pulled latest commits
   # 3. Check built package version
   
   # Verify build locally
   git pull origin main
   python -m build
   ls dist/  # Check generated package filename
   ```

3. **Git Tag Conflict**:
   ```bash
   # Check existing tags
   git tag -l
   
   # Delete local conflicting tag
   git tag -d v0.1.7
   
   # Delete remote conflicting tag (use with caution)
   git push origin :refs/tags/v0.1.7
   ```

4. **PyPI Publish Fails**:
   - ✅ Check if `PYPI_API_TOKEN` is correctly set
   - ✅ Confirm version uniqueness (PyPI doesn't allow duplicate versions)
   - ✅ Check if package builds successfully
   - ✅ Verify publish job used latest version

5. **PR Merge Doesn't Trigger Version Bump**:
   ```bash
   # Check if commit message follows conventional commit specification
   git log --oneline -1
   
   # If commit message doesn't follow spec, defaults to patch version
   # Recommended to use standard prefixes: feat:, fix:, breaking:, etc.
   ```

#### Debug Mode

```bash
# Test version bump locally
python scripts/bump_version.py patch --dry-run

# Check Git status
git status
git log --oneline -5
git tag -l

# Check CI status
# Visit GitHub Actions page to view detailed logs
# Focus on:
# - auto-version job output
# - build job package filename
# - publish job git pull output
```

### 🔐 Permission Requirements

The automation process requires the following permissions:

1. **GitHub Token**: For committing and pushing changes
2. **PyPI Token**: For publishing to PyPI
3. **Repository Permissions**: Write permission for creating tags and releases

### 📊 Monitoring and Notifications

- **GitHub Actions**: View workflow execution status
- **PyPI**: Confirm package published successfully
- **GitHub Releases**: View release history

### 🎯 Best Practices

#### 1. Development Phase

```bash
# ✅ Use feature branch
git checkout -b feature/new-feature

# ✅ Use conventional commits
git commit -m "feat: add amazing feature"

# ✅ Push and create PR
git push origin feature/new-feature
# Create Pull Request through GitHub interface
```

#### 2. Code Review Phase

- ✅ Check if commit message follows conventional commit specification
- ✅ Confirm version bump type is reasonable
- ✅ Run local tests to ensure code quality
- ✅ Review code changes

#### 3. Merge Phase

- ✅ Use Squash and Merge to keep commit history clean
- ✅ Ensure merge commit message includes correct conventional prefix
- ✅ After merge, automatically triggers CI/CD process

#### 4. Release Verification

```bash
# Pull latest code
git pull origin main

# Verify version number
python -c "from scalebox.version import get_version, get_version_info; print(f'Version: {get_version()}, Info: {get_version_info()}')"

# Check PyPI
pip install scalebox-sdk --upgrade
python -c "import scalebox; print(scalebox.__version__)"

# Check GitHub Release
# Visit https://github.com/scalebox-dev/scalebox-sdk-python/releases
```

#### 5. Emergency Fix Process

```bash
# For emergency fixes, can operate directly on main branch
git checkout main
git pull origin main

# Fix issue
# ... write code ...

# Use hotfix prefix
git commit -m "hotfix: critical security patch"
git push origin main

# Automatically triggers patch version bump and publish
```

### 📚 Related Documentation

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Python Packaging](https://packaging.python.org/)

---

**Note**: Automated version management greatly simplifies the release process, but thorough testing is still recommended before important version releases.
