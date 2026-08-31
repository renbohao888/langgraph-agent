"""实施/工具模块：Agent 可以“动手”调用的外部能力。

在 Agent 开发里，tools（工具）就是让模型真正去“做事”的手指。
模型（大脑）决定要不要调用某工具、传什么参数，这里负责真正执行。
"""
from langchain_core.tools import tool


@tool
def calculator(expression: str) -> float:
    """安全计算一个数学表达式，例如 '(3+5)*2'。"""
    # 只允许数字、运算符和括号，避免执行任意代码
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        raise ValueError("表达式包含非法字符：" + expression)
    return eval(expression, {"__builtins__": {}}, {})  # 已过滤输入，仅用于教学演示


@tool
def read_file(path: str) -> str:
    """读取一个文本文件的内容。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取失败：{e}"


@tool
def write_note(content: str) -> str:
    """把一段内容追加写入项目根目录的 notes.txt，用来演示“长期记忆”的能力。"""
    import os

    notes_path = os.path.join(os.getcwd(), "notes.txt")
    with open(notes_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")
    return "已保存到笔记"


# 注册给 Agent 的工具列表
TOOLS = [calculator, read_file, write_note]
