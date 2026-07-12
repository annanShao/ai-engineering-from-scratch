# Lesson 14 · AutoGen v0.4:Actor Model 与 Agent Framework

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/14-autogen-actor-model/` |
| 类型 | Build · ~75 分钟 |
| 前置 | L12 (Workflow vs Agent)、L13 (LangGraph) |
| 关键文件 | `docs/en.md`、`code/main.py`(stdlib actor runtime) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/14-autogen-actor-model/docs/en.md |
| 状态 | ✅ 完成(换尺子时刻 + actor 三原语 + 一戒律三奢侈品 + DLQ 补刀 + 3/3 体检 + 4 金句) |

---

## 这节课的真定位:Phase 14 工程双柱的第二根

- **L13(LangGraph)** = 流程的可靠性(durable execution)
- **L14(AutoGen)** = 组织的弹性(actor / fault-isolation / 并发 / 分布式)

这两节合起来,是 Phase 14 整相的工程双柱。后面 L15-L17 三个框架,拿这两根柱子去对照,就能看出"每个框架在哪根柱子上加了什么、又付了什么代价"。

---

## 核心金句

### #1 · 换尺子时刻:你那把"图的所有权"尺子在 actor 这里失灵
> **LangGraph 的世界观是『一个 graph,一个共享 state,工程师拥有』;actor 的世界观是『N 个 actor,每个自己拥有自己的私有 state,只通过消息交流』。"图"在 actor 里**根本不存在**——只有消息走向构成的对话流。**

**Phase 14 新尺子(给 L14 换上):**

| 老尺子(L12/L13) | 新尺子(L14 actor) |
|---|---|
| "谁拥有那张图?" | **"谁拥有那份 state?"** |
| graph 是一等公民 | **actor 是一等公民** |
| 控制流 = edge | **控制流 = message routing** |
| 故障 = 整张图崩 | **故障 = 单个 actor 倒,其他人继续** |
| 并发是"特性" | **并发是默认** |

**LangGraph 让一个 agent 工作流 durable;AutoGen 让一群 agent 同时活着。前者是『单进程的可靠性』,后者是『分布式系统的可用性』——是两个工程问题,不是同一个问题的两种解法。**

### #2 · Actor 三原语 + 一条铁律,40 年没换过
> **Actor = Private state(外部碰不到)+ Inbox(消息队列)+ Handler(`receive(msg) → effects`,effects 只能是 5 种:reply / send / spawn / update self-state / stop self)。** 铁律:**两个 actor 永远不能共享内存,只能交换消息。**

这条戒律是 actor 一切好处的来源——没共享 → 没锁 → 没死锁;没共享 → 一个崩不污染另一个;没共享 → 同机/远程同抽象。**Actor 模型用一条戒律(不许共享内存)同时换来三个工程奢侈品(无锁并发 / 容错隔离 / 透明分布)。这就是 Erlang 40 年没倒、WhatsApp 50 人撑 9 亿用户的根因。AutoGen v0.4 把它搬进了 agent 领域。**

### #3 · 解耦的三件礼物(每条对应一类生产场景)

| 礼物 | 工程意义 |
|---|---|
| **Fault isolation** | 20 个 agent 的 team,1 个挂了,其他 19 个继续——LangGraph 整图崩,actor 单点崩 |
| **Natural concurrency** | 不用自己 `asyncio.gather`,actor 默认并发处理 inbox |
| **Distribution-ready** | inbox + transport 同抽象,1→100 机器只换 transport(NATS/gRPC/HTTP),代码不动 |

**这是 LangGraph 给不了的三件事**——checkpointer 解决"单 run 崩了能续",但没有内建多 actor 并发模型。

### #4 · AutoGen 在 maintenance,但 actor 是经久的(taste 级金句)
> **AutoGen v0.7.x 对研究/原型稳定,Microsoft 已把活跃开发转移到 Microsoft Agent Framework(2025-10-01 preview,2026 Q1 末 1.0 GA)。AutoGen 的 pattern 可以平滑 port——actor 模型才是经久的想法。**

**把认知绑到『AutoGen 怎么用』很快过期;绑到『actor 怎么思考』,十年还在。** 这是 Phase 14 这相设计成"先学原理再看框架"的原因——L13/L14 本质上是给同一组原理换皮。

→ 看 L15-L17 时**带着怀疑**:这个框架解决的是个真问题还是框架自己制造的问题?L12 那句"框架成本几千行"持续生效。

---

## DLQ 补刀:actor 失败处理的第三个原语(L06 + L13 + L14 拼齐)

**Dead-Letter Queue 的核心精神:** 出错的消息**不丢、不重试、不阻塞——挪到一个角落让人来看**。这是 Erlang "let it crash" 哲学的工程化兑现。

没 DLQ 的下场:崩消息悄无声息地丢,而且因为不影响其他 actor,**你可能几周才发现监控里有个静默黑洞**。

**Agent 跟世界打交道的失败模式 = 三件事拼起来:**

| 阶段 | 教 | 答案 |
|---|---|---|
| tool 报错 | L06 | error 塞回 observation 让 LLM 看 |
| tool 成功了但 state 没写就崩 | L13 | 幂等 + state 副作用台账 |
| **actor 处理消息时整个崩了** | **L14 DLQ** | **DLQ + 人工/告警介入** |

**L06 是 prompt 层的 graceful failure,DLQ 是 runtime 层的 fault containment。两者一起,才覆盖 agent 跟世界打交道的全部失败模式。**

---

## 关键概念地图

**AutoGen v0.4 三层 API:**

| 层 | 是什么 | 给谁 |
|---|---|---|
| **Core** | 低层 actor framework:`AgentRuntime / Agent / Message / Topic`,异步事件驱动 | 完全控制 actor 行为时 |
| **AgentChat** | 高层任务驱动:`AssistantAgent / UserProxyAgent / RoundRobinGroupChat / SelectorGroupChat` | 90% 常规多 agent 协作 |
| **Extensions** | OpenAI/Anthropic/Azure/tool/memory 集成 | 接外部世界 |

**三种 topology(对照 L13):**

| AutoGen topology | L13 / L12 对应 |
|---|---|
| RoundRobinGroupChat(固定轮转) | L12 prompt chaining 多 agent 版 |
| SelectorGroupChat(LLM 选下一个) | L13 Supervisor;L12 Routing |
| Magentic-One(参考多 agent 团队) | Claude Code 的 subagent 编排 |

注意 SelectorGroupChat 就是 L13 supervisor 的 actor 版;**而 LangChain 2026 改推 tool-call 派**——告诉你这两个框架虽然世界观不同,但都在被同一股『把中间层折叠掉』的潮流影响。

**用尺子收口:**

| AutoGen 部件 | 性质 |
|---|---|
| actor handler 里的 LLM 调用 | 内化 |
| actor 私有 state | **外部分布式 owned**(对比 LangGraph 集中 owned) |
| inbox / message queue | 外部 transport(可换) |
| runtime fault isolation | **外部 control plane**——actor 卖的真东西 |
| OTel span 自动埋点 | 外部可观测性(L23 专讲) |

---

## 体检 · 3/3 ✅

| # | 题 | 答 | 点评 |
|---|---|---|---|
| Q1 | 一戒律换的三个工程奢侈品 | B(无锁并发 + 故障隔离 + 透明分布) | 锁定本质 |
| Q2 | LangGraph 整图崩 vs actor 单点崩的源头 | B(共享 state vs 私有 state) | 直接到根因,没停在症状 |
| Q3 | 实时新闻情绪监控选什么 | C(AutoGen / Agent Framework) | 三信号叠加判断,没被 LangGraph 也有 durable 带歪 |

---

## 手做记录

`code/main.py` 实现 stdlib actor runtime(Message + Actor + Runtime + 两 actor 演示:ReviewerAgent + ChecklistAgent 消息往来 + 模拟故障证明 fault isolation)。**未额外跑**——概念已通过换尺子 + 三原语 + DLQ 补刀完全消化。

### 留给后续的钩子
- **Microsoft Agent Framework vs AutoGen 的承袭/差异**——未深挖,2026 Q1 GA 后值得回看。
- **分布式 transport 选型**(NATS / RabbitMQ / gRPC / Kafka)——actor 落到真实分布式环境的关键决策。
- **Dead-letter 策略**(重试次数 / TTL / 告警阈值 / 人工 review SLA)——生产 actor 系统的运维真现实,可能在 L23 (observability) / L26 (failure modes) 再碰。
- **进 L15 CrewAI 时带着怀疑**:role 抽象是不是只是把 actor 和 graph 用人类组织语言重新打包了一遍?这是看穿"营销层"的好练习。
