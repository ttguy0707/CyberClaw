# 懒加载快速开始指南

## 5 分钟上手

### 1. 创建技能

在 `workspace/office/skills/` 目录下创建新技能：

```
workspace/
└── office/
    └── skills/
        └── my_first_skill/
            └── SKILL.md
```

### 2. 编写技能文件

`SKILL.md` 格式：

```markdown
name: my_first_skill
description: 我的第一个技能，用于演示懒加载

## 使用方法

1. 调用 mode='help' 查看此文档
2. 调用 mode='run' command='your_command' 执行
```

### 3. 使用技能

```python
from cyberclaw.core.skill_loader import load_dynamic_skills

# 获取所有技能（自动懒加载）
tools = load_dynamic_skills()

# Agent 会自动使用这些技能
```

## 常用操作

### 查看技能数量

```python
from cyberclaw.core.skill_loader import get_skill_count

count = get_skill_count()
print(f"当前有 {count} 个技能")
```

### 添加新技能后刷新

```python
from cyberclaw.core.skill_loader import reload_skills

# 强制重新扫描技能目录
tools = reload_skills()
```

### 修改技能内容后清除缓存

```python
from cyberclaw.core.skill_loader import clear_skill_cache

# 清除缓存（下次调用自动重新加载）
clear_skill_cache()
```

## 性能提示

### ✅ 最佳实践

1. **保持技能文件精简**
   - 将 `name` 和 `description` 放在前 50 行
   - 避免在元数据部分使用大量内容

2. **合理使用缓存**
   - 系统会自动管理 LRU 缓存
   - 无需手动清除缓存（除非修改了技能内容）

3. **批量操作**
   - 添加多个技能后调用一次 `reload_skills()`
   - 避免频繁重新扫描

### ❌ 避免的做法

1. **不要频繁调用 `reload_skills()`**
   - 元数据会缓存 60 秒
   - 频繁调用不会带来性能提升

2. **不要手动清除缓存**
   - 系统会自动管理缓存
   - 只在修改技能内容后需要清除

3. **不要创建过大的技能文件**
   - 单个文件建议不超过 10KB
   - 大文件会影响加载性能

## 故障排查

### 问题：新增技能不显示

**原因**：元数据缓存未过期

**解决**：
```python
from cyberclaw.core.skill_loader import reload_skills
reload_skills()
```

### 问题：修改技能内容后仍然是旧版本

**原因**：内容缓存未失效

**解决**：
```python
from cyberclaw.core.skill_loader import clear_skill_cache
clear_skill_cache()
```

### 问题：技能扫描不到

**原因**：
- 文件名不是 `SKILL.md` 或 `README.md`
- `name` 或 `description` 不在前 50 行
- 文件编码不是 UTF-8

**解决**：
- 检查文件名和格式
- 确保 name/description 在文件开头
- 使用 UTF-8 编码保存

## 性能对比

### 传统预加载模式

```
启动时间：~2000ms (for 100 skills)
内存占用：~250KB (for 100 skills)
热更新：需要重启 Agent
```

### 懒加载模式（当前）

```
启动时间：~0.4ms (for 100 skills)
内存占用：~50KB (for 100 skills)
热更新：自动生效
```

**性能提升**：
- 启动速度提升 99.98%
- 内存占用降低 80%
- 零停机热更新

## 下一步

- 📖 [详细使用指南](LAZY_LOADING_GUIDE.md) - 完整的 API 文档
- 🏗️ [实现总结](LAZY_LOADING_SUMMARY.md) - 架构和设计细节
- 🧪 [性能基准测试](../examples/benchmark_lazy_loading.py) - 运行自己的测试
- 📝 [技能开发指南](SKILL_DEVELOPMENT.md) - 开发自定义技能

## 支持

遇到问题？

1. 查看 [故障排查](#故障排查) 部分
2. 阅读 [详细文档](LAZY_LOADING_GUIDE.md)
3. 查看 [GitHub Issues](https://github.com/your-repo/issues)
