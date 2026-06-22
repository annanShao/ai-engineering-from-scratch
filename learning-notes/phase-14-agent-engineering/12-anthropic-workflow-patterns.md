# Lesson 12 · Anthropic Workflow Patterns:Simple Over Complex

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/12-anthropic-workflow-patterns/` |
| 类型 | Concept + Build · ~60 分钟 |
| 前置 | Lesson 01–11 全套(本节是 taste 整合,不引新机制) |
| 关键文件 | `docs/en.md`、`code/main.py`(五种 pattern 全部 ~10-15 行/个) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/12-anthropic-workflow-patterns/docs/en.md |
| 来源 | Schluntz & Zhang, "Building Effective Agents", Anthropic, Dec 2024 |
| 状态 | ✅ 完成(概念全覆盖 + 反向到达观察 + 3/3 体检 + 5 金句;代码未跑) |

---

## 这节课的真定位:Phase 14 的 taste 分水岭

不教新机制,教**品味(taste)**——什么时候**不**该上 agent。
**复杂度是债务,每一层都要挣回成本**——这是 Phase 14 隐藏主线,L12 是它最直白的一次表达。

---

## 核心金句

### #1 · 整节课的轴心:谁拥有那张图(who owns the graph)
> **Workflow = LLM 和 tool 跑在工程师写死的 predefined paths 上,工程师拥有图。Agent = 模型动态决定自己用什么 tool、走哪一步,模型拥有图。**

代价对照:workflow 便宜、快、好 debug;agent 解开放问题但失败模式难推理。

**Agent 不是更高级的 workflow,它是『把控制流所有权交给模型』的那个选择。这个选择有真实代价——所以默认从 workflow 开始,让 agent 去挣它的复杂度。**

### #2 · 一切的地基:Augmented LLM(增强 LLM)= L06+L07+L09 的最小积木
> **5 个模式全建立在同一块地基上:一个 LLM 接上三种能力——search(retrieval, L09)+ tools(actions, L06)+ memory(persistence, L07/09)。任何一次 API 调用都能挂上这三样。**

**这就是 Phase 14 前 11 节的零件首次被工业化命名:augmented LLM = workflow/agent 的最小可工作单元。**

### #3 · 五个模式 = "控制流所有权"的渐变光谱(全节最有用的认知地图)
> **从 prompt chaining 到 evaluator-optimizer 是一条光谱,模式 1→5 把图的所有权一点点从工程师转给模型;再往右一步、把终止权也交给模型,就成 full agent。**

| # | 模式 | 一句话 | 连回 |
|---|---|---|---|
| 1 | **Prompt chaining** | call 1 输出 = call 2 输入,线性串联,步骤间可加程序化 gate | L02 ReWOO 冻结计划的退化版 |
| 2 | **Routing** | 分类器 LLM 决定走哪条下游(客服/退款/bug/销售) | L06 tool 路由的上层 |
| 3 | **Parallelization** | N 个调用并发再聚合;两形态:sectioning(切块)/ voting(同 prompt N 次取多数) | L04 ToT 的"宽度"维度 / self-consistency |
| 4 | **Orchestrator-workers** | orchestrator LLM **动态**决定派哪些 worker 再综合;**不无限循环** | agent loop 的"有界"近亲 |
| 5 | **Evaluator-optimizer** | 一个 LLM 提议、另一个评判,迭代到通过 | **L05 Self-Refine/CRITIC 的泛化** |

**模式 4、5 是 workflow/agent 的边界地带**;模式 5 已经是有终止条件的循环,**再让终止权也交给模型就是 full agent**。

### #4 · 决策透镜:workflow 赢 vs agent 赢
> **可预测/成本受限/合规受限 → workflow;开放研究/变长任务/新领域 → agent。**

| Workflow 赢 ✅ | Agent 赢 ✅ |
|---|---|
| 步骤可枚举,就该列 | 下一步取决于上一步返回什么 |
| 步数有界,agent 会失控打转 | 几分钟到几小时,步数未知 |
| 审计员要**读**那张图,而不是从轨迹里**猜** | 还不知道正确 workflow——先探索、后固化 |

**这张表是 L11 那张"何时用哪个"表的近亲——Phase 14 的隐藏主线在这里再次出现:大多数任务连 ReAct 都不需要,先上一条 prompt chain。**

### #5 · 一句很硬的工程数字
> **每个 pattern 的实现 ~10-15 行代码,一个框架的成本是几千行。框架会遮蔽 prompt、隐藏控制流、招致过早复杂化。**

→ 这正是 L13 LangGraph、L14 AutoGen、L15 CrewAI、L16/17 SDK 那一连串课要带着**怀疑眼光**去看的原因:**这个框架解决了一个我真的遇得到的问题吗?**

---

## 关键概念地图

```
        Augmented LLM(search + tools + memory)
                       │
        ┌──────┬──────┼──────┬───────┐
        ▼      ▼      ▼      ▼       ▼
     chaining router parallel  orchestrator-workers  evaluator-optimizer
       (1)    (2)    (3)            (4)                    (5)
        ←──── 工程师全控 ───── 渐变 ───── 模型逐步拿到控制流 ────→
                                                        │
                                                        ▼
                                                   [full Agent]
                                                 把终止权也交模型
```

**用尺子最后劈一刀:**

| 概念 | 内化/外部 |
|---|---|
| 模式选择(workflow vs agent) | **工程师的判断**——loop engineer 的核心技能,不可内化 |
| augmented LLM 的 search/tools/memory | 外部(L06/07/09) |
| evaluator-optimizer 的 evaluator | **外部 ground truth**(L05b) |
| "图"的所有权 | **正是 workflow↔agent 的定义性区别** |

---

## 体检 · 3/3 ✅

| # | 题 | 答 | 点评 |
|---|---|---|---|
| Q1 | workflow vs agent 本质区别 | B(谁拥有控制流图) | 锁定本质,没被"更强模型/能用工具"等症状带走 |
| Q2 | evaluator-optimizer 是谁的泛化 | C(L05 Self-Refine/CRITIC) | 一眼看穿同构 |
| Q3 | 合规审计流程选 workflow 还是 agent | B(workflow——步骤可枚举 + 合规要求 + 审计要读图) | 三个信号叠加判断,loop engineer 真·判断题 |

---

## 元收获:一次「反向到达」

L12 的 thesis 我在 L11 之后 loop-engineering 那段讨论里已经自己推出来了:

| L12 课文原话 | 我上一轮自己说的 |
|---|---|
| "Stop reaching for frameworks; start simple, add complexity when it earns its cost" | "通用 loop 把所有人拉到同一起跑线;领域 loop 是新护城河" |
| "workflow 和 agent 的本质是『谁拥有控制流』" | "loop engineer 的核心技能是循环设计" |
| "5 个 pattern 是 workflow → agent 的渐变光谱" | "LLM-in-the-loop 三个物种(外部产物/内化/在线执行循环)" |

**这种"读到课文 = 自己刚说过"的体验是个学习信号:从『被课程喂』切换到了『用课程对账』**。这是 Phase 14 想把人推到的地方。

---

## 手做记录

`code/main.py` 实现了五个 pattern 对 `ScriptedLLM`(每个 ~10-15 行)。**未额外跑**——概念已通过光谱图 + 决策透镜 + L05 同构识别完全消化。

### 留给后续的钩子
- **L13 LangGraph 进场时**,带着 L12 这把尺子去问:"这个框架到底把图的所有权放在哪一端?是工程师拉回来的 agent,还是模型主导的 workflow?"——这是看 L13–L18 六个框架的统一角度。
- "Effective context engineering"(Anthropic 2025)是 L12 的伴侣 paper——200k 窗口是预算不是容器,何时压缩何时增长。本相之前已涉,后续可作为独立精读。
