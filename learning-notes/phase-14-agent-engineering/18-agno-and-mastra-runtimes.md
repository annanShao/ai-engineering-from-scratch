# Lesson 18 · Agno 与 Mastra:轻量 Runtime

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/18-agno-and-mastra-runtimes/` |
| 类型 | Concept(comparative)· ~60 分钟 |
| 前置 | L13-L17(框架五家光谱) |
| 关键文件 | `docs/en.md`、`code/main.py`(Agno-shaped vs Mastra-shaped 并排 toy) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/18-agno-and-mastra-runtimes/docs/en.md |
| 状态 | ✅ 完成(框架篇 coda + 价值分层模型(第 6 把尺子)+ agent loop 内核拆解 + 3/3 体检 + 4 金句) |

---

## 这节课的真定位:框架篇的 coda + 第 6 把尺子

L13-L17 是"重型框架巡演",L18 是"如果你不想要重型框架,这俩给你"。**它不是教新机制(没有),是教 taste——『不是每个 agent 都得用 LangGraph』**。同时这节逼出了第 6 把尺子:**"价值分层"——该爬到栈的哪一层**。

---

## 核心金句

### #1 · 价值分层模型(第 6 把尺子,本节最大收获)
> **从裸 REST 到重型框架是一个 6 层栈,每往上一层用『灵活性 + 学习成本 + 锁定』换『少写的代码』。唯一无条件该升的是 Layer 0→1;其余每跳都要先掏出痛点才有资格升。**

| Layer | 写什么 | 替你做什么 | 何时升 |
|---|---|---|---|
| 0 裸 REST | `requests.post` | 啥都不做 | 只在没 SDK 的环境 |
| 1 Client SDK(openai/anthropic) | `client.messages.create` | 重试/流式/类型/鉴权/error 分类 | **几乎无条件该用** |
| 2 轻量 Runtime(Agno/Mastra) | `Agent(tools).run()` | **agent loop** + model router + 多模态 + 性能 | 要 tool use/多轮 |
| 3 Agent SDK(OpenAI/Claude) | `Runner.run(agent)` | + handoff/guardrail/session/subagent/hook | 要这些原语,认一家 provider |
| 4 重型框架(LangGraph/CrewAI/AutoGen) | graph/crew/actor | + 显式编排/durable state/多 agent 拓扑 | 要 durable/graph/多 agent |
| 5 Workflow Engine(Temporal+agent) | workflow+activity | + 工业级 exactly-once/分布式 | 跨天长跑/严格副作用 |

**"裸 REST → Client SDK 是整个栈里唯一『几乎无条件该升』的一跳——它换来的是『你自己一定写得更烂』的基础设施(429 退避/流式 SSE/超时/error 类型化)。Client SDK → 任何更高层全部是有条件的,条件就是你的需求复杂度。正确默认姿势:从 Layer 1 起步,只在撞到具体痛点时才往上爬一层。"**

### #2 · 轻量 runtime 的"轻"轻在哪:不替你拥有长期 memory + 不给你 graph
> **轻量 runtime = L01 ReAct loop + tool registry,写成高性能库,memory 和编排都甩给你。**

- **Messages 处理**:✅ loop 内核(append/role 标注/tool result 塞回,就是那个 while 循环本身)
- **Memory(长期)**:❌ 不在内核,是可选挂件——**Agno 倾向甩给你的 DB(stateless session-scoped FastAPI,每请求起新 agent,session state 进 DB),Mastra 给原语但要配 backend**
- **默认模式**:**agent-tool-use(= L01 ReAct)**,模型在 loop 里自己决定调哪个 tool;**没有内建 router/supervisor/handoff**
- **要 multi-agent**:你手写(tool-as-agent = 手写版 L16 handoff;或代码层 router = 手写版 L12 Routing)

**"轻量 runtime 的『轻』,很大程度轻在它不替你拥有长期 memory,也不给你一等公民 graph——它管好『一次 run 里的 messages 循环』,把跨 run 记忆和控制流编排都甩给你。这是它『快』的原因,也是它『轻』的代价。"**

### #3 · Agno = 纯 ReAct 零编排;Mastra = ReAct + 轻量 Workflows
| | Agno | Mastra |
|---|---|---|
| 语言 | Python(原 Phi-data) | TypeScript(Vercel AI SDK 之上) |
| 哲学 | "No graphs, chains — just pure python" | TS-first + Vercel/Next.js 深嵌 |
| 性能 | **~2μs 实例化 / ~3.75 KiB/agent / 23 providers** | — |
| 部署 | stateless session-scoped FastAPI | Express/Hono/Fastify/Koa + Next.js/Astro |
| 杀器 | 原生多模态 + agentic RAG | **Unified Model Router 3,300+ 模型/94 providers** + Mastra Studio(localhost:4111 调试 UI) |
| 编排 | 纯 single-agent tool use,零编排 | + Workflows 原语(轻量编排) |

### #4 · 性能崇拜是 framework 圈最常见的判断错误
> **Agno 的 2μs 不是用来吹的,是给特定场景(多短命 agent 高并发:chat fan-in / eval pipeline / API 每请求起新 agent)的工具。其他场景(单 agent 跑 10 分钟)瓶颈是 LLM call 不是实例化,这数字基本不重要。**

每一项轻量 runtime 的优势都挂着"只有你需要 X 才有价值"的条件,**没有一项是无条件净赚**。这跟 Layer 1 Client SDK 形成对比——后者是唯一无条件的。

**Multi-model router 看穿一层**:Mastra 的 3300 不是它写了 3300 个 adapter,是它**继承 Vercel AI SDK 整个 provider 生态**——"多 model"的真实含义是"生态借力";评估时问的不是"支持几个模型",是"provider 生态由谁维护、更新够不够快"。

**Mastra Studio 同源 L17 harness-first**:框架不只给 SDK 抽象,给一个**实际能用的工具/界面**——Mastra Studio 之于 Mastra ≈ Claude Code 之于 Claude SDK。

---

## 关键概念地图

**agent loop 内核(任何轻量 runtime 帮你写好的样板)**:
```python
messages = [{"role":"user","content":input}]
while True:
    resp = llm.call(messages, tools=tools)   # 调 LLM
    messages.append(resp)                     # append(messages 处理)
    if resp.tool_calls:
        for tc in resp.tool_calls:
            messages.append(exec_tool(tc))    # tool result 塞回(messages 处理)
        continue
    return resp.content                       # 没 tool 调用 = 完成
```
→ **Agno 相对裸 REST 的核心增值就是这个 while 循环 + tool_call parse/execute/append。**

**何时选(taste 决策表):**
- Agno —— Python 后端,FastAPI,大量短命 agent,强 perf 要求
- Mastra —— TS 后端,Next.js/Vercel,多 provider 路由,Zod-typed tools
- LangGraph —— durable state + explicit graph 比速度重要
- OpenAI/Claude SDK —— 要 provider 产品化 shape
- 客户端 SDK —— 单 agent loop 啥都不要

**3 个翻车点:**

| 翻车 | 避法 |
|---|---|
| Perf-for-perf's-sake(选 Agno 因为"2μs 好快"但 workload 是 10s/对话) | 先 profile,实例化不是瓶颈就别看这数 |
| Ecosystem lock-in(Mastra Vercel 集成在别处变负担) | 明确部署目标再选 |
| Enterprise license 混淆(Mastra `ee/` 是 source-available 非 Apache 2.0) | fork 前必读 license |

**"L13-L18 六节框架课不是让你记住六个 framework 怎么用,是让你学会回答一个判断题:给定我的 stack、规模、合规、speed budget,这个项目该用哪一家?为什么不是其他五家?——能讲出『为什么不是』的工程师,比能讲出『为什么是』的值钱十倍。"**

---

## 体检 · 3/3 ✅

| # | 题 | 答 | 点评 |
|---|---|---|---|
| Q1 | Agno 2μs 在哪类场景值钱 | C(大量短命 agent 高并发) | 没被"性能越快越好"带走 |
| Q2 | Mastra Studio 同源哪节哲学 | D(L17 harness-first) | 看穿"给工具不只给抽象" |
| Q3 | TS/Next.js/Vercel + 多 provider + 调试 UI 选什么 | C(Mastra) | 三信号叠加精准 |

---

## 手做记录

`code/main.py` 是 Agno-shaped vs Mastra-shaped 并排 toy(同功能不同结构两个 trace)。**未额外跑**——概念已通过价值分层模型 + agent loop 内核拆解完全消化。

### 留给后续的钩子
- **🎉 框架篇(L13-L18)正式收尾**;L19+ 切到"运营"(评测 / observability / security / production)。
- **第 6 把尺子(价值分层)** 加入工具箱:看任何 agent 项目先问"它在栈的哪一层、该不该升"。
- **L24 observability** 会再碰 Agno/Mastra 的 Langfuse/Phoenix/Opik 集成。
- 出师三题(L01-L18 验收)仍挂着,可随时做。
