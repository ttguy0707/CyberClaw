import os
import sys
import time
import sqlite3
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import threading

# 引入我们写好的核心大脑和配置
from CyberClaw.core.agent import create_agent_app
from CyberClaw.core.config import DB_PATH

class CyberSpinner:
    def __init__(self, message="正在接入核心推理引擎..."):
        self.message = message
        self.is_running = False
        self.thread = None
        self.start_time = 0
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.CYAN = '\033[38;5;51m'
        self.SILVER = '\033[38;5;250m'
        self.PURPLE = '\033[38;5;141m'
        self.RESET = '\033[0m'

    def spin(self):
        i = 0
        while self.is_running:
            frame = self.frames[i % len(self.frames)]
            elapsed_time = time.time() - self.start_time
            
            sys.stdout.write(
                f"\r\033[K {self.CYAN}{frame}{self.RESET} "
                f"{self.SILVER}{self.message}{self.RESET} "
                f"{self.PURPLE}[{elapsed_time:.1f}s]{self.RESET}"
            )
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
            
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self.spin)
            self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
            self.thread = None


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def type_line(text: str, delay: float = 0.008):
    """轻微打字机效果"""
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()





def print_banner():
    clear_screen()

    CYAN = '\033[38;5;51m'         # 电光青
    PURPLE = '\033[38;5;141m'      # 霓虹紫
    SILVER = '\033[38;5;250m'      # 冷银灰
    DIM = '\033[2m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    WHITE = '\033[37m'


    logo = f"""{CYAN}{BOLD}
 ██████╗██╗   ██╗██████╗ ███████╗██████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
╚██████╗   ██║   ██████╔╝███████╗██║  ██║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝

 ██████╗██╗      █████╗ ██╗    ██╗
██╔════╝██║     ██╔══██╗██║    ██║
██║     ██║     ███████║██║ █╗ ██║
██║     ██║     ██╔══██║██║███╗██║
╚██████╗███████╗██║  ██║╚███╔███╔╝
 ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
{RESET}"""



    sub_title = f"{WHITE}{BOLD}👾  Welcome to the {PURPLE}{BOLD}CyberClaw{RESET}{WHITE}{BOLD} !  {RESET}"

    divider = f"{DIM}{PURPLE}{'━' * 78}{RESET}"

    meta = f"""
{divider}
 {SILVER}[ SYS ]{RESET} {CYAN}Neural shell initialized{RESET}
 {SILVER}[ MEM ]{RESET} {CYAN}SQLite memory lattice online{RESET}
 {SILVER}[ I/O ]{RESET} {CYAN}Workspace mount complete{RESET}
 {SILVER}[ NET ]{RESET} {CYAN}Local cognition channel stable{RESET}
{divider}
"""

    tip = (
        f"{PURPLE} >> {RESET}"
        f"{SILVER}CyberClaw 已完成启动。输入命令开始，输入 {PURPLE}/exit{RESET}{SILVER} 退出。{RESET}\n"
    )

    print(logo)
    print(sub_title)
    print()
    time.sleep(0.12)

    time.sleep(0.12)

    print(meta)
    type_line(tip, delay=0.004)


def main():
    print_banner()

    # 1. 唤醒 SQLite 物理记忆
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    memory = SqliteSaver(conn)
    app = create_agent_app(provider_name='aliyun', model_name='glm-5', checkpointer=memory)
    
    config = {"configurable": {"thread_id": "local_geek_master"}}

    # 2. 核心交互循环
    while True:
        try:
            user_input = input(" \033[38;5;51m❯\033[0m \033[38;5;250m你\033[0m > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["/exit", "/quit"]:
                print("\n \033[38;5;141m✦ 记忆已固化，CyberClaw 进入休眠。\033[0m")
                break
            
            print()
            inputs = {"messages": [HumanMessage(content=user_input)]}
            
            spinner = CyberSpinner("CyberClaw正在思考中...")
            spinner.start()
            
            is_first_token = True
            
            for msg, metadata in app.stream(inputs, config=config, stream_mode="messages"):
                
                # 情况 A：如果消息来自大模型 (Agent)
                if metadata.get("langgraph_node") == "agent":
                    
                    # 1. 拦截工具调用的意图
                    if getattr(msg, "tool_call_chunks", None):
                        # 只有包含 name 的块才是工具调用的起始信号
                        name = msg.tool_call_chunks[0].get("name")
                        if name:
                            spinner.stop()
                            print(f" \033[38;5;51m[ 唤醒内置工具 : {name} ]\033[0m")
                            spinner.message = "等待环境反馈..."
                            spinner.start()
                        continue
                        
                    # 2. 拦截正常的文本 Token 并打字机输出
                    if msg.content:
                        if is_first_token:
                            spinner.stop()
                            print(f" \033[38;5;141m👾 CyberClaw\033[0m > \033[38;5;250m", end="")
                            is_first_token = False
                        
                        # end="" 防止换行, flush=True 强制立刻推送到屏幕
                        print(msg.content, end="", flush=True)

                # 情况 B：如果消息来自工具执行结果
                elif isinstance(msg, ToolMessage):
                    spinner.stop()
                    print(f" \033[38;5;250m[ 工具执行完毕 ]\033[0m")            
                    spinner.message = "正在整合推理结果..."
                    spinner.start()
            
            if not is_first_token:
                print("\033[0m") 
            spinner.stop()

            PURPLE = '\033[38;5;141m'
            DIM = '\033[2m'
            RESET = '\033[0m'
            print(f"\n {DIM}{PURPLE}{'━' * 78}{RESET}\n")

        except KeyboardInterrupt:
            print(f"\n {DIM}{PURPLE}{'━' * 78}{RESET}")
            print("\n \033[38;5;141m✦ 强制中断，CyberClaw 进入休眠。\033[0m")
            break
            
    conn.close()

if __name__ == "__main__":
    main()