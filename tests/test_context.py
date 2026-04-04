import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cyberclaw.core.context import trim_context_messages
from typing import List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage

# 测试
def print_messages(prefix: str, msgs: List[BaseMessage]):
    """格式化打印消息列表"""
    print(f"{prefix} ({len(msgs)} 条):")
    for i, msg in enumerate(msgs):
        content = msg.content if len(msg.content) < 30 else msg.content[:27] + "..."
        if isinstance(msg, ToolMessage):
            print(f"  [{i}] {msg.__class__.__name__}(tool_call_id={msg.tool_call_id}): {content}")
        else:
            print(f"  [{i}] {msg.__class__.__name__}: {content}")
    print()


def run_test_case(name: str, messages: List[BaseMessage], trigger_turns: int = 1, keep_turns: int = 4):
    """运行单个测试用例，指定触发水位和保留回合数"""
    print("=" * 60)
    print(f"测试: {name} (trigger={trigger_turns}, keep={keep_turns})")
    print("-" * 60)

    print_messages("原始消息", messages)
    kept, discarded = trim_context_messages(messages, trigger_turns, keep_turns)
    print_messages("保留的消息", kept)
    print_messages("丢弃的消息", discarded)


# ---------- 测试用例 ----------
def main():
    # 1. 基本场景：系统消息 + 多轮对话，保留最近2个回合
    run_test_case(
        "基本场景 - 保留最近2回合",
        [
            SystemMessage(content="你是一个智能助手"),
            HumanMessage(content="你好"),
            AIMessage(content="你好！有什么可以帮助你的？"),
            HumanMessage(content="今天天气怎么样"),
            AIMessage(content="抱歉，我无法获取实时天气。"),
            ToolMessage(content="调用天气API失败", tool_call_id="1"),
            HumanMessage(content="那讲个笑话吧"),
            AIMessage(content="当然，这是一个笑话：..."),
        ],
        trigger_turns=8,   # 总是触发裁剪
        keep_turns=4,
    )

    # 2. 只有系统消息
    run_test_case(
        "只有系统消息",
        [SystemMessage(content="你是一个智能助手")],
        trigger_turns=8, keep_turns=4,
    )

    # 3. 没有系统消息，保留最近1个回合
    run_test_case(
        "没有系统消息 - 保留最近1回合",
        [
            HumanMessage(content="你好"),
            AIMessage(content="你好！"),
            HumanMessage(content="再见"),
            AIMessage(content="再见！"),
        ],
        trigger_turns=8, keep_turns=3,
    )

    # 4. 实际回合数少于 keep_turns，应保留所有
    run_test_case(
        "不足 keep_turns - 保留所有",
        [
            SystemMessage(content="你是一个助手"),
            HumanMessage(content="你好"),
            AIMessage(content="你好"),
        ],
        trigger_turns=8, keep_turns=4,   # 实际只有2回合（Human+AI算一个回合），但 keep_turns=4，所以保留全部
    )

    # 5. 连续两个 HumanMessage（没有 AI 回复）
    run_test_case(
        "连续 Human",
        [
            HumanMessage(content="你好"),
            HumanMessage(content="在吗？"),
            AIMessage(content="我在，请讲。"),
        ],
        trigger_turns=8, keep_turns=4,
    )

    # 6. 第一个非系统消息是 AIMessage（应被丢弃）
    run_test_case(
        "以 AI 开始",
        [
            SystemMessage(content="你是一个助手"),
            AIMessage(content="我是 AI，但我先说话了？"),
            HumanMessage(content="你好"),
            AIMessage(content="你好"),
        ],
        trigger_turns=8, keep_turns=4,
    )

    # 7. 一个回合内有多条 AI 和 Tool 消息，保留最近1个回合
    run_test_case(
        "单回合多 AI/Tool - 保留最近1回合",
        [
            SystemMessage(content="你是一个助手"),
            HumanMessage(content="调用工具A"),
            AIMessage(content="正在调用..."),
            ToolMessage(content="工具A返回结果1", tool_call_id="2"),
            AIMessage(content="结果处理中"),
            ToolMessage(content="工具A返回结果2", tool_call_id="3"),
            AIMessage(content="最终结果：成功"),
            HumanMessage(content="好的，谢谢"),
            AIMessage(content="不客气"),
        ],
        trigger_turns=8, keep_turns=4,
    )

    # 8. 混合多轮，保留最近3个回合
    run_test_case(
        "混合多轮 - 保留最近3回合",
        [
            SystemMessage(content="你是一个助手"),
            HumanMessage(content="第一轮"),
            AIMessage(content="回复1"),
            HumanMessage(content="第二轮"),
            AIMessage(content="回复2"),
            ToolMessage(content="工具消息2", tool_call_id="4"),
            HumanMessage(content="第三轮"),
            AIMessage(content="回复3"),
            HumanMessage(content="第四轮"),
            AIMessage(content="回复4"),
            HumanMessage(content="第五轮"),
            AIMessage(content="回复5"),
        ],
        trigger_turns=4, keep_turns=3,
    )

    # 9. 空消息列表
    run_test_case("空列表", [], trigger_turns=1, keep_turns=4)

    # 10. 只有系统消息（重复）
    run_test_case("仅系统", [SystemMessage(content="系统消息")], trigger_turns=1, keep_turns=4)

    # ===== 新增测试用例：测试 trigger_turns 阈值行为 =====
    # 11. 总回合数小于 trigger_turns，不裁剪
    messages_11 = [
        SystemMessage(content="助手"),
        HumanMessage(content="第一轮"),
        AIMessage(content="回复1"),
        HumanMessage(content="第二轮"),
        AIMessage(content="回复2"),
    ]  # 总回合数 = 2
    run_test_case(
        "总回合数小于 trigger (2 < 3) - 不裁剪",
        messages_11,
        trigger_turns=3, keep_turns=1,  # trigger=3 > 2，应保留全部
    )

    # 12. 总回合数等于 trigger_turns，触发裁剪
    messages_12 = [
        SystemMessage(content="助手"),
        HumanMessage(content="第一轮"),
        AIMessage(content="回复1"),
        HumanMessage(content="第二轮"),
        AIMessage(content="回复2"),
        HumanMessage(content="第三轮"),
        AIMessage(content="回复3"),
    ]  # 总回合数 = 3
    run_test_case(
        "总回合数等于 trigger (3 == 3) - 触发裁剪，保留最近1回合",
        messages_12,
        trigger_turns=3, keep_turns=1,  # 应保留最后一个回合（第三轮及其AI回复）
    )

    # 13. 总回合数大于 trigger_turns，触发裁剪，保留最近2回合
    messages_13 = [
        SystemMessage(content="助手"),
        HumanMessage(content="第一轮"),
        AIMessage(content="回复1"),
        HumanMessage(content="第二轮"),
        AIMessage(content="回复2"),
        HumanMessage(content="第三轮"),
        AIMessage(content="回复3"),
        HumanMessage(content="第四轮"),
        AIMessage(content="回复4"),
    ]  # 总回合数 = 4
    run_test_case(
        "总回合数大于 trigger (4 > 3) - 触发裁剪，保留最近2回合",
        messages_13,
        trigger_turns=3, keep_turns=2,  # 应保留第三、四轮
    )


if __name__ == "__main__":
    main()