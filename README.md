# 一个基于 LangGraph 的 Agent 入门项目

这是一个**面向零基础、面向投递 Agent 开发岗位**的入门项目。
它把 Agent 的**四大核心模块**拆得清清楚楚，你改一改、跑一跑，就能变成**你自己的求职作品**。

> 底层框架：https://github.com/langchain-ai/langgraph （工业界最主流的 Agent 框架）

## 四模块对应关系

| 模块 | 对应文件 | 说明 |
|------|---------|------|
| 🧠 大脑（LLM） | `agent/graph.py`（`agent` 节点） | 负责理解、决策、生成。这里用 `langchain_openai.ChatOpenAI` |
| 💾 记忆（Memory） | `agent/state.py` + `agent/memory.py` | state 是短期记忆（对话累积），memory.py 用 SQLite 做长期持久化 |
| 🗺️ 规划（Planning） | `agent/graph.py`（`planner` 节点） | 先让模型把大目标拆成一步步计划 |
| 🔧 实施/工具（Tools） | `agent/tools.py` | 计算器、读写文件等真正“动手”的能力 |

工作流程（LangGraph 状态图）：
```
开始 → 规划 → 大脑决策 → (若调用工具) → 执行工具 → 回到大脑 → … → 输出答案 → 结束
```

## 环境要求

- Python 3.10+
- 一个可用的大模型 API Key（OpenAI / DeepSeek / 通义千问 / Moonshot 等，国内可用）

## 快速开始（三步）

```bash
# 1. 进入项目根目录
cd langgraph-agent

# 2. 安装依赖（建议用虚拟环境）
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt

# 3. 配置 Key 并运行
copy .env.example .env            # Windows；macOS/Linux 用 cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY（国内模型还要设 OPENAI_BASE_URL / OPENAI_MODEL）
python -m agent.main
```

运行后你会看到 `你:` 提示符，试试输入：
- `帮我算 (3+8)*2`
- `阅读 README.md`
- `记住我的喜好：我讨厌吃香菜`
- 再问 `我刚才让你记住什么？`（验证长期记忆，重启程序后仍然记得）

## 怎么把它变成“你自己的项目”

1. **改名字**：把 `agent/` 包名改成你喜欢的（比如 `my_agent/`），同步改 import。
2. **加工具**：在 `agent/tools.py` 里学着加一个函数并用 `@tool` 装饰，然后在 `TOOLS` 列表里注册。
3. **换大脑**：在 `.env` 里换模型；或在 `agent/graph.py` 里换 `SYSTEM_PROMPT` 为人设。
4. **写 README**：把上面的介绍改成你自己的话，讲清楚你的设计思路——面试时这就是你的加分项。

## 上传到你自己的 GitHub

```bash
git init
git add .
git commit -m "feat: 基于 LangGraph 的 Agent 入门项目"
# 在 GitHub 网页上新建一个空仓库，然后：
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

> 注意：`.env` 已被 gitignore 忽略，**不会**上传你的 Key，安全。

## 免责说明

- `tools.py` 里的 `calculator` 用 `eval` 但已过滤字符，仅用于教学**演示**。
  真正上生产的工具函数需要更严格的隔离（例如 Docker/E2B 沙箱）。
- 本仓库代码仅供学习，请勿在未受控环境运行不受信任的代码。
