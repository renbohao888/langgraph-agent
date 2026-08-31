"""把 Agent 包装成一个 Web 服务（Flask）。

这就是把 Agent 变成“能给别人用的后端”：浏览器/接口都能调它。
你熟悉的 Flask 这里都用上了：路由、装饰器、request、jsonify。

用法（在项目根目录 langgraph-agent/ 下执行）：
    .venv\\Scripts\\python app.py
然后浏览器打开  http://127.0.0.1:5000/
"""
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from agent.graph import build_agent
from agent.memory import get_checkpointer
from agent.tools import TOOLS

load_dotenv()

app = Flask(__name__)

_api_key = os.getenv("OPENAI_API_KEY", "").strip()
_base_url = os.getenv("OPENAI_BASE_URL") or None
_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_llm = ChatOpenAI(api_key=_api_key, model=_model, base_url=_base_url, temperature=0)
_builder = build_agent(_llm, TOOLS)
_checkpointer, _conn = get_checkpointer()
_graph = _builder.compile(checkpointer=_checkpointer)

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>我的 Agent</title>
<style>body{font-family:sans-serif;max-width:680px;margin:40px auto}
input{padding:8px;width:70%}button{padding:8px 16px}
#plan{color:#555;white-space:pre-line;margin-top:12px}
#out{background:#f5f5f5;padding:12px;border-radius:8px;white-space:pre-wrap}</style>
</head><body>
<h2>我的 LangGraph Agent</h2>
<input id="msg" placeholder="输入问题，例如：帮我算 (3+8)*2" size="55">
<button onclick="send()">发送</button>
<div id="plan"></div><pre id="out"></pre>
<script>
async function send(){
  const msg = document.getElementById('msg').value;
  const res = await fetch('/chat', {method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:msg})});
  const data = await res.json();
  const plan = (data.plan||[]).map((s,i)=>`${i+1}. ${s}`).join('\\n');
  document.getElementById('plan').innerText = '规划：\\n' + plan;
  document.getElementById('out').innerText = '回答：\\n' + data.answer;
}
</script></body></html>"""


@app.route("/", methods=["GET"])
def index():
    return PAGE


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user = str(payload.get("message", "")).strip()
    thread = str(payload.get("thread_id", "default"))
    if not user:
        return jsonify({"error": "message 不能为空"}), 400
    result = _graph.invoke(
        {"messages": [HumanMessage(content=user)]},
        config={"configurable": {"thread_id": thread}},
    )
    return jsonify(
        {"plan": result.get("plan", []), "answer": result["messages"][-1].content}
    )


if __name__ == "__main__":
    print("✅ 启动成功！浏览器打开: http://127.0.0.1:5000/")
    app.run(host="127.0.0.1", port=5000, debug=True)
