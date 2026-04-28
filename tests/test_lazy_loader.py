"""
测试懒加载技能加载器
"""
import os
import sys
import time
import tempfile
import shutil
import importlib

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyberclaw.core.skill_loader import load_dynamic_skills, get_skill_count, reload_skills, clear_skill_cache


def create_test_skills(test_dir: str, num_skills: int = 5):
    """创建测试技能"""
    skills_dir = os.path.join(test_dir, "office", "skills")
    os.makedirs(skills_dir, exist_ok=True)
    
    for i in range(num_skills):
        skill_dir = os.path.join(skills_dir, f"test_skill_{i}")
        os.makedirs(skill_dir, exist_ok=True)
        
        skill_content = f"""name: Test Skill {i}
description: 这是第 {i} 个测试技能，用于验证懒加载机制

## 详细说明

这是一个测试技能的详细文档内容。
它应该有足够的内容来测试缓存机制。

## 使用方法

1. 先调用 mode='help' 查看此文档
2. 然后调用 mode='run' 执行命令

命令示例：
```bash
echo "Skill {i} executed"
```
"""
        
        with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_content)
    
    return skills_dir


def test_lazy_loading():
    """测试懒加载功能"""
    print("=" * 60)
    print("测试 1: 基本懒加载功能")
    print("=" * 60)
    
    # 创建临时测试目录
    temp_dir = tempfile.mkdtemp(prefix="cyberclaw_test_")
    skills_dir = create_test_skills(temp_dir, num_skills=5)
    
    # 修改环境变量指向测试目录
    original_env = os.environ.get("CYBERCLAW_WORKSPACE")
    os.environ["CYBERCLAW_WORKSPACE"] = temp_dir
    
    try:
        # 重新导入配置以使用测试目录
        import cyberclaw.core.config as config_module
        importlib.reload(config_module)
        
        # 重新导入 skill_loader 以使用新的 SKILLS_DIR
        import cyberclaw.core.skill_loader as skill_loader_module
        importlib.reload(skill_loader_module)
        
        # 清除缓存
        skill_loader_module.clear_skill_cache()
        
        # 测试 1: 扫描技能
        print(f"\n[测试 1.1] 扫描技能目录...")
        count = skill_loader_module.get_skill_count()
        print(f"[OK] 扫描到 {count} 个技能")
        assert count == 5, f"期望 5 个技能，实际 {count} 个"
        
        # 测试 2: 获取工具（懒加载占位符）
        print(f"\n[测试 1.2] 获取工具列表（懒加载）...")
        start_time = time.time()
        tools = skill_loader_module.load_dynamic_skills()
        elapsed = time.time() - start_time
        print(f"[OK] 获取 {len(tools)} 个工具，耗时: {elapsed:.4f}秒")
        assert len(tools) == 5, f"期望 5 个工具，实际 {len(tools)} 个"
        
        # 测试 3: 验证工具属性
        print(f"\n[测试 1.3] 验证工具属性...")
        for i, tool in enumerate(tools):
            print(f"  - 工具 {i}: {tool.name}")
            assert "lazy_runner" in str(tool.func), f"工具 {tool.name} 不是懒加载函数"
        print(f"[OK] 所有工具都是懒加载模式")
        
        # 测试 4: 模拟首次调用（触发完整加载）
        print(f"\n[测试 1.4] 模拟首次调用技能（触发完整内容加载）...")
        start_time = time.time()
        result = tools[0].func(mode='help')
        elapsed = time.time() - start_time
        print(f"[OK] 首次调用耗时: {elapsed:.4f}秒")
        print(f"[OK] 结果预览: {result[:100]}...")
        assert "Test Skill 0" in result, "技能内容未正确加载"
        
        # 测试 5: 第二次调用（应该使用缓存）
        print(f"\n[测试 1.5] 第二次调用（应该使用缓存）...")
        start_time = time.time()
        result2 = tools[0].func(mode='help')
        elapsed2 = time.time() - start_time
        print(f"[OK] 第二次调用耗时: {elapsed2:.4f}秒")
        if elapsed2 > 0:
            print(f"[OK] 速度提升: {(elapsed / elapsed2):.2f}x")
        else:
            print(f"[OK] 速度提升: 缓存响应极快 (< 0.001s)")
        assert elapsed2 <= elapsed, "第二次调用应该更快或相等（使用缓存）"
        
        print("\n" + "=" * 60)
        print("测试 2: 强制重新扫描")
        print("=" * 60)
        
        # 测试 6: 添加新技能
        print(f"\n[测试 2.1] 添加新技能...")
        new_skill_dir = os.path.join(skills_dir, "new_skill")
        os.makedirs(new_skill_dir, exist_ok=True)
        with open(os.path.join(new_skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("name: New Skill\ndescription: 新添加的技能")
        
        # 强制重新扫描
        print(f"\n[测试 2.2] 强制重新扫描...")
        skill_loader_module.reload_skills()
        count_after = skill_loader_module.get_skill_count()
        print(f"[OK] 扫描后技能数: {count_after}")
        assert count_after == 6, f"期望 6 个技能，实际 {count_after} 个"
        
        print("\n" + "=" * 60)
        print("测试 3: 缓存清除")
        print("=" * 60)
        
        # 测试 7: 清除缓存
        print(f"\n[测试 3.1] 清除缓存...")
        skill_loader_module.clear_skill_cache()
        
        # 再次调用应该重新加载
        print(f"\n[测试 3.2] 缓存清除后首次调用...")
        start_time = time.time()
        result3 = tools[0].func(mode='help')
        elapsed3 = time.time() - start_time
        print(f"[OK] 缓存清除后调用耗时: {elapsed3:.4f}秒")
        
        print("\n" + "=" * 60)
        print("[PASS] 所有测试通过！")
        print("=" * 60)
        
    finally:
        # 恢复原始环境变量
        if original_env is not None:
            os.environ["CYBERCLAW_WORKSPACE"] = original_env
        else:
            os.environ.pop("CYBERCLAW_WORKSPACE", None)
        
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n[OK] 临时测试目录已清理")


if __name__ == "__main__":
    test_lazy_loading()
