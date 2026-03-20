import os
from dotenv import load_dotenv

load_dotenv()

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(CORE_DIR)
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)

WORKSPACE_DIR = os.getenv("CYBERCLAW_WORKSPACE", os.path.join(PROJECT_ROOT, "workspace"))

# 3. 🌟 规划各个核心分区的绝对路径
DB_PATH = os.path.join(WORKSPACE_DIR, "state.sqlite3")     # 状态机：潜意识与短期记忆
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory")         # 显性记忆：Markdown 画像
PERSONAS_DIR = os.path.join(WORKSPACE_DIR, "personas")     # 人设区：系统 Prompt
SCRIPTS_DIR = os.path.join(WORKSPACE_DIR, "scripts")       # 脚本区：自动化武器库

# 4. 🌟 自动基建：只要模块被导入，立刻检查并创建缺失的文件夹
for d in [WORKSPACE_DIR, MEMORY_DIR, PERSONAS_DIR, SCRIPTS_DIR]:
    os.makedirs(d, exist_ok=True)

print(f"🔧 [Config] Workspace 路径已就绪: {WORKSPACE_DIR}")