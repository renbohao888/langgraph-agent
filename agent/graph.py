"""组装 Agent：把 大脑 + 记忆 + 规划 + 工具 串成一张“状态图”。

LangGraph 用“图”来表示 Agent 的工作流程：
  开始 → 规划(planning) → 大脑决策(agent) → 若调用工具→执行工具(tools) → 回到大脑… 
  当大脑不再调用工具，就输出最终回答，结束。

- planner 节点 = 规划模块
- agent 节点   = 大脑（LLM），负责判断该说话还是该调用工具
- tools 节点   = 实施/工具模块
- StateGraph 自带的消息累积 = 短期记忆；外部 SQLite checkpointer = 长期记忆
"""
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .state import AgentState

SYSTEM_PROMPT = (
    "你是一个乐于助人的 AI 助手，可以使用工具完成任务。"
    "请用中文回答。如果用户没有明确要求，尽量简洁。"
)


def build_agent(model, tools: List) -> StateGraph:
    """构建并返回可编译的 Agent 图。"""
    tool_node = ToolNode(tools)
    llm_with_tools = model.bind_tools(tools)

    def planner(state: AgentState) -> dict:
        """规划模块：先让大脑给出执行步骤（不调用工具）。"""
        last_user = state["messages"][-1].content if state["messages"] else ""
        plan_prompt = SystemMessage(
            "你是任务规划器。请用中文列出完成用户目标的具体步骤，每行一步，只列步骤，不要执行。"
        )
        plan_resp = model.invoke([plan_prompt, HumanMessage(content=str(last_user))])
        steps = [s.strip() for s in str(plan_resp.content).splitlines() if s.strip()]
        return {"plan": steps or ["（规划为空）"]}

    def agent(state: AgentState) -> dict:
        """大脑：基于当前记忆（messages）决定是回答还是调用工具。"""
        msgs = [SystemMessage(content=SYSTEM_PROMPT)] + list(state["messages"])
        response = llm_with_tools.invoke(msgs)
        return {"messages": [response]}

    builder = StateGraph(AgentState)
    builder.add_node("planner", planner)
    builder.add_node("agent", agent)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "agent")
    # 如果大脑最后一条消息含着工具调用 → 去 tools；否则结束
    builder.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "agent")

    return builder
