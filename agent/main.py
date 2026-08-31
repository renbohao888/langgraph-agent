"""运行入口。

用法（在项目根目录 langgraph-agent/ 下执行）：
    python -m agent.main

需要先装依赖并把 API Key 填到 .env 里（参考 .env.example）。
"""
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .graph import build_agent
from .memory import get_checkpointer
from .tools import TOOLS


def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL") or None
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        print("❌ 还没配置 API Key。请把 .env.example 复制为 .env，并填入你的 Key。")
        return

    # 大脑：OpenAI 官方接口，也兼容 DeepSeek/通义千问/Moonshot 等
    # （只需在 .env 里设置 OPENAI_BASE_URL 和 OPENAI_MODEL）
    llm = ChatOpenAI(api_key=api_key, model=model, base_url=base_url, temperature=0)

    builder = build_agent(llm, TOOLS)

    checkpointer, conn = get_checkpointer()
    try:
        graph = builder.compile(checkpointer=checkpointer)
        print("=== Agent 已就绪（大脑 + 记忆 + 规划 + 工具） ===")
        print("输入一句话开始；输入 exit 退出。\n")
        config = {"configurable": {"thread_id": "demo-thread"}}

        while True:
            user = input("你: ").strip()
            if not user:
                continue
            if user in {"exit", "quit", "退出"}:
                break

            result = graph.invoke({"messages": [HumanMessage(content=user)]}, config=config)

            print("\n--- 规划 ---")
            for i, step in enumerate(result.get("plan", []), 1):
                print(f"{i}. {step}")
            print("--- Agent ---")
            print(result["messages"][-1].content)
            print()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
