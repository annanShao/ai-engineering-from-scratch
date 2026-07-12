# Lesson 17 · Claude Agent SDK:Subagents 与 Session Store

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/17-claude-agent-sdk/` |
| 类型 | Build · ~75 分钟 |
| 前置 | L13-L16(四家框架对照里的最后一块拼图) |
| 关键文件 | `docs/en.md`、`code/main.py`(stdlib SDK shape) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/17-claude-agent-sdk/docs/en.md |
| 状态 | ✅ 完成(四家光谱收口 + harness-first 哲学 + 5 组件 + Temporal sidebar 拉满 + 3/3 体检 + 4 金句) |

---

## 这节课的真定位:四家光谱的最后一块拼图

L13/L14/L15/L16 一路推过来后,L17 用一个**反方向**收尾——前三家(LangGraph/CrewAI/OpenAI SDK)都是"先有 SDK 你拿它建 app",Claude SDK 是"**先有一个用得很爽的 app(Claude Code),把它的 harness 抽出来给你**"。**身份证明就是它自己存在**——你打开 Claude Code 就在 work。

---

## 核心金句

### #1 · 四家光谱的最终对比

| | LangGraph | CrewAI | OpenAI SDK | **Claude SDK** |
|---|---|---|---|---|
| 起点 | 从原语开始,你拼 | 从原语开始,你拼 | 从原语开始,SDK 帮你管 | **从一个已经在跑的 app 开始,SDK 是它的内脏** |
| 中心哲学 | state-first | role-first | handoff-first | **harness-first** |
| 内置 tool | 0 | 几个 toolkit | function-tool 架子 | **10+ 全套(read/write/bash/grep/glob/web…)** |
| 钩子 / 拦截 | 自己 wrap | 没原生 | guardrail(3 点位) | **8 种 hook 生命周期点位** |
| Session | 自己写 checkpointer | Flow state | `Session` 一行 | **CLI-grade(list/load/append/delete/list_subkeys/--session-mirror)** |
| 是不是"battle-tested" | 看你用什么 backend | 看你 Crew 设计 | OpenAI 自家产品 | **就是 Claude Code 在用的同一套** ⭐ |

**"前三家是『拿原语去拼一个 agent』,Claude SDK 是『拿一个已经在生产跑两年的 agent 把它拆开给你』。这是这一相唯一一个**身份证明就是它自己存在**的 SDK。"**

### #2 · Built-in tools = Anthropic 帮你做了 80% 的 tool curation
> **内置 tool 不是 SDK 的『卖相』,是 Anthropic 帮你**预先做了 tool curation**。这一相反复讲『tool 设计是 agent 工程的核心』——Claude SDK 把这件事的 80% 工作量替你做完,你只需要为业务专属事写 custom tool。**

10+ tool:`read_file / write_file / edit_file / list_dir / grep / glob / bash / web_fetch / notebook_edit / task(spawn subagent) ...`——按 L06 "tool 要专、不要 generic `run_shell`" 原则,Claude Code 两年迭代出的"通用任务最小够用集"。

### #3 · Subagent 的两个用途 + context isolation = L07 的"进程级"兑现
**Anthropic 文档原话两用途:**
1. **Parallelization** —— 独立工作并发(20 微服务并发分析)
2. **Context isolation** —— subagent 用**自己**的 context window,**只把结果返回给 orchestrator**;主 agent 的 budget 被保住

**这就是 L07 MemGPT 思想的"进程级"兑现:**

| L07 MemGPT | L17 Subagent |
|---|---|
| page-in/page-out 一段记忆 | 把整段独立工作完全圈在另一个进程的 window 里 |
| 主 agent 看到摘要 | 主 agent 看到 subagent 返回的最终结果 |

新加 API:`list_subagents()`, `get_subagent_messages()` 可读 subagent transcript。

### #4 · Hooks 8 点位 = harness-first 哲学的红利
> **OpenAI SDK 的 guardrail 只挂 3 个点位(input/output/tool);Claude SDK hook 挂 8 个,且包括 `PreCompact` 这种很底层的点——只有真的在跑 long-context agent 才知道这里需要钩。这是 harness-first 的红利:Claude SDK 暴露的生命周期点位是**实际生产用过的**点位,不是设计出来的点位。**

8 个 hook 点位:`PreToolUse / PostToolUse / SessionStart / SessionEnd / UserPromptSubmit / PreCompact / Stop / Notification`。

**Hooks 是『不改 SDK 源码就能注入横切关注』的能力——logging / rate-limit / policy 检查 / 自定义 telemetry / prompt 改写都能挂。这是 L23 (OTel) 和 L27 (security) 那些"跨多个 agent 都要做的同一件事"的工程实现位。**

---

## Sidebar · Temporal:分布式工程师 10 年前解决了 L13 的痛点

> **Temporal = durable workflow engine,runtime 保证业务逻辑崩了能从**精确到「上一个未完成的副作用调用」**的位置接着跑。**

**对照 L13 那 5 个 checkpoint 颗粒——Temporal 给你颗粒 ④(activity 级):**

| | LangGraph | Temporal |
|---|---|---|
| Checkpoint 颗粒 | ③ Node | ④ **Activity**(每次副作用) |
| 你要写 | state schema + 幂等 tool | **什么都不写,runtime 全包** |
| Stripe 例子崩了重跑 | 扣两次(除非加 idempotency key) | **不会被扣两次,Temporal 自动跳过** |
| 代价 | 一张 Postgres 表 | **一个 Temporal server 集群**(或 Temporal Cloud ~$200/月起) |

**核心魔法**:Temporal 记录每次 activity 调用 + 返回值进 event history;崩溃后**重放** workflow code,跑到已记录的 activity **跳过实际调用、返回记录结果**——只重跑没完成的那个。

**致命约束**:workflow 函数必须 deterministic(`time.now()`、`random()`、HTTP、LLM 都要包成 activity)。 **LLM 调用塞进 activity 后,event history 记 `(prompt, response)`,重放时回放——LLM 调用被人为变成可重放**。

**2026 emerging 趋势**:大公司(Stripe / Snap / Coinbase)把**长跑 agent 整体塞进 Temporal workflow**——agent 行为 + 工业级 durability + exactly-once 副作用免费 + 分布式调度免费 + event history 天然 audit trail。 **「agent loop 整体写在 workflow engine 里,LLM 是其中一个 activity」是 2026 agent on production 的 emerging best practice**,L29 会再撞到。

**送你的一句:"你 L13 学的 checkpointer 是 agent 圈刚开始尝试做的 durability;Temporal 是分布式系统圈做了 10 年的 durability。 两者会合流——不会是 LangGraph 学着做 Temporal,是 agent loop 整体被塞进 Temporal。 你的 L13 mental model 是这个合流的入场券。"**

---

## 关键概念地图

**5 个核心组件:**

| 组件 | 是什么 | 类比 |
|---|---|---|
| Built-in tools(10+) | read/write/bash/grep/glob/web_fetch/task… | Anthropic 帮你做了 80% tool curation |
| Subagent(Task tool) | parallelization + context isolation | L07 MemGPT 的进程级兑现 |
| Session store | append/load/list/delete/list_subkeys/--session-mirror | 对话+执行 transcript 全套可审计 |
| Hooks(8 点位) | 不改 SDK 源码注入横切关注 | L23 OTel + L27 security 的实现位 |
| W3C trace context | OTel span 跨进程传播,subagent 自动归到同一个 trace | 分布式可观测性 SDK 层兑现 |

**Client SDK vs Agent SDK:**
- `anthropic` = 原始 Messages API,你拥有 loop/tools/state
- `claude-agent-sdk` = Claude Code 那一整套 loop 当库

**Claude Managed Agents(beta `managed-agents-2026-04-01`)**:Anthropic 托管选项,长跑异步 + prompt caching + 内置 compaction,用控制权换托管基建。 **Claude SDK ≈ 自起 PostgreSQL;Managed Agents ≈ Anthropic 给你 RDS。**

**3 个翻车点:**

| 翻车 | 修法 |
|---|---|
| Subagent over-spawn(100 微任务起 100 subagent,启动 overhead 比工作还多) | batch(一个 subagent 干 10 件事) |
| Hook creep(每个团队加 hook,启动膨胀,相互依赖) | 每季 review,删过期 |
| Session bloat(累积无清理) | `list_sessions` + 过期策略 |

**用尺子收口:**

| Claude SDK 部件 | 性质 | 对应 |
|---|---|---|
| 内置 tool 集 | 外部 tool curation 替你做了 80% | L06 tool 设计经验固化 |
| Subagent + context isolation | 外部 context budget 管理 | L07 MemGPT + L09 Mem0 工业版 |
| Session store | 外部对话+执行 transcript | L13 checkpointer 表亲(粒度不同) |
| Hooks(8 点位) | 外部横切关注注入 | L23 OTel + L27 security 钩子的实现位 |
| W3C trace context | 外部分布式可观测性 | L23 标准化兑现 |

**"Claude SDK 是这一相『内化 vs 外部』这把尺子用得**最极致**的框架——它把『LLM 之外几乎所有 agent 工程的脏活』都内置成默认行为:tool curation、context isolation、hook 点位、session、tracing。 哲学也最直接:**『你看 Claude Code 跑得好,你就拿同一套去做你的 agent』**。这不是设计上的优雅,这是『工程上的偷懒——而且是最聪明的那种偷懒』。"**

---

## 体检 · 3/3 ✅

| # | 题 | 答 | 点评 |
|---|---|---|---|
| Q1 | Subagent context isolation 同源哪节 | B(L07 MemGPT 的进程级兑现) | 锁定根因 |
| Q2 | Claude SDK 8 hook vs OpenAI 3 guardrail 根本原因 | B(harness-first 的红利——暴露实际生产用过的点位) | 看穿"暴露 vs 设计"的差别 |
| Q3 | 内部 DevOps agent 选什么 | D(Claude SDK——10+ tool 覆盖 git/grep/bash + subagent 并发 + PreToolUse audit + 团队已有肌肉记忆) | 包括"团队已有肌肉记忆"这个**非技术**因素 |

---

## 手做记录

`code/main.py` 实现 stdlib SDK shape(Tool/Registry + Subagent + SessionStore + Hooks + 3 subagent 并发 demo)。**未额外跑**——概念已通过四家光谱对比 + Temporal sidebar 完全消化。

### 留给后续的钩子
- **L18 Agno / Mastra**:轻量 runtime 风格,与 L13-L17 重型框架对比收尾
- **L23 Observability** + L27 Security:Claude SDK hooks 是这两节工程实现位的早到预告
- **L29 Production Runtimes**:Temporal sidebar 那个"agent 塞进 workflow engine"的 emerging pattern 会再撞到
- **Managed Agents vs OpenAI Assistants API** 横向对比——两家托管方案 trade-off
- **`PreCompact` hook 实战**:大 context agent 在压缩之前自定义保留哪些 message,是生产 long-context agent 的关键 lever
