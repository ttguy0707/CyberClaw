import os
import sys
import time


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

    try:
        user_input = input(" \033[38;5;51m❯\033[0m \033[38;5;250m你\033[0m > ")
        print(f"\n \033[38;5;213m◆\033[0m \033[38;5;141m收到指令\033[0m: {user_input}")
        print(" \033[38;5;51m◆\033[0m 正在接入核心推理引擎...\n")
    except KeyboardInterrupt:
        print("\n \033[38;5;141m✦ 会话已中断，CyberClaw 进入休眠。\033[0m")


if __name__ == "__main__":
    main()