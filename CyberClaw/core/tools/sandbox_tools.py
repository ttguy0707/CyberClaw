import os
import subprocess
from .base import cyberclaw_tool
from ..config import OFFICE_DIR
import re

def _get_safe_path(relative_path: str) -> str:
    """
    将模型传入的相对路径转换为绝对路径，并死死检查它是否越界！
    如果模型尝试传入 "../../etc/passwd"，这里会直接把它拦截。
    """
    # 将 OFFICE_DIR 转化为标准绝对路径
    base_dir = os.path.abspath(OFFICE_DIR)
    # 将目标路径转化为绝对路径
    target_path = os.path.abspath(os.path.join(base_dir, relative_path))
    
    # 核心防御：目标路径必须以 OFFICE_DIR 开头！
    if not target_path.startswith(base_dir):
        raise PermissionError(f"越权拦截：你试图访问沙盒外的路径 '{relative_path}'！你只能在 office 工位内活动。")
    
    return target_path

@cyberclaw_tool
def list_office_files(sub_dir: str = "") -> str:
    """
    查看你的 office 工位里有哪些文件和文件夹。
    如果 sub_dir 为空，则查看工位根目录。
    """
    try:
        target_dir = _get_safe_path(sub_dir)
        if not os.path.exists(target_dir):
            return f"目录不存在：{sub_dir}"
        
        items = os.listdir(target_dir)
        if not items:
            return f"[{sub_dir if sub_dir else 'office 根目录'}] 是空的。"
        
        # 格式化输出，标注是文件还是文件夹
        result = []
        for item in items:
            item_path = os.path.join(target_dir, item)
            item_type = "📁" if os.path.isdir(item_path) else "📄"
            result.append(f"{item_type} {item}")
            
        return "\n".join(result)
    except Exception as e:
        return str(e)
    
@cyberclaw_tool
def read_office_file(filepath: str) -> str:
    """
    读取 office 工位里指定文件的内容。
    filepath 参数应该是相对于 office 的路径，例如 "test.py" 或 "skills/my_skill.py"。
    """
    try:
        target_path = _get_safe_path(filepath)
        if not os.path.exists(target_path):
            return f"文件不存在：{filepath}"
        
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
            # 防爆截断：防止读取几个 G 的日志把 Token 撑爆
            if len(content) > 10000:
                return content[:10000] + "\n\n...[内容过长，已被安全截断]..."
            return content
    except Exception as e:
        return str(e)
    
@cyberclaw_tool
def write_office_file(filepath: str, content: str, mode: str = "w") -> str:
    """
    在 office 工位里操作文件内容。
    
    参数说明:
    - filepath: 相对路径，例如 "spider.py" 或 "docs/readme.md"。
    - content: 要写入的具体文本或代码内容。
    - mode: 写入模式。
        - "w" (默认): 【覆盖/新建】模式。如果文件已存在，将彻底清空原内容并写入新内容！
        - "a": 【追加】模式。保留原内容，将新内容追加到文件最末尾（常用于写日志或在文件末尾新增函数）。
        
    ⚠️ 智能体操作规范：
    1. 如果你要修改一个长文件中间的某几行，目前最安全的做法是：读取原文件，在你的内存中完成替换，然后用 "w" 模式把【完整的最新代码】重写进去。
    2. 如果你需要重命名文件或删除文件，请直接使用 execute_office_shell 工具执行 `mv` 或 `rm` 命令。
    """
    try:
        target_path = _get_safe_path(filepath)
        
        # 严格校验传入的 mode
        if mode not in ["w", "a"]:
             return "❌ 错误：mode 参数必须是 'w' (覆盖) 或 'a' (追加)。"
        
        # 如果模型想在子目录里写文件，确保子目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        with open(target_path, mode, encoding="utf-8") as f:
            # 如果是追加模式，且内容不是以换行符开头，自动补一个换行，防止代码粘连
            if mode == "a" and not content.startswith("\n"):
                f.write("\n" + content)
            else:
                f.write(content)
                
        action = "覆盖/新建" if mode == "w" else "追加"
        return f"✅ 成功以 {action} 模式写入文件：{filepath} (共 {len(content)} 字符)"
    except Exception as e:
        return str(e)
    
@cyberclaw_tool
def execute_office_shell(command: str) -> str:
    """
    在 office 工位中执行 Shell 命令。
    
    ⚠️ 【极其重要的环境限制 - 你必须遵守】：
    1. 这是一个非交互式 (Non-interactive) 终端！不要运行任何需要等待用户输入（如 [y/N]、输入密码）的命令。所有安装命令必须携带免确认参数（如 -y, --yes, --quiet）。
    2. 禁止使用 cd 命令跳出当前目录，你的活动范围仅限 office。
    3. [无状态警告] 每次执行都是一个全新的独立终端进程！cd 命令的状态不会保留到下一次工具调用。
       如果你想在子目录执行命令，请使用“命令链”（如 `cd skills && npm install`）或者“直接使用相对路径”（如 `python skills/test.py`）。
    """
    try:
        # 简单粗暴地拦截常见的跳出目录指令
        dangerous_patterns = [r"cd\s+\.\.", r"cd\s+/", r"cd\s+~", r"\.\."]
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return "❌ 权限拒绝：检测到危险的目录跳转指令。你被禁止离开 office 工位！"

        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            cwd=OFFICE_DIR,
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            timeout=60  # 60秒超时熔断
        )
        
        output = f"▶️ 执行命令: `{command}`\n"
        output += f"🔄 退出码 (Exit Code): {result.returncode}\n"
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        # 针对挂起导致的超时或报错，给予大模型明确的 Debug 提示
        if result.returncode != 0 and ("prompt" in stderr.lower() or "y/n" in stdout.lower()):
            output += "\n💡 系统提示：命令可能由于交互式等待而失败。请重试并务必添加 -y 类的免确认参数！"
        
        if stdout:
            output += f"\n[STDOUT]\n{stdout[-2000:] if len(stdout) > 2000 else stdout}"
        if stderr:
            output += f"\n[STDERR]\n{stderr[-2000:] if len(stderr) > 2000 else stderr}"
            
        if not stdout and not stderr:
            if result.returncode == 0:
                output += "\n(静默执行完毕：Exit Code 为 0，无任何终端输出)"
            else:
                output += "\n(异常退出：Exit Code 非 0，且无任何错误日志输出)"
            
        return output
        
    except subprocess.TimeoutExpired:
        return (f"❌ 严重错误：命令执行超过 60 秒已被熔断！\n"
                f"原因极可能是你运行了阻塞式命令（需要按 Y 确认，或者跑了死循环）。"
                f"请修改你的命令，确保使用静默/自动确认参数！")
    except Exception as e:
        return f"❌ 执行异常：{str(e)}"