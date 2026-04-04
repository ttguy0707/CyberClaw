import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cyberclaw.core.agent import create_agent_app

def main():
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: 未找到 OPENAI_API_KEY，请检查项目根目录的 .env 文件！")
        return

    print("初始化 CyberClaw 核心引擎...")
    
    app = create_agent_app(provider_name="aliyun", model_name="glm-5")
    
    print("CyberClaw 启动完毕！你可以开始提问了。(输入 'quit' 或 'q' 退出)")
    print("-" * 50)

    state = {"messages": []}

    while True:
        user_input = input("\n[你]: ")
        if user_input.lower() in ['quit', 'q', 'exit']:
            print("再见，CyberClaw 下线！")
            break
        
        if not user_input.strip():
            continue

        # 把用户的输入包装成 LangChain 标准消息，塞进状态托盘
        state["messages"].append(HumanMessage(content=user_input))

        print("\n[CyberClaw 思考中...]")
        
        # 使用 stream_mode="updates" 可以让我们精准捕捉到每个节点运行后的增量状态
        for event in app.stream(state, stream_mode="updates"):
            
            # 遍历当前事件中所有执行完毕的节点 (通常一次只有一个)
            for node_name, node_state in event.items():
                print(f"⚙️ 节点: '{node_name}' 执行完毕")
                
                # 获取该节点刚刚产出的最新一条消息
                latest_message = node_state["messages"][-1]
                
                if node_name == "agent":
                    # 检查大模型是不是下发了工具调用指令
                    if latest_message.tool_calls:
                        tool_call = latest_message.tool_calls[0]
                        print(f"🛠️ 决策: 准备调用工具 [{tool_call['name']}]")
                        print(f"📥 参数: {tool_call['args']}")
                    elif latest_message.content:
                        # 如果没有调用工具，且有文本内容，说明大模型给出了最终回答
                        print(f"\n🤖 [CyberClaw]: {latest_message.content}")
                        
                elif node_name == "tools":
                    # 打印工具执行返回的原始结果
                    print(f"✅观察: 工具返回结果 -> {latest_message.content}")
        
        
if __name__ == "__main__":
    main()