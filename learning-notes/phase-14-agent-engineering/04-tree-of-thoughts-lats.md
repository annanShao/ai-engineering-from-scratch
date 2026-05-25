# Lesson 04 · Tree of Thoughts and LATS(刻意搜索)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/04-tree-of-thoughts-lats/` |
| 类型 | Build · ~75 分钟 |
| 前置 | Lesson 01 (Agent Loop)、Lesson 03 (Reflexion) |
| 关键文件 | `docs/zh.md`、`code/main.py`(ToT BFS + toy LATS MCTS) |
| 状态 | 🔄 进行中(阅读前概念铺垫) |

---

## 核心金句

### #1 · 外部搜索 vs 内部搜索:ToT/LATS 在模型外,native reasoning 在模型内
> **ToT/LATS 是"外部搜索"——harness 在编排层发起多次 LLM call(多分支)、打分、回溯,树在模型外面。o1/R1 的 native reasoning 是"内部搜索"——模型在一次 call 内部于隐藏 reasoning token 里自提假设、自评、回溯;某种程度上 RL 把 ToT 当年在外部干的事内化进了模型。**

推论:当你用的本来就是 reasoning model,它内部已经在 deliberate,再套昂贵外部树搜索(100–1000× token)边际收益就小——所以 2026 大多数生产 agent 不跑 LATS。ToT 那个 4%→74% 是在 GPT-4(非 reasoning)上测的;换 o1/R1 差距会收窄。

外部搜索现在主要剩在**有便宜可靠 value function** 的小生境(跑测试的 coding agent、deep-research 多路 query):

> **因为那里"验证"比"思考"更值钱,而验证恰恰是模型内部搜索给不了的。**

内部搜索的"评估"是 self-eval(模型评自己,弱信号、可能谎报成功);外部搜索能插一个 grounded 的 verifier(unit test、符号检查器)。这是不可消除的 gap,也是 ToT/LATS 的存活理由。

---

## 关键概念地图

(待补)

---

## 手做记录

(待补)
