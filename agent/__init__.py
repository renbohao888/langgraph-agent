"""一个基于 LangGraph 的简单 Agent 项目。

四模块对应关系：
- 大脑   : graph.py 中的 LLM（langchain_openai.ChatOpenAI）
- 记忆   : state.py（短期） + memory.py（长期，SQLite 持久化）
- 规划   : graph.py 中的 planner 节点
- 实施/工具: tools.py
"""
