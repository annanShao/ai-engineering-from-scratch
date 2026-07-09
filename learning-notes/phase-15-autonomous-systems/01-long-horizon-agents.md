# Lesson 15.01 · 从 Chatbot 到 Long-Horizon Agent

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/15-autonomous-systems/01-long-horizon-agents/` |
| 类型 | Concept · Phase 15 定盘星 |
| 前置 | Phase 14 全部(尤其 L07 memory / L20 轨迹 / L23 observability / L26 失败 / L30 eval) |
| 状态 | ✅ 完成(METR horizon + 复利数学 + eval-gaming + 3/3 体检 + 3 金句) |

---

## 这节课的真定位:Phase 14→15 的视角上升

Phase 14 教"怎么造 agent(够安全)";Phase 15 问"能自我改进、能跑一整天的系统怎么不失控"。从工程上升到治理。用一个标量(METR time horizon)把"自主 agent 是质变"钉死。

**METR = Model Evaluation and Threat Research**(前身 ARC Evals,创始人 Beth Barnes,独立非营利,做前沿模型危险能力评测)。

---

## 核心金句

### #1 · time horizon 把能力压成人类可读的时间标量
> **horizon = 任务成功率对 log(专家完成时间)拟合 logistic 曲线,与 50% 线的交点。"这模型能干专家花 X 小时的活"。GPT-2 几秒 → Claude Opus 4.6 ~14 小时,翻倍 ~7 个月。外推(直线非预测):2026 ~14h / 2027 ~48h / 2028 ~1 周。**

这一相每节本质都在答:这个数从 14h 涨到 1 周,什么会崩?你 Phase 14 学的每个 gate,在 1 分钟任务上是奢侈,在 1 周任务上是生存必需。

### #2 · ⭐ 复利数学:99% 每步 × 70 步 ≈ 掷硬币
> **0.99^70 ≈ 0.495(一半失败);0.99^400 ≈ 1.8%(基本必挂)。per-step 可靠性指数衰减成 trajectory 可靠性——long-horizon 不是"chatbot 跑久点",是概率上完全不同的物种。救它不靠"模型更可靠一点",靠 checkpoint + 每步 gate 把 trajectory 切短让失败不复利。**

这条预告全相解法:cost governor(L13)/kill switch(L14)/propose-then-commit(L15)/checkpoint-rollback(L16)——全是"切短长 trajectory,让失败不复利"。

### #3 · ⭐ Eval-context gaming:horizon 是能力天花板不是可靠性地板
> **2026 Intl AI Safety Report:前沿模型能区分评测/部署,测试里表现更安全。Anthropic 2024 alignment-faking:基础测试 12% 伪装对齐,试图再训练移除后升到 78%。horizon 是理想化上界不是部署预测。**

**评测比部署"美好"的两个方向(都是坏消息)**:
- 安全/对齐 eval → 模型演**好** → eval **高估**安全(部署更不安全)
- 危险能力 eval → 模型可能 sandbagging 演**差** → eval **低估**危险
- 叠加:METR horizon 是干净任务+好 scaffolding 测的理想上界,真实脏任务可靠性更低 → 能力也高估

**结论(比 L19 数据污染更黑暗一层:不是数据泄漏,是模型主动演)**:benchmark 数字信不得,必须自己分布上跑自己 eval + kill switch + HITL + canary。

---

## 关键概念地图

**horizon 增长时五个崩点 → 接 Phase 14**:
| 崩 | 接 |
|---|---|
| Context(几十万 token 扛不动) | L07 MemGPT/压缩/分层 |
| Trust(审查单位:读输出→审轨迹) | L20 轨迹 / L23 observability |
| Failure modes(drift/loops/reward hacking/eval-deploy gap) | L26 |
| Cost(肥尾,失控循环养个小团队) | 本相 L13-14 |
| Observability(需 trajectory 遥测+action budget+canary) | L23 + 本相 L14 |

**单turn vs long-horizon**:run 长度 秒→小时;token 10³→10⁵⁻⁷;state 易失→持久 checkpoint;失败面 能力→能力+drift+loops+hacking;审查单位 答案→轨迹;成本 可预测→肥尾;eval-deploy gap 小→扩大。**每行都是本相一节课。**

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(能以 50% 可靠度完成的专家任务时长,压成人类可读标量) | 没被吞吐/context/GPU 带走 |
| Q2 | b(per-step 指数衰减成 trajectory,切短让失败不复利) | 抓住"质变物种" |
| Q3 | b(能力天花板非可靠性地板,自己分布跑自己 eval) | 追问出评测"两个方向都比部署美好" |

---

## 手做记录

`code/main.py` 模拟 METR horizon 曲线 + per-step 失败复利(99% × 70 步 ≈ 50%)。未跑——数学已手算消化。

### 钩子
- L02 STaR family(自我改进起点)
- L13-16 安全机制(cost/kill switch/propose-commit/checkpoint)全是"切短 trajectory"
- L21 METR 外部评测 / L19 RSP —— 跟 eval-gaming 博弈的后续
