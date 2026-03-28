import time
import json
import os
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

cyber_theme = Theme({
    "info": "dim cyan",
    "warning": "color(141)",
    "error": "bold red",
    "llm_input": "dim white",
    "tool_call": "bold yellow",
    "tool_result": "bold green",
    "ai_message": "bold bright_magenta",
    "timestamp": "dim white"
})

console = Console(theme=cyber_theme)

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "local_geek_master.jsonl")

def tail_f(filepath):
    """非阻塞监听文件末尾"""
    if not os.path.exists(filepath):
        console.print(f"[warning]⏳ 等待日志文件生成: {filepath}[/warning]")
        while not os.path.exists(filepath):
            time.sleep(0.5)
            
    with open(filepath, 'r', encoding='utf-8') as f:
        f.seek(0, 2)
        console.print(Panel("🛰️ [bold cyan]CyberClaw Livestream 监控网络已接入[/bold cyan]\n[dim]Target: " + filepath + "[/dim]", border_style="cyan", expand=False))
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

def render_event(line: str):
    """只监控底层行为与脑电波"""
    try:
        data = json.loads(line.strip())
        event = data.get("event")
        ts_str = data.get("ts", "") 
        try:

            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1] + '+00:00'

            dt_utc = datetime.fromisoformat(ts_str)

            dt_local = dt_utc.astimezone()

            ts = dt_local.strftime("%H:%M:%S")
        except Exception:

            ts = ts_str.split("T")[-1].replace("Z", "")
        prefix = f"[timestamp][ {ts} ][/timestamp] "
        
        if event == "llm_input":
            count = data.get("message_count", 0)
            console.print(f"{prefix}[llm_input]🧠 神经元唤醒：发送了 {count} 条上下文记忆...[/llm_input]")
            

        elif event == "tool_call":
            tool_name = data.get("tool", "unknown")
            args = data.get("args", {})
            # 把 JSON 参数格式化得更易读
            args_str = json.dumps(args, ensure_ascii=False, indent=2) 
            content = f"[tool_call]💡 使用工具:{tool_name}[/tool_call]\n传入参数:\n{args_str}"
            
            console.print(Panel(content, title=f"⚙️ 意图决断 [ {ts} ]", border_style="color(141)", expand=False))
            
        elif event == "tool_result":
            tool_name = data.get("tool", "unknown")
            result = data.get("result_summary", "")
            # 截断超长日志
            display_result = result[:300] + "\n...[截断]..." if len(result) > 300 else result
            content = f"[bold cyan]💻 执行结果:{tool_name}[/bold cyan]\n{display_result}"
            
            console.print(Panel(content, title=f"📡 环境回传 [ {ts} ]", border_style="color(141)", expand=False))
            

        elif event == "system_action":
            action = data.get("content", "")
            console.print(f"{prefix}[warning]⚙️ 底层状态机：{action}[/warning]")
            
        elif event == "ai_message":
            pass 
            
    except json.JSONDecodeError:
        pass

def main():
    try:
        for line in tail_f(LOG_FILE):
            render_event(line)
    except KeyboardInterrupt:
        console.print("\n[warning]✦   监控网络已断开。[/warning]")

if __name__ == "__main__":
    main()