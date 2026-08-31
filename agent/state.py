"""记忆模块之一：状态（State）。

在 Agent 里，“记忆”的本质就是一份随对话不断更新的“状态”。
LangGraph 把这份状态当成图节点之间传递、累积的数据。

这里定义了两类记忆：
- messages：短期记忆。用 add_messages 累加，会自动保留历史对话，
  模型据此知道“我们聊到哪里了”。
- plan：规划模块的结果（LLM 生成的步骤计划），也放进状态里。
"""
from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # 短期记忆：对话消息列表（会自动累积、按 id 去重）
    messages: Annotated[List[BaseMessage], add_messages]
    # 规划模块产物：LLM 给出的执行步骤
    plan: List[str]
