# Development Guide

## 自动化版本管理 (Automated Version Management)

本项目实现了完全自动化的版本管理和发布流程，无需手动干预。

### 🚀 自动化版本升级

#### 方法1：GitHub Actions 手动触发

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "CI/CD Pipeline" workflow
3. 点击 "Run workflow" 按钮
4. 选择版本升级类型：
   - **patch**: 补丁版本 (0.1.1 → 0.1.2) - 错误修复
   - **minor**: 次要版本 (0.1.1 → 0.2.0) - 新功能
   - **major**: 主要版本 (0.1.1 → 1.0.0) - 破坏性更改
5. 选择是否自动提交和推送更改
6. 点击 "Run workflow"

#### 方法2：本地脚本（开发时）

```bash
# 预览版本升级（不实际修改）
python scripts/bump_version.py patch --dry-run

# 执行版本升级
python scripts/bump_version.py patch

# 检查更改
git diff

# 提交更改
git add .
git commit -m "Bump version to 0.1.2"

# 推送更改和标签
git push origin main
git push origin --tags
```

### 🔄 自动化发布流程

#### 触发条件

1. **手动触发**: 通过 GitHub Actions 界面
2. **标签触发**: 推送 `v*` 标签到仓库
3. **分支触发**: 推送到 `main` 分支

#### 自动化步骤

1. **版本升级**:
   - 更新 `scalebox/__init__.py`
   - 更新 `scalebox/version.py`
   - 更新 `pyproject.toml`
   - 更新 `CHANGELOG.md`

2. **代码质量检查**:
   - 运行测试套件
   - 代码格式检查 (Black)
   - 导入排序检查 (isort)
   - 代码质量检查 (flake8)
   - 类型检查 (mypy)

3. **构建和发布**:
   - 构建 Python 包
   - 检查包质量
   - 发布到 PyPI
   - 创建 GitHub Release

### 📁 版本文件管理

项目中的版本信息存储在多个文件中，脚本会自动同步：

```
scalebox/
├── __init__.py          # __version__ = "0.1.1"
├── version.py           # __version__ = "0.1.1"
└── ...

pyproject.toml           # version = "0.1.1"
CHANGELOG.md             # 自动更新版本日志
```

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

1. **版本冲突**:
   ```bash
   # 检查当前版本
   python -c "from scalebox.version import get_version; print(get_version())"
   
   # 手动同步版本
   python scripts/bump_version.py patch --dry-run
   ```

2. **Git标签冲突**:
   ```bash
   # 检查现有标签
   git tag -l
   
   # 删除冲突标签
   git tag -d v0.1.1
   git push origin :refs/tags/v0.1.1
   ```

3. **PyPI发布失败**:
   - 检查 `PYPI_API_TOKEN` 是否正确设置
   - 确认版本号唯一性
   - 检查包构建是否成功

#### 调试模式

```bash
# 启用详细输出
python scripts/bump_version.py patch --dry-run

# 检查Git状态
git status
git log --oneline -5

# 检查CI状态
# 访问 GitHub Actions 页面查看详细日志
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

1. **版本升级前**:
   - 确保所有更改已提交
   - 运行本地测试
   - 检查CHANGELOG内容

2. **版本升级后**:
   - 验证版本号正确
   - 检查所有文件同步
   - 确认CI流程正常

3. **发布后**:
   - 验证PyPI包可用
   - 检查GitHub Release
   - 通知团队新版本

### 📚 相关文档

- [语义化版本控制](https://semver.org/lang/zh-CN/)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [PyPI 发布指南](https://packaging.python.org/tutorials/packaging-projects/)
- [Python 包管理](https://packaging.python.org/)

---

**注意**: 自动化版本管理大大简化了发布流程，但仍建议在重要版本发布前进行充分测试。
