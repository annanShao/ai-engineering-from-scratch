# Lesson 13 · LangGraph:Stateful Graphs 与 Durable Execution

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/13-langgraph-stateful-graphs/` |
| 类型 | Build · ~75 分钟 |
| 前置 | L01 (ReAct)、L06 (Tool)、L09 (Memory)、L12 (Workflow vs Agent) |
| 关键文件 | `docs/en.md`、`code/main.py`(stdlib stateful graph)、`code/main.ts`(2026 新增 TS 版) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/13-langgraph-stateful-graphs/docs/en.md |
| 状态 | ✅ 完成(概念全覆盖 + 两个深度追问 + 3/3 体检 + 5 金句;代码未跑) |

---

## 这节课的真定位

L12 教 taste("谁拥有控制流图"),L13 是这把尺子的第一个**框架级落地实践**。LangGraph 不是教 agent 怎么思考,是教 agent 怎么**可被中断、可被审查、可被恢复**——把 Phase 14 反复强调的"必须外部"那一类(state / 持久化 / 控制流)做成工业级 SDK。Klarna/Uber/J.P. Morgan 上生产,要的不是 agent 的智能,是图的可审计性。

---

## 核心金句

### #1 · 在 L12 光谱上的位置:把不确定性"装进盒子"
> **LangGraph 把『不确定性』圈进每个 node 的盒子里,而把『图本身』的所有权死死攥在工程师手里。这是为什么 Klarna/Uber/J.P. Morgan 敢上生产——他们要的不是 agent 智能,是图的可审计性。**

L12 光谱往右走到 evaluator-optimizer 已是有终止条件的循环;**再让终止权也交给模型就是 full agent**。LangGraph 选择停在 evaluator-optimizer 那一档:**图工程师拥有,但每个 node 内部允许内嵌 agent**——是个"混血"中间物种。

### #2 · 四个零件简单到惊人,但杀手锏不在这四件
> **State(typed dict,每 node 读它改它,一等公民)+ Node(纯函数 `state→state_update`)+ Edge(conditional/direct)+ START/END sentinel。就这四样,完。**

真正的卖点:**state 是一等公民,checkpoint 是默认行为**——其他所有特性(human-in-the-loop / streaming / 崩溃恢复)都是这两件事的副产品。L12 那句"框架成本是几千行"对 LangGraph 不太适用,因为它的**概念表面**真的只有四件。

### #3 · Durable Execution = 给每个 node 自动 `git commit`
> **40 步的 run 卡在第 38 步崩了,你想从 38 接着跑而不是从 0 烧一遍 token。LangGraph 的答案:每 node 跑完,runtime 序列化 state 落盘到 checkpointer(SQLite/Postgres/Redis);崩了 `resume(session_id)` 接着走。**

**vs L11 AlphaEvolve archive 的对比:** 形似神不同。

| | AlphaEvolve archive | LangGraph checkpointer |
|---|---|---|
| 为什么存 | 后续 generation 采样,服务**演化压力** | 崩溃恢复/人在回路/UI 流式,服务**持久化** |
| 是 ground truth 延伸吗 | ✅ | ❌(与正确性无关) |

副作用(白送的三件):**Streaming**(每 node yield 增量)、**Human-in-the-loop**(critical node 前 pause 给人改,因 state 已序列化所以几乎免费)、**Memory**(短期=state 内 history,长期=checkpointer + 外挂 Mem0)。

### #4 · Supervisor → Tool-call 派(2026 LangChain 自己改口)
> **Anthropic / LangChain 2026 推荐:把 subagent 暴露成主 agent 的 tool,而不是用专职 supervisor LLM 做路由。** 等同于"路由 = tool 选择",不需要独立认知任务。

**两套世界观对比:**

| 维度 | `create_supervisor` 老派 | tool-call 新派 |
|---|---|---|
| 每次换手 LLM 调用数 | 2 次(supervisor 决策 + subagent 干活) | 1 次(主 agent 调 tool) |
| context 控制 | 框架决定切法,难干预 | 主 agent 显式塞 args,完全可控 |
| subagent 失败补救 | 难(路由信号丢错误信息) | 易(tool 报错走 L06 "error as observation") |
| 类比 | 大公司科层制——"我先汇报给主管,主管派下来" | 现代扁平团队——"这事我找 Bob 自己谈" |

Claude Code 的 `Task` tool 就是这个 pattern 的存在证明。**"把不必要的中间层折叠掉"——这和 L12 "复杂度是债务" 是同一个哲学的两次出现。**

三种 topology:Supervisor(L12 orchestrator-workers 的工业实现)/ **Swarm**(peer-to-peer 直接交接,每个 agent 把"转交给谁"暴露为 tool)/ Hierarchical(supervisor 嵌套)。

### #5 · Checkpoint 太小 = 副作用 exactly-once 的老问题(穷人版 Temporal)
> **LangGraph 的 checkpointer 解决『单机崩溃后能不能续跑』,但它**不**自动解决『副作用 exactly-once』。后者靠 tool 自己幂等 + state 完整记录副作用台账。LangGraph + 幂等 tool = 穷人版 Temporal/Cadence。**

**4 个真实翻车场景**——state 只存了"LLM 说了什么",没存"LLM 让世界改变了什么":

| # | 场景 | 后果 |
|---|---|---|
| 1 | `process_refund_tool` 调 Stripe 成功 → state 写盘前 OOM 崩 → resume 重跑 | 客户拿 $100(本应 $50),你赔一倍 |
| 2 | `send_email` 发完邮件 → 写盘前崩 → resume 重发 | 客户收两封一样邮件;SMTP 不像 Stripe 有 idempotency key,救不回来 |
| 3 | `reflect_and_save_to_mem0` 写完 mem → 崩 → resume 重写 | Mem0 多一条几乎一样的记忆 → fusion 加权后**人为放大权重** → L09 fusion 假设崩塌 |
| 4 | `db.execute("INSERT INTO loans ...")` 成功 → 崩 → resume 重 INSERT | UNIQUE 约束报错 → agent 按 L06 "error as observation" 改写 INSERT → 产生**两条略不同的贷款申请记录** |

**修法**: tool 用 `idempotency_key`(Stripe 原生);state 里维护 `tool_call_id + 状态(pending/done)` 的副作用台账;memory write 也带去重 key。

**和 L06 的对偶**:
- L06 问:tool 没跑成功怎么办 → 把 error 塞回 observation
- L13 问:tool 跑成功了但你不知道怎么办 → 把 tool 调用台账塞进 state
- **两道题加起来覆盖"和外部世界交互的 agent"两个最容易出血的点。**

---

## 关键概念地图

**Where this pattern goes wrong(三个翻车,每条对应 L12 那把尺子):**

| 翻车 | 课文说 | 用尺子翻译 |
|---|---|---|
| Checkpoint 太小 | 只 checkpoint 对话轮次 → tool state/memory 写不可恢复 | state 必须**全量**序列化——半个 state 不如没 state |
| Non-deterministic node | resume 假设输入产出相同 state 更新 | node 必须像纯函数;不纯就把不纯的种子写进 state |
| **Conditional edge 滥用** | 每条边都 conditional → 状态机不可推理 | **你给的 conditional 越多,图的所有权越往模型那端滑——LangGraph 用户最隐蔽的反模式:以为在用 workflow,实际是 full agent 套了个 LangGraph 壳子** |

**LangGraph 部件的内化/外部映射:**

| 部件 | 性质 |
|---|---|
| node 里的 LLM 调用 | 内化 |
| state schema | 工程师设计的外部 scaffolding |
| checkpointer | 外部持久化(L07 MemGPT 的工业表亲) |
| edges 的拓扑 | 工程师的判断(loop engineer 核心技能) |
| `resume(session_id)` | **外部 control plane**——LangGraph 卖给企业的真东西 |

---

## 体检 · 3/3 ✅

| # | 题 | 答 | 点评 |
|---|---|---|---|
| Q1 | checkpointer vs archive 本质区别 | C(服务持久化 vs 服务演化) | 抓住"为什么存",不是"怎么存" |
| Q2 | 每条边都 conditional 的项目 | B(以为在用 workflow,实际偷偷成 full agent 套壳) | LangGraph 用户最隐蔽的反模式 |
| Q3 | 贷款审批 agent 怎么选 | D(LangGraph——线性 + human-in-the-loop + 断点恢复 + 审计读图) | 三信号叠加的真·判断题 |

---

## 手做记录

`code/main.py`/`main.ts` 实现 stdlib stateful graph(State + Node + StateGraph + SQLiteCheckpointer + 一个 classify→branch→human gate→send 演示图,失败-持久化-resume 全 trace)。**未额外跑**——概念已通过两个深度追问(supervisor vs tool-call、checkpoint 翻车 4 例)完全消化。

### 留给后续的钩子
- **进 L14 AutoGen 时换尺子**:actor 模型和"graph + state"是完全不同的并发世界观;"图的所有权"那把尺子在 actor 里**会失灵**,需要换一把新的——这种"换尺子"体验是 Phase 14 最值得期待的一段。
- **Klarna/Uber 生产 case 细节** + **Swarm topology vs Anthropic multi-agent research blog**——未深挖,留作横向扩展。
- **Temporal/Cadence vs LangGraph**——分布式 workflow engine 和 agent durable execution 的本质亲缘,值得单独一节横向对比。
