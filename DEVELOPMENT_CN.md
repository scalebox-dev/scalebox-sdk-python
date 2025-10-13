# Development Guide

## 开发模式说明 (Development Workflow)

本项目采用**开源项目标准工作流**，使用 `main` 作为受保护分支，通过 Pull Request 进行代码合并和自动化版本管理。

### 🎯 工作流程概览

```
功能开发分支 (feature/*)
      ↓
  创建 Pull Request
      ↓
  代码审查 + CI 测试
      ↓
  合并到 main 分支
      ↓
  🤖 自动版本升级（根据提交信息）
      ↓
  🚀 自动发布到 PyPI
```

## 自动化版本管理 (Automated Version Management)

### 🚀 推荐：约定式提交触发自动升级

**最佳实践**：使用约定式提交（Conventional Commits），系统会自动检测并选择正确的版本类型。

#### 约定式提交规范

| 提交前缀 | 版本升级 | 示例 | 说明 |
|---------|---------|------|------|
| `feat:` / `feature:` | **minor** | `feat: add user authentication` | 新功能 |
| `fix:` / `bugfix:` / `hotfix:` | **patch** | `fix: resolve memory leak` | 错误修复 |
| `breaking:` / `break:` | **major** | `breaking: change API signature` | 破坏性更改 |
| `chore:` / `refactor:` / `style:` / `perf:` | **patch** | `chore: update dependencies` | 维护性更改 |
| 其他 | **patch** | `docs: update README` | 默认补丁版本 |

#### 完整开发流程示例

```bash
# 1. 从 main 创建功能分支
git checkout main
git pull origin main
git checkout -b feature/user-auth

# 2. 进行开发
# ... 编写代码 ...

# 3. 使用约定式提交
git add .
git commit -m "feat: add user authentication system

- Implement JWT token generation
- Add login/logout endpoints
- Add user session management"

# 4. 推送分支
git push origin feature/user-auth

# 5. 创建 Pull Request
# 通过 GitHub 界面创建 PR 到 main 分支

# 6. 合并后自动触发
# ✅ CI 自动检测为 "feat:" → minor 版本升级
# ✅ 版本从 0.1.7 → 0.2.0
# ✅ 自动创建标签 v0.2.0
# ✅ 自动发布到 PyPI
```

### 🔧 备选：本地脚本（测试用）

**注意**：本地脚本仅用于开发测试，不推荐用于正式发布。

```bash
# 预览版本升级（不实际修改）
python scripts/bump_version.py patch --dry-run

# 测试版本升级
python scripts/bump_version.py patch --no-tag

# 检查更改
git diff
```

### 🔄 自动化发布流程

#### 触发条件

**主要触发方式**：
- ✅ **PR 合并到 main**：推荐，符合开源项目最佳实践
- ⚠️ **直接推送到 main**：仅用于紧急修复
- 🔧 **手动触发**: 通过 GitHub Actions 界面（备用）

#### 自动化执行步骤

**阶段1：智能版本检测**
```yaml
1. 分析合并的提交信息
2. 根据约定式提交前缀决定版本类型：
   - feat: → minor (0.1.7 → 0.2.0)
   - fix: → patch (0.1.7 → 0.1.8)
   - breaking: → major (0.1.7 → 1.0.0)
3. 执行版本升级脚本
```

**阶段2：版本文件更新**
```yaml
自动更新以下文件：
- scalebox/__init__.py          (__version__ 和 __version_info__)
- scalebox/version.py            (__version__ 和 __version_info__)
- pyproject.toml                 (version 字段)
- CHANGELOG.md                   (版本历史)
```

**阶段3：提交和标签**
```yaml
1. 提交版本更改：chore: auto-bump version to X.Y.Z
2. 推送到 main 分支
3. 创建并推送标签：vX.Y.Z
```

**阶段4：代码质量检查**
```yaml
并行运行：
- 代码格式检查 (Black)
- 导入排序检查 (isort)
- 代码质量检查 (flake8)
- 类型检查 (mypy)
- 单元测试 (pytest)
```

**阶段5：构建和发布**
```yaml
1. Checkout 最新 main 分支
2. Pull 最新提交（包含版本升级）
3. 构建 Python 包（使用最新版本号）
4. 检查包质量 (twine check)
5. 发布到 PyPI
```

#### 版本同步机制

**关键特性**：
- ✅ `__version__` 和 `__version_info__` 自动同步
- ✅ 所有版本文件一次性更新
- ✅ publish 作业使用最新版本构建
- ✅ GitHub 版本号 = PyPI 版本号

### 📁 版本文件管理

项目中的版本信息存储在多个文件中，脚本会自动同步：

```
scalebox/
├── __init__.py          # __version__ = "0.1.7"
├── version.py           # __version__ = "0.1.7"
│                        # __version_info__ = (0, 1, 7)
└── ...

pyproject.toml           # version = "0.1.7"
CHANGELOG.md             # 自动更新版本日志
```

**重要**：`__version_info__` 元组会自动与 `__version__` 字符串保持同步。

### 🏷️ 版本规则

遵循 [语义化版本控制](https://semver.org/lang/zh-CN/) 规范：

- **MAJOR (主版本号)**: 不兼容的API更改
- **MINOR (次版本号)**: 向后兼容的功能添加  
- **PATCH (修订号)**: 向后兼容的错误修复

### 🔧 脚本选项

`bump_version.py` 脚本支持以下选项：

```bash
# 基本用法
python scripts/bump_version.py {major|minor|patch}

# 高级选项
python scripts/bump_version.py patch --dry-run      # 预览更改
python scripts/bump_version.py patch --no-tag        # 不创建Git标签
python scripts/bump_version.py patch --no-changelog # 不更新CHANGELOG
```

### 📋 发布检查清单

自动化流程会执行以下检查：

- [ ] 所有测试通过
- [ ] 代码质量检查通过
- [ ] 版本文件同步
- [ ] 包构建成功
- [ ] 包质量检查通过
- [ ] 发布到PyPI成功
- [ ] GitHub Release创建成功

### 🚨 故障排除

#### 常见问题

1. **版本不同步**:
   ```bash
   # 检查所有版本
   echo "Version in __init__.py:"
   grep "__version__" scalebox/__init__.py
   
   echo "Version in version.py:"
   grep "__version" scalebox/version.py
   
   echo "Version in pyproject.toml:"
   grep "^version" pyproject.toml
   
   # 如果不同步，拉取最新代码
   git pull origin main
   ```

2. **GitHub 版本号 ≠ PyPI 版本号**:
   ```bash
   # 检查 GitHub Actions 日志
   # 1. 确认 auto-version 作业是否成功
   # 2. 确认 publish 作业是否拉取了最新提交
   # 3. 查看构建的包版本号
   
   # 本地验证构建
   git pull origin main
   python -m build
   ls dist/  # 检查生成的包文件名
   ```

3. **Git标签冲突**:
   ```bash
   # 检查现有标签
   git tag -l
   
   # 删除本地冲突标签
   git tag -d v0.1.7
   
   # 删除远程冲突标签（谨慎操作）
   git push origin :refs/tags/v0.1.7
   ```

4. **PyPI发布失败**:
   - ✅ 检查 `PYPI_API_TOKEN` 是否正确设置
   - ✅ 确认版本号唯一性（PyPI 不允许重复版本）
   - ✅ 检查包构建是否成功
   - ✅ 验证 publish 作业是否使用了最新版本

5. **PR 合并后未触发版本升级**:
   ```bash
   # 检查提交信息是否符合约定式提交规范
   git log --oneline -1
   
   # 如果提交信息不符合规范，会默认使用 patch 版本
   # 建议使用标准前缀：feat:, fix:, breaking: 等
   ```

#### 调试模式

```bash
# 本地测试版本升级
python scripts/bump_version.py patch --dry-run

# 检查Git状态
git status
git log --oneline -5
git tag -l

# 检查CI状态
# 访问 GitHub Actions 页面查看详细日志
# 重点检查：
# - auto-version 作业输出
# - build 作业的包文件名
# - publish 作业的 git pull 输出
```

### 🔐 权限要求

自动化流程需要以下权限：

1. **GitHub Token**: 用于提交和推送更改
2. **PyPI Token**: 用于发布到PyPI
3. **仓库权限**: 写入权限用于创建标签和发布

### 📊 监控和通知

- **GitHub Actions**: 查看工作流执行状态
- **PyPI**: 确认包发布成功
- **GitHub Releases**: 查看发布历史

### 🎯 最佳实践

#### 1. 开发阶段

```bash
# ✅ 使用功能分支
git checkout -b feature/new-feature

# ✅ 使用约定式提交
git commit -m "feat: add amazing feature"

# ✅ 推送并创建 PR
git push origin feature/new-feature
# 在 GitHub 创建 Pull Request
```

#### 2. 代码审查阶段

- ✅ 检查提交信息是否符合约定式提交规范
- ✅ 确认版本升级类型是否合理
- ✅ 运行本地测试确保代码质量
- ✅ 审查代码更改

#### 3. 合并阶段

- ✅ 使用 Squash and Merge 保持提交历史清晰
- ✅ 确保合并提交信息包含正确的约定式前缀
- ✅ 合并后自动触发 CI/CD 流程

#### 4. 发布验证

```bash
# 拉取最新代码
git pull origin main

# 验证版本号
python -c "from scalebox.version import get_version, get_version_info; print(f'Version: {get_version()}, Info: {get_version_info()}')"

# 检查 PyPI
pip install scalebox-sdk --upgrade
python -c "import scalebox; print(scalebox.__version__)"

# 检查 GitHub Release
# 访问 https://github.com/scalebox-dev/scalebox-sdk-python/releases
```

#### 5. 紧急修复流程

```bash
# 如需紧急修复，可以直接在 main 分支操作
git checkout main
git pull origin main

# 修复问题
# ... 编写代码 ...

# 使用 hotfix 前缀
git commit -m "hotfix: critical security patch"
git push origin main

# 自动触发 patch 版本升级和发布
```

### 📚 相关文档

- [语义化版本控制](https://semver.org/lang/zh-CN/)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [PyPI 发布指南](https://packaging.python.org/tutorials/packaging-projects/)
- [Python 包管理](https://packaging.python.org/)

---

**注意**: 自动化版本管理大大简化了发布流程，但仍建议在重要版本发布前进行充分测试。
