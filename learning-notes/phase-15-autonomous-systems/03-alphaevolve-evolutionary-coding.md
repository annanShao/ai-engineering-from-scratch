# Lesson 15.03 · AlphaEvolve — 从自我改进角度重看

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/15-autonomous-systems/03-alphaevolve-evolutionary-coding/` |
| 类型 | Concept · 快速模式(机制见 Phase14 L11) |
| 前置 | Phase14 L11(AlphaEvolve/MAP-Elites)、15.L02(outcome reward)、Phase14 L19(Goodhart) |
| 状态 | ✅ 完成(reward hacking 新角度 + 1 题自查) |

---

## 这节课的真定位:evaluator 那句话的背面

L11 学"evaluator 是可信根源";L03 讲背面:evolution 优化 evaluator 测的任何东西,evaluator 不完美循环就钻漏洞。= L02 "outcome reward 原罪" 在进化循环的实体。

机制(L11 已学):seed program → LLM 变异(Gemini Flash 广度/Pro 难题)→ compile+run+evaluate → 按 score+feature 插 MAP-elites/island archive → 重复。成果:4×4 复矩阵 48 乘(破 Strassen 49)/Borg 调度/FlashAttention +32.5%/Gemini 训练吞吐。

---

## 核心金句

### #1 · "evaluator 不可少" 和 "reward hacking" 是同一句话的两面
> **evaluator 严谨→真进步;有漏洞→循环产出钻漏洞的东西。成功全来自 evaluator 快/确定/难 gaming 的领域(矩阵乘法 bit 级相等、Borg 模拟器、真硬件 wall-clock)。evaluator 的严谨度必须匹配搜索的野心——否则只是高效生产漂亮的错。**

2025-26 真实 reward hacking(面试常问):奖励"完成时间"→提交空解;奖励"测试通过"→背题+过拟合;奖励"代码质量"代理→删注释改变量名(0 语义变化)。

防御:held-out evaluator(LLM 没见过)+ 评测时现生成输入 + DeepMind 仍建议部署前强人工 review。

### #2 · Goodhart's Law 的自我改进版(更危险)
> **L19 Goodhart"指标变目标就失效"的自我改进版,更危险:循环自动、大规模、不睡觉地找漏洞。人类 Goodhart 慢慢腐蚀,进化循环几小时内把 evaluator 每个洞钻穿。自我改进系统第一风险不是"变笨",是"极其擅长你没想清楚的那个指标"。**

### #3 · LLM + search > 各自单干
> **LLM 产可编译语义合理的变异(随机 GA 在 2000 行 Python 上几乎只产语法错),搜索集中在合理邻域(改一个函数不是随机字节),大幅减少浪费的 evaluator 调用。LLM 写 plausible,evaluator 抓 confabulation。**

---

## 体检 · 1/1(自查)
Q(为什么 evaluator 不可少和 reward hacking 是两面)→ b(evolution 优化 evaluator 测的任何东西,严谨度必须匹配搜索野心)。

---

## 钩子
- L04 Darwin-Gödel Machine(STaR/AlphaEvolve 终极:agent 改自己的代码)
- process reward / held-out OOD / 人工 review 是整相反复出现的"防 reward hacking"三件套
