import os
import sys
import time
import asyncio
import shutil
import random
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.styles import Style
from prompt_toolkit.utils import get_cwidth  
from prompt_toolkit.application import get_app

from CyberClaw.core.agent import create_agent_app
from CyberClaw.core.config import DB_PATH
from CyberClaw.core.bus import task_queue

class AsyncCyberSpinner:
    def __init__(self, message="正在接入核心推理引擎..."):
        self.message = message
        self.task = None
        self.start_time = 0
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.CYAN = '\033[38;5;51m'
        self.SILVER = '\033[38;5;250m'
        self.PURPLE = '\033[38;5;141m'
        self.RESET = '\033[0m'

    async def spin(self):
        try:
            i = 0
            while True:
                frame = self.frames[i % len(self.frames)]
                elapsed_time = time.time() - self.start_time
                
                sys.stdout.write(
                    f"\r\033[K {self.CYAN}{frame}{self.RESET} "
                    f"{self.SILVER}{self.message}{self.RESET} "
                    f"{self.PURPLE}[{elapsed_time:.1f}s]{self.RESET}"
                )
                sys.stdout.flush()
                await asyncio.sleep(0.08)
                i += 1
        except asyncio.CancelledError:
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()

    def start(self):
        if self.task is None:
            self.start_time = time.time()
            self.task = asyncio.create_task(self.spin())

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

    @property
    def is_running(self):
        return self.task is not None


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def type_line(text: str, delay: float = 0.008):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()


def print_banner():
    clear_screen()

    CYAN = '\033[38;5;51m'
    PURPLE = '\033[38;5;141m'
    SILVER = '\033[38;5;250m'
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
    print(meta)
    type_line(tip, delay=0.004)


def cprint(text="", end="\n"):
    print_formatted_text(ANSI(str(text)), end=end)


async def async_main():
    print_banner()

    MAX_UI_WIDTH = 80  
    DIM_PURPLE_CODE = "\033[2m\033[38;5;141m"
    
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    
    current_provider = os.getenv("DEFAULT_PROVIDER", "aliyun")
    current_model = os.getenv("DEFAULT_MODEL", "glm-5")

    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as memory:
        app = create_agent_app(provider_name=current_provider, model_name=current_model, checkpointer=memory)
        config = {"configurable": {"thread_id": "local_geek_master"}}

        class SpinnerState:
            action_words = [
                "Thinking...",              
                "Working...",               
                "Beep boop...",             
                "Eating bugs...",           
                "Charging battery...",      
                "Brewing coffee...",        
                "Blinking lights...",       
                "Polishing pixels...",      
                "Scanning matrix...",       
                "Warming up circuits...",   
                "Syncing data...",          
                "Pinging server..."         
            ]
            current_words = [] 
            is_spinning = False
            start_time = 0
            frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            is_tool_calling = False 
            tool_msg = ""           

        spinner = SpinnerState()

        def get_safe_width():
            term_width = shutil.get_terminal_size().columns
            return max(10, min(MAX_UI_WIDTH, term_width - 1))

        def get_bottom_toolbar():
            w = get_safe_width()
            bottom_line = f"{DIM_PURPLE_CODE}{'━' * w}\033[0m"
            
            if not spinner.is_spinning:
                return ANSI(f"{bottom_line}\n ") 
            
            elapsed = time.time() - spinner.start_time
            if spinner.is_tool_calling:
                display_msg = spinner.tool_msg
            else:
                idx_word = int(elapsed) % len(spinner.current_words)
                display_msg = f"👾 {spinner.current_words[idx_word]}"

            idx_frame = int(elapsed * 12) % len(spinner.frames)
            frame = spinner.frames[idx_frame]
            
            spinner_text = f" \033[38;5;51m{frame}\033[0m \033[38;5;250m{display_msg}\033[0m \033[38;5;141m[{elapsed:.1f}s]\033[0m"
            return ANSI(f"{bottom_line}\n{spinner_text}")

        def get_dynamic_prompt():
            w = get_safe_width()
            top_line = f"{DIM_PURPLE_CODE}{'━' * w}\033[0m"
            return ANSI(f"{top_line}\n  \033[38;5;51m❯\033[0m ")

        async def agent_worker():
            while True:
                user_input = await task_queue.get()
                if user_input.lower() in ["/exit", "/quit"]:
                    task_queue.task_done()
                    break
                
                spinner.current_words = spinner.action_words.copy()
                random.shuffle(spinner.current_words)
                
                spinner.start_time = time.time()
                spinner.is_spinning = True
                spinner.is_tool_calling = False
                
                inputs = {"messages": [HumanMessage(content=user_input)]}
                try:
                    async for event in app.astream(inputs, config=config, stream_mode="updates"):
                        for node_name, node_data in event.items():
                            if node_name == "agent":
                                last_msg = node_data["messages"][-1]
                                
                                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                    for tc in last_msg.tool_calls:
                                        spinner.is_tool_calling = True
                                        spinner.tool_msg = f"唤醒内置工具 : {tc['name']}..."
                                        cprint(f"  ●\033[38;5;51m Tool Call: \033[0m{tc['name']}")
                                    cprint('')
                                        
                                elif last_msg.content:
                                    spinner.is_spinning = False
                                    
                                    lines = last_msg.content.strip().split('\n')
                                    if lines:
                                        formatted_out = f"  \033[38;5;141m❯\033[0m \033[38;5;250m{lines[0]}"
                                        for line in lines[1:]:
                                            formatted_out += f"\n    {line}"
                                        formatted_out += "\033[0m" 
                                        cprint(formatted_out)
                                    
                            elif node_name != "agent": 
                                spinner.is_tool_calling = False 
                                
                except Exception as e:
                    spinner.is_spinning = False
                    cprint(f"  \033[31m[ ⚠️ 引擎异常 : {e} ]\033[0m")

                spinner.is_spinning = False
                cprint() 
                task_queue.task_done()

        async def user_input_loop():
            custom_style = Style.from_dict({
                'bottom-toolbar': 'bg:default fg:default noreverse',
            })
            
            session = PromptSession(
                bottom_toolbar=get_bottom_toolbar,
                style=custom_style,
                erase_when_done=True  
            )
            
            async def redraw_timer():
                while True:
                    if spinner.is_spinning:
                        try:
                            get_app().invalidate()
                        except Exception:
                            pass
                    await asyncio.sleep(0.08)
                    
            redraw_task = asyncio.create_task(redraw_timer())
            
            while True:
                try:
                    with patch_stdout():
                        user_input = await session.prompt_async(get_dynamic_prompt)

                    user_input = user_input.strip()
                    if not user_input:
                        continue
                    
                    prefix = "  ❯ "
                    content_cols = get_cwidth(prefix) + get_cwidth(user_input)
                    w = get_safe_width()
                    
                    pad_len = max(2, w - content_cols)
                    padded_bubble = f"{prefix}{user_input}" + " " * pad_len
                    
                    cprint(f"\033[48;2;38;38;38m\033[38;5;255m{padded_bubble}\033[0m\n")
                    
                    await task_queue.put(user_input)
                    if user_input.lower() in ["/exit", "/quit"]:
                        cprint("  \033[38;5;141m✦ 记忆已固化，CyberClaw 进入休眠。\033[0m")
                        break
                        
                except (KeyboardInterrupt, EOFError):
                    cprint("\n  \033[38;5;141m✦ 强制中断，CyberClaw 进入休眠。\033[0m")
                    await task_queue.put("/exit")
                    break

            redraw_task.cancel() 

        worker = asyncio.create_task(agent_worker())
        await user_input_loop()
        await task_queue.join()
        worker.cancel()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()