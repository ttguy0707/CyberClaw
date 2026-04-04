import time
import json
import os
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
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
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "local_geek_master.jsonl")

def print_header():
    """渲染 简约斜体版·CyberClaw 监控面板"""
    
    monster = (
        "  ▄█▄▄█▄  \n"
        " ▀██████▀ \n"
        " ██▄██▄██ \n"
        "  ▀    ▀  "
    )
    

    content = Text(justify="center")
    content.append("\n  Live Stream  \n\n", style="bold white italic")
    content.append(monster + "\n\n", style="color(141)")
    content.append("   What is CyberClaw doing?    \n", style="dim white italic") 

    panel = Panel(
        Align.center(content),  
        title="[bold color(141)] CyberClaw [/bold color(141)]",
        title_align="left",
        border_style="color(141)",
        box=box.ROUNDED,
        width=42,               
        padding=0
    )

    console.print(Align.center(panel))
    console.print()

def tail_f(filepath):
    """文件末尾监听"""
    if not os.path.exists(filepath):
        console.print(f"[warning]⏳ 等待日志文件生成...[/warning]")
        while not os.path.exists(filepath):
            time.sleep(0.5)
            
    with open(filepath, 'r', encoding='utf-8') as f:
        f.seek(0, 2)
        print_header()
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

def render_event(line: str):
    """解析并渲染监控日志 (100% 中文还原)"""
    try:
        data = json.loads(line.strip())
        event = data.get("event")
        ts_str = data.get("ts", "") 
        try:
            if ts_str.endswith('Z'): ts_str = ts_str[:-1] + '+00:00'
            dt_local = datetime.fromisoformat(ts_str).astimezone()
            ts = dt_local.strftime("%H:%M:%S")
        except:
            ts = ts_str.split("T")[-1][:8]
            
        prefix = f"[timestamp][ {ts} ][/timestamp] "
        
        if event == "llm_input":
            count = data.get("message_count", 0)
            console.print(f"{prefix}[llm_input]🧠 神经元唤醒：发送了 {count} 条上下文记忆...[/llm_input]")
            
        elif event == "tool_call":
            tool_name = data.get("tool", "unknown")
            args_str = json.dumps(data.get("args", {}), ensure_ascii=False, indent=2) 
            content = f"[bold white] ● 使用工具: [/bold white][bold color(141)]{tool_name}[/bold color(141)]\n传入参数:\n{args_str}"
            console.print(Panel(content, title=f"✦ 意图决断 [ {ts} ]", title_align="left", border_style="color(141)", width=60))
            
        elif event == "tool_result":
            tool_name = data.get("tool", "unknown")
            result = data.get("result_summary", "")
            display_result = result[:300] + "\n...[截断]..." if len(result) > 300 else result
            content = f"[bold white] ● 执行结果: [/bold white][bold cyan]{tool_name}[/bold cyan]\n{display_result}"
            console.print(Panel(content, title=f"✦ 环境回传 [ {ts} ]", title_align="left", border_style="cyan", width=60))
            
        elif event == "system_action":
            action = data.get("content", "")
            console.print(f"{prefix}[warning]✦ 底层状态机：{action}[/warning]")
            
    except: pass

def main():
    try:
        console.clear()
        for line in tail_f(LOG_FILE):
            render_event(line)
    except KeyboardInterrupt:
        console.print("\n[warning]✦ 监控网络已断开。[/warning]")

if __name__ == "__main__":
    main()