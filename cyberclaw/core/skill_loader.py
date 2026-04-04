import os
import re
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from .config import SKILLS_DIR
from .tools.sandbox_tools import execute_office_shell


class DynamicSkillInput(BaseModel):
    mode: str = Field(
        description="必须是 'help' 或 'run'。第一次使用时强烈建议先传入 'help' 阅读说明书。"
    )
    command: Optional[str] = Field(
        default="", 
        description="仅在 mode='run' 时需要。你要执行的完整命令，保留 {baseDir} 占位符。"
    )

def load_dynamic_skills() -> List[StructuredTool]:
    loaded_skills = []
    
    if not os.path.exists(SKILLS_DIR):
        return loaded_skills

    for item in os.listdir(SKILLS_DIR):
        folder_path = os.path.join(SKILLS_DIR, item)
        if not os.path.isdir(folder_path):
            continue

        md_path = os.path.join(folder_path, "SKILL.md")
        if not os.path.exists(md_path):
            md_path = os.path.join(folder_path, "README.md")
        
        if not os.path.exists(md_path):
            continue

        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
            desc_match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)

            raw_name = name_match.group(1).strip() if name_match else item
            tool_name = re.sub(r'[^a-zA-Z0-9_-]', '_', raw_name)
            
            raw_desc = desc_match.group(1).strip() if desc_match else f"提供 {raw_name} 相关功能"
            if (raw_desc.startswith('"') and raw_desc.endswith('"')) or (raw_desc.startswith("'") and raw_desc.endswith("'")):
                raw_desc = raw_desc[1:-1]

            mini_description = (
                f"{raw_desc}\n\n"
                f"注意：这是一个外部扩展技能。首次使用请务必先传入 `mode='help'` 来阅读完整说明书，之后再使用 `mode='run'` 配合 `command` 执行底层脚本。"
            )

            def create_skill_runner(skill_folder_name: str, md_content: str):
                def runner(mode: str, command: str = "") -> str:
                    if mode == "help":
                        return (
                            f"========== 【{skill_folder_name} 完整说明书】 ==========\n"
                            f"{md_content[:3000]}\n"
                            f"====================================\n"
                            f"提示：请根据以上说明，如果觉得能解决问题，就将 mode 设为 'run'，并将拼装好的执行命令填入 command 重新调用。否则就尝试其他工具，没有其他合适工具就老实跟用户说"
                        )
                    elif mode == "run":
                        if not command:
                            return "错误：在 'run' 模式下，必须提供 command 参数！"
                        
                        actual_cmd = command.replace("{baseDir}", f"skills/{skill_folder_name}")
                        return execute_office_shell.invoke({"command": actual_cmd})
                    else:
                        return "错误：mode 参数只能是 'help' 或 'run'。"
                return runner

            dynamic_tool = StructuredTool.from_function(
                func=create_skill_runner(item, content),
                name=tool_name,
                description=mini_description,
                args_schema=DynamicSkillInput
            )
            loaded_skills.append(dynamic_tool)

        except Exception as e:
            print(f" \033[38;5;196m[警告] 技能包 {item} 加载失败: {e}\033[0m")
            
    return loaded_skills