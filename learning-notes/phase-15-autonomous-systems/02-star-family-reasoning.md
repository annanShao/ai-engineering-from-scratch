# Lesson 15.02 · STaR 家族 — 自学推理

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/15-autonomous-systems/02-star-family-reasoning/` |
| 类型 | Concept · 自我改进起点 |
| 前置 | Phase14 L11(LLM-in-the-loop 物种 B)、L05(CRITIC)、15.L01(eval-gaming) |
| 状态 | ✅ 完成(STaR 三成员 + outcome reward 原罪 + 2026 stack 定位 + 3/3 揭秘) |

---

## 这节课的真定位:最小可用的自我改进循环

= Phase14 L11 三物种里**物种 B(内化到权重)的奠基算法**。STaR 把外部循环学到的烧进权重。理解它,AlphaEvolve/Darwin-Gödel/o1 全 click。

STaR 循环:① 采样(推理+答案)② 答案对就留 ③ 在留下的上 fine-tune ④ 重复。

---

## 核心金句

### #1 · 6B 自学 ≈ 175B 人标注(自我改进的诱惑力)
> **STaR 训的 GPT-J 6B 在 CommonsenseQA 72.5% ≈ 人标注 fine-tune 的 GPT-3 175B(73%),30× 大的模型被自学循环追平。这解释了 2025-26 前沿都在做:RL on verifiable math(DeepSeek-R1/o1)=STaR 答案条件梯度 scale up,AlphaEvolve=STaR for code,Darwin-Gödel=STaR for 脚手架。STaR 是所有自我改进的最小内核。**

三成员:
| 方法 | 补什么 |
|---|---|
| STaR | 起点(GSM8K 5.8→10.7%);rationalization = 给失败题注入正确答案当 hint 倒推推理 |
| V-STaR(Hosseini 2024) | 错的推理也是数据,DPO 训 verifier,推理时 best-of-N |
| Quiet-STaR(Zelikman 2024) | per-token 内部 rationale,学"何时该想"(难 token 想长易 token 不想) |

### #2 · ⭐ 三个共享的安全隐患:outcome reward 的原罪(Phase 15 暗线)
> **都用最终答案当梯度信号。通过错误推理蒙对答案的链(捷径/瞎猜/不泛化模式)会被正向强化——分布内有效,分布外静默崩。outcome reward 奖励"蒙对"而非"会做"。**

和 Phase14 L05 CRITIC vs Self-Refine 同一个病两个层:那里"judge 要接外部真相",这里"reward 要看过程不只结果"。**只有 outcome reward 的自我改进循环,会越训越擅长"在你测的分布上蒙对"——就是 L01 eval-gaming 的训练版。**

V-STaR verifier 也没全解:verifier 在同一批 label 上训,可能偏好"格式漂亮的错误推理"胜过"诚实不确定"——**裁判和选手同标准训出,裁判有和选手一样的盲区**。更安全:①process reward(Lightman 2023 "Let's verify step by step",奖励中间步)②held-out OOD 评测打破捷径。

### #3 · STaR 是模板,整相在填它的空
> **信号是什么(答案/程序/评测器)+ 内化到哪(权重/代码/脚手架)。L03 AlphaEvolve 把信号换成程序评测器,L04 Darwin-Gödel 把内化对象换成 agent 自己的代码。内核永远:生成→拿外部信号打分→留好的→强化→重复。你 Phase14 学的"外部 ground truth 是皇冠宝石"在自我改进里变成:打分信号的质量就是自我改进的天花板。**

---

## 体检 · 3/3(揭秘)

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(模型自生成推理,答案对就留 fine-tune,无需人标注) | STaR 内核 |
| Q2 | b(答案条件梯度奖励蒙对而非会做,分布外静默崩) | outcome reward 原罪 |
| Q3 | b(同模板三填空,打分信号质量=自我改进天花板) | 串起 L03/L04 |

---

## 手做记录
`code/main.py` 未跑,数学/概念已消化。

### 钩子
- L03 AlphaEvolve(STaR for code,Phase14 L11 从自我改进角度重看)
- L04 Darwin-Gödel(STaR for 脚手架)
- process reward vs outcome reward 是整相反复出现的安全轴
