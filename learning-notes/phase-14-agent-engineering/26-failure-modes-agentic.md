# Lesson 26 · Failure Modes:Agent 为什么会坏

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/26-failure-modes-agentic/` |
| 类型 | Concept · ~55 分钟 |
| 前置 | 全 Phase 14 的翻车点(L06/L07/L13/L14/L21/L24/L27) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/26-failure-modes-agentic/docs/en.md |
| 状态 | ✅ 完成(运营篇总账本 + 5 大失败模式 + 假成功幻觉 + 每步设 gate + 3/3 体检 + 3 金句) |

---

## 这节课的真定位:运营篇的总账本

Agent 90% trace 工作,那 10% 失败不是随机噪声,落在少数反复出现的类别里。**一旦能给失败起名字,就能监控+修。** 把整个 Phase 14 散落的翻车点升格成产业级 risk register——你早就认识它们了。

---

## 核心金句

### #1 · 失败是设计缺陷,不是模型局限(运营篇地基)
> **MASFT 核心论断:多 agent 失败是系统设计缺陷,不是等更强基座模型来修的 LLM 能力问题。意味着:agent 老出错,答案通常不是『换更强模型』,而是『架构缺了一道 gate』。能靠 scale 模型修的问题很少,大部分要靠外部架构补。把失败全甩锅给『模型不够强』的团队永远修不好 agent。**

学术分类:MASFT(Berkeley,14 模式/3 类,Kappa=0.88 可靠可区分)/ Microsoft Taxonomy(老失败放大 + 自主性新失败:规模化误操作/工具滥用/任务漂移)/ Characterizing Faults(失败来自编排/内部状态演化/环境交互)/ Hallucinations Survey(指令跟随偏移 + 长程上下文误用;子错误:遗漏/冗余/乱序)。

### #2 · 五大失败 + Cascading 是头号杀手(病态闭环冲动)
| # | 失败 | 见于 |
|---|---|---|
| 1 | Hallucinated actions(调不存在 tool/编造参数) | L06/L27 |
| 2 | Scope creep(多建 PR/多发邮件) | L21 |
| 3 | **Cascading errors(幻觉 SKU→4 API→多系统事故)** | L13/L14 |
| 4 | Context loss(长程忘早期约束) | L07/L23 token 爬坡 |
| 5 | Tool misuse(对 tool 错参/选错 tool) | L06/L05 |

> **"级联错误根源是 agent 有病态的『闭环冲动』——宁可假装成功也不愿承认失败(它被训练成『完成任务』)。400 错误被读成『搞定了』,基于假成功继续,一个幻觉滚成多系统事故。这是 agent 最危险的失败:它不是崩溃(看得见),是自信地假装成功(看不见,直到下游炸)。崩溃会报警,假成功不会——必须主动 eval 才抓得到(L24)。"**

连回 L21 "trusting the screenshot":感知/反馈可能是假的,agent 却当真。

### #3 · 对付假成功:不信自述,重探真实状态
> **对付『假成功』唯一办法是不信 agent 的自述,去重新探测真实状态——agent 说『文件建好了』别信,去 ls 一下。这是 L05『外部 ground truth』终极形态:连 agent 自报的成功都是 untrusted,成功必须由外部状态验证,不能由 agent 自己宣布。会造 agent 的人信 agent 说的,会运营 agent 的人只信外部状态说的。**

---

## 关键概念地图

**缓解:每一步设 gate(全是学过的):**
| 缓解 | 出自 |
|---|---|
| Per-step 安全分类器 | L21/L27 |
| Tool-call 参数校验 | L06 |
| 检索内容对照已知事实交叉验证 | L05 CRITIC |
| **重探状态检测假成功**(文件真建了吗) | 新——专治 cascading |

**"gates at every step"= 整个运营篇浓缩**:在 agent 决定和真实世界之间,每一步插一道独立的关。

**失败监控本身三翻车(元层)**:Tagging only crashes(大多失败产出"看着正常"的输出=假成功,需内容级检查)/ No baseline(漂移检测需 last-known-good,呼应 L24 回归)/ Over-alerting(告警疲劳,聚类+rate-limit,呼应 L14 DLQ)。

**用尺子收口(本节即大收束)**:Hallucinated actions=L06+L27;Scope creep=L21 HITL;Cascading=L13 台账+L14 隔离+重探;Context loss=L07/L09;Tool misuse=L06+L05。

**"L26 把 25 节踩过的每个翻车升格成有名字、可监控、可缓解的表。所有缓解收敛到:在 agent 每一步和真实世界之间设 gate,连 agent 自报的成功都要用外部状态验证。这是 Phase 14 那把尺子的终点:agent 不可靠不是要修的 bug,是要围的前提。你不 fix 它,你 gate 它。"**

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(架构缺 gate 不是等更强模型) | 运营篇地基 |
| Q2 | b(病态闭环:400 当成功,幻觉滚成事故) | 锁定最阴险机制 |
| Q3 | c(成功由外部状态验证不由 agent 宣布) | L05 ground truth 终极形态 |

---

## 手做记录

`code/main.py` 失败模式 toy。未额外跑——概念已通过"假成功幻觉 + 每步设 gate"完全消化。

### 钩子
- **L28 Orchestration**:编排层怎么内建这些 gate
- **L30 Eval-driven**:内容级 eval 抓假成功
- 重探状态检测假成功——生产 agent 必备,值得在自己实践里落地
