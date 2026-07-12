# Lesson 29 · Production Runtimes:Queue / Event / Cron

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/29-production-runtimes/` |
| 类型 | Concept · ~55 分钟 |
| 前置 | L13 (durable)、L14 (actor)、L17 (Managed/Temporal)、L18 (Agno/Mastra)、L22 (语音)、L23/L24 (observability) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/29-production-runtimes/docs/en.md |
| 状态 | ✅ 完成(六种运行时形态 + "形状决定失败能否活下来" + debug case + checkpoint invoke 追问 + 免体检直接过) |

---

## 这节课的真定位:把 agent 落到"真上线"的形态

同一 agent notebook 里跑得好,上生产以 notebook 从不暴露的方式挂(第 37 步网络超时/语音中途挂断/cron 重启死掉/后台 OOM)。**运行时的"形状"决定哪些失败你能扛过去。** 你前面学的所有能力,最后都要装进某种运行时形状里上线。

---

## 核心金句

### #1 · 运行时形状决定哪些失败能活下来
> **选运行时不是选技术,是先问『这个任务会怎么失败』,再选一个能扛住那种失败的形状。把 5 分钟任务装进 request-response,用户会挂断、worker 会堆积、重试会雪崩——不是 agent 错了,是你把它装进了扛不住它失败模式的形状里。**

**六种形态:**
| 形态 | 适合 | stack |
|---|---|---|
| Request-response(同步 HTTP,用户等) | 短任务 <30s | Agno/Mastra(L18) |
| Streaming(SSE/WS 渐进) | 实时反馈 | LiveKit WebRTC(L22) |
| Durable execution(每步 checkpoint 自动 resume) | 步数未知+恢复成本高 | LangGraph(L13)/AutoGen actor(L14) |
| Queue/background(进队列 worker 取) | 长程几十-几百步 | Celery/BullMQ/SQS |
| Event-driven(订阅触发器) | 被动响应事件 | Claude Managed(L17)/CrewAI Flows(L15) |
| Scheduled(cron 定期) | 周期任务 | K8s CronJob+durable |

### #2 · 按"时间 × 恢复成本"两轴选,durable 是叠加层
> **先问:这任务跑多久?崩了能不能从头再来?短+能重来→request-response(别过度工程);长+不能重来→queue+durable。durable execution 是叠加层(和其他形态正交),不是独立形态——任何"崩了不能重来"的场景都该叠上它。**

### #3 · 两句硬话(不可选)
- **Observability is load-bearing(承重墙)**:没有 OTel span(L23)+Langfuse/Phoenix/Opik(L24),没法 debug 第 40 步失败的 agent。对生产不是可选项,是"debug 得飞快"vs"加更多日志从头重放"的区别。
- **>30s 且不能重启的 run 必须上 durable**:可操作红线。

---

## 两个实战追问(用户提问,超纲)

### 追问 A · 具体 debug case:trace ≠ checkpoint
**关键混淆澄清**:trace(录像,L23/L24,不可执行)≠ checkpoint(存档,L13,可 resume)。**trace 负责定位,checkpoint 负责重来——两个系统配合。Langfuse 告诉你 bug 在哪,但不能在 Langfuse 上改了重跑。**

40 步 agent 第 12 步 prompt 写错(丢了数字)case:
1. Langfuse span 树定位到第 12 步 prompt("debug 得飞快"就在这,不用重跑 40 步)
2. patch prompt
3. **⭐ 关键坑:从坏 prompt 之前的 checkpoint(第 11 步)resume,不是从失败点(39)——坏 prompt 早污染了后面所有 state。resume 到多细取决于 checkpointer 存多密(node 级 vs step 级,呼应 A5)**

两种 patch:prompt 在代码里→改代码+从 checkpoint invoke(checkpoint 只恢复 state,代码新鲜执行);prompt 在 state 里→`update_state`+resume。

### 追问 B · "从 checkpoint invoke" 在哪处理:你的进程里,不是平台
**分层**:①Checkpointer 后端(你跑的 DB,存每步 state)→ ②LangGraph 运行时(库,读 checkpoint 恢复 state 继续)→ ③你的代码 `graph.invoke(None, config={checkpoint_id})` → ④Studio/LangSmith(可选 UI,只是把 ③ 包装成按钮)。

**"resume 不是平台功能,是 LangGraph 库本身的功能,跑在你进程里靠你配的 checkpointer DB。Studio/LangSmith 只是把 `invoke(None,config)` 包装成网页按钮+可点的树——没它们照样能 resume,只是得自己写代码看日志。平台卖的是方便和可视化,不是能力本身。"**

**deepagents + LangGraph Studio 本地**:deepagents=LangGraph(用户 trace 里 `langgraph_checkpoint_ns`/`langchain_create_agent` 为证,checkpoint 机制已在跑)。理论上 Studio 认得,但用户司 graph 缝了 TPP 专属 middleware(ruyi 运行时/沙箱/SkillsSync),本地没对应环境跑不起来。**三条路**:①先查 TPP 自己有没有 replay/fork(最靠谱,第一方平台通常自带)②抽核心 graph mock 掉 TPP middleware 本地跑 ③纯代码 `get_state_history`+`invoke(None,config)`。**第一方平台=深度集成换锁定的代价现身:缝得越深越难拆出来本地调。**

---

## 关键概念地图

**四个翻车(全是形状选错)**:Wrong shape choice(5 分钟任务用 request-response)/ No DLQ(失败任务凭空消失,L14)/ Opaque background work(后台没导出 trace,失败不可见直到用户投诉,L26 假成功)/ Skipping durable state(>30s 不能重启却没上 durable)。

**用尺子收口(运行时层大收束)**:六形态映射 L18/L22/L13/L14/L17/L15;observability 承重=L23+L24。

**"你造的 agent(L01-L11)、选的框架(L13-L18)、加的防御(L26-L27)、埋的观测(L23-L24),最后都落进六种运行时形态之一。选形态唯一正确方法:先问这任务会怎么失败、崩了能不能重来,再选扛得住的形状。会造 agent 的人让它在 notebook 跑通,会上线 agent 的人让它在扛得住真实失败的形状里跑通。"**

---

## 手做记录

概念课,未跑代码。核心通过 debug case(trace vs checkpoint)+ checkpoint invoke 在哪处理两个实战追问完全消化——直接对接用户司 deepagents/TPP 生产环境。

### 钩子
- **L30 Eval-driven**:把评测升成开发方法论(Phase 14 前 30 收官)
- checkpoint fork-resume 在自己 TPP 环境落地——先找平台团队问 replay 能力
