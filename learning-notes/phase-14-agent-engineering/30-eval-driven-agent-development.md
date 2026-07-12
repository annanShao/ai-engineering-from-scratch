# Lesson 30 · Eval-Driven Agent Development(前 30 节收官)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/30-eval-driven-agent-development/` |
| 类型 | Concept + Build · ~60 分钟 |
| 前置 | L05/L06/L19/L20/L24/L26/L27——全相评测相关 |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/30-eval-driven-agent-development/docs/en.md |
| 状态 | ✅ 完成(前 30 收官 + 三层评测 + eval 当代码养 + Tying Phase 14 together + 3/3 体检 + 3 金句) |

---

## 这节课的真定位:Phase 14 前 30 节的拱顶石

不教新东西,把学过的每一节翻译成一个 eval case,给出方法论:**agent 开发不是"写完再测",是 eval-driven——先定义『对』长什么样(eval),再写代码去满足它,和 TDD 同构。把评测从"最后一步"提到"第一步"。**

---

## 核心金句

### #1 · 三层评测:从"通用但假"到"特定但真"
> **benchmark 泛化但和你产品无关(还可能污染);custom offline 贴你产品但离线;online 最真但最晚(生产已在跑)。三层都要——benchmark 挡模型选型退化,custom 挡我的场景退化,online 挡真实世界退化。只做 benchmark 是 L19『测错东西』;只做 online 是"等用户投诉才知道"。**

| 层 | 用途 | 学过的 |
|---|---|---|
| 1. Static benchmarks | 跨模型比较 + 回归门禁 | L19 SWE-bench/GAIA + L20 WebArena/OSWorld + L06 BFCL |
| 2. Custom offline | 你产品的形状(通用测不到) | L24 LLM-judge + L19 execution-based + L20 轨迹 |
| 3. Online | 生产真流量 | L24 session replay + L16/L21 guardrail 告警 + L23 cost/latency |

### #2 · 核心方法论:eval 当代码养(TDD 搬到 agent)
> **『eval 分数当合并门禁』把评测从『偶尔跑的脚本』变成『代码不达标进不了 main 的硬关卡』。这是 TDD 搬到 agent:传统软件用单元测试门禁『功能对不对』,agent 用 eval 门禁『行为好不好』。差别:单元测试确定(pass/fail),eval 统计(分数+阈值+不能退化>5%)。成熟标志是 CI 里有 eval gate,不是人肉 review『感觉这 prompt 改得挺好』。**

2026 best practice:evals live next to code / 每 PR 跑 CI / eval 分数 gate merge(退化>5% 拦) / **每道 guardrail→一个 eval case** / 每条学到的规则→一个 failure case。

**"每道 guardrail 对应 eval case"呼应 L26**:加防御就写 case 验证它真触发,否则防御是"写了但不知道有没有用"的死代码。

### #3 · Tying Phase 14 together:每节课都是一个 eval case
> **你学的每一节不只是概念,是一个『你 agent 该有的、可测试的行为』。『如果你的 eval suite 里每一条都有 case,你就覆盖了 Phase 14』——把整相从『知识』变成『可执行的质量标准』。你不再是『知道 handoff drift』,而是『我 CI 里有 case 验证 hop counter 真的 5 跳后停』。知识变成 gate 才算真落地。**

摘录清单:L01 无限循环 guard / L02 tool 失败正确 replan / L05 judge 通过精修输出 / L06 参数强制转换+未知 tool 拒 / L07-10 检索引用匹配来源+过期失效 / L13 resume 精确重现 state / L14 DLQ 抓崩溃 handler / L16 guardrail 对的输入触发 / L21 per-step safety 抓注入 DOM / L26 检测器标记已知失败 / L27 PVE 拒毒检索 / L28 supervisor 路由到对的专家。

---

## 关键概念地图

**Evaluator-optimizer(Anthropic)**:proposer 生成→evaluator 判→精修到通过。是 L05 Self-Refine 泛化。任何在意的 agent flow 都能包进去提可靠性。

**四个翻车(eval 本身也会坏)**:

| 翻车 | 呼应 |
|---|---|
| No baseline(没 last-known-good) | 说不出"退化了"(L24/L26) |
| **LLM-judge without grounding(judge 自己幻觉)** | **L05 CRITIC——judge 要接外部工具**(从 L05→L24→L30 出现三次) |
| Over-fitting to evals(优化 eval 偏离生产) | L19 Goodhart——轮换 case |
| Flaky evals(非确定假告警) | pin seed/snapshot state(L13 确定性) |

**"judge 要接 ground truth"从 L05 到 L24 到 L30 出现三次——不是重复,是反复砸同一钉子:评测可信度=judge 独立性,不是聪明程度。**

**收官金句**:"L30 证明 Phase 14 不是 30 个孤立知识点,是一套可逐条写成 eval、逐条在 CI 里 gate 的质量标准。贯穿始终那句话最终定形:agent 不可靠是前提,你的工作是把『它该怎么正确』写成 eval,让不达标的改动进不了生产。会造 agent 的人写代码,会交付 agent 的人写 eval 然后让代码去通过它。"

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(评测提到第一步=agent 版 TDD,分数当门禁) | 锁定翻转本质 |
| Q2 | b(没 eval 的 guardrail=没测过的假设=死代码) | 没被延迟/token 带走 |
| Q3 | b(三层各挡一种退化) | 没被"冗余备份/难度递进"带走 |

---

## 手做记录

`code/main.py` stdlib eval harness。未额外跑——概念已通过三层评测 + eval 当代码养 + Tying Phase 14 清单完全消化。

### 里程碑
- **Phase 14 前 30 节(理论 L01-L11 + 框架 L12-L18 + 运营 L19-L29 + 评测收官 L30)正式完成。**
- L31-L42 是 Agent Workbench 实战相:从"学概念"变成"做项目",在真实 repo 上用前 30 节的东西。
- 可选:进 L31 前做一次 Phase 14 前 30 节大复盘(像 L01-L17 那次,但全 30 节总图)。
