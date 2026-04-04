import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cyberclaw.core.config import DB_PATH
from cyberclaw.core.context import trim_context_messages, AgentState
from cyberclaw.core.provider import get_provider
from cyberclaw.core.tools.builtins import BUILTIN_TOOLS
from cyberclaw.core.agent import create_agent_app

from langgraph.checkpoint.memory import MemorySaver
from cyberclaw.core.logger import audit_logger

def main():
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ 错误：未找到 OPENAI_API_KEY")
        return

    print("🚀 启动 CyberClaw 记忆压力测试 (引入 MemorySaver)...\n")

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    
    memory = SqliteSaver(conn)

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    current_provider = os.getenv("DEFAULT_PROVIDER", "aliyun")
    current_model = os.getenv("DEFAULT_MODEL", "glm-5")
    app = create_agent_app(provider_name=current_provider, model_name=current_model, checkpointer=memory)
    
    session_id = "test_user_lilei"
    config = {"configurable": {"thread_id": session_id}}

    test_conversations = [
        # "你好，我叫李雷，我是一名程序员。",
        # "我非常喜欢喝冰美式咖啡。",
        # "你能帮我算一下 25 乘以 48 等于多少吗？",
        # "我平时喜欢用 Python 写代码。",
        # "我周末打算去爬山。",
        # "我的幸运数字是 7。",
        # "现在几点了？",
        # "你还记得我叫什么名字、喜欢喝什么吗？",
        # "我刚才问了什么问题？"
        # "我非常喜欢打篮球"
        # "这周末天气好，适合做什么运动呢？"
        # "根据我的用户偏好，我喜欢什么编程语言呢"
        # "我叫什么名字？"
        # "下周一我想去游泳"
        # "我喜欢喝什么?"
        # 第 1 轮：告知偏好。观察目标 -> 是否触发 update_user_profile 工具调用？
        # "你好，我是王大锤。我是一名算法工程师，平时写代码卡壳的时候，我最喜欢喝一罐冰镇的无糖可乐来寻找灵感。你可以叫我锤哥。",
        
        # # 第 2 轮：闲聊干扰。消耗短期注意力。
        # "现在帮我写一个极简的 Python 函数：计算斐波那契数列的第 n 项。",
        
        # # 第 3 轮：终极测试！观察目标 -> 它是否能【瞬间】回答出可乐，且【绝对不】产生任何工具调用？
        # "代码写得不错。我现在遇到个大 Bug，卡了两个小时了。根据我的习惯，你建议我现在干点什么来回回血？"
        "我的职业是什么？"
    ]

    for i, user_input in enumerate(test_conversations, 1):
        print(f"\n[{i}/9] 👤 用户: {user_input}")
        print("-" * 50)

        audit_logger.log_event(
            thread_id=session_id,
            event="human_message",
            content=user_input
        )
        
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        for event in app.stream(inputs, config=config, stream_mode="updates"):
            for node_name, node_state in event.items():
                
                if "messages" in node_state:
                    latest_msg = node_state["messages"][-1]
                    if node_name == "agent" and latest_msg.type == "ai" and latest_msg.content:
                        print(f"🤖 CyberClaw: {latest_msg.content}")
                
                if "summary" in node_state:
                    print(f"\n🧠 [系统后台触发] 已生成/更新长期记忆档案:\n{node_state['summary']}\n")

    print("\n✅ 测试完成！正在通知后台日志线程安全退出...")
    audit_logger.shutdown()
    conn.close()

if __name__ == "__main__":
    main()