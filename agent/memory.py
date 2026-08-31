"""记忆模块之二：长期记忆（持久化）。

短期记忆（状态里的 messages）只活在一次运行里。要想让 Agent “记得”
上一次聊了什么，就需要把状态保存起来。这里用 SQLite 做一个简单的
checkpointer：每次对话结束都把状态写进数据库，下次运行再读出来。

这就是 LangGraph 的“持久化执行 / 长期记忆”机制。
"""
import os
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

# 数据库文件放在项目根目录（agent 包的上一级）
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agent_memory.sqlite")


def get_checkpointer() -> tuple[SqliteSaver, sqlite3.Connection]:
    """创建一个带 SQLite 持久化的 checkpointer，供图编译使用。"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return SqliteSaver(conn), conn
