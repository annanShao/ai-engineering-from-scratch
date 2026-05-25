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

### #2 · native reasoning 机制是链,行为是"压扁的搜索"
> **R1/o1 物理上仍是一条线性 autoregressive token 链(无并行分支、无回溯指针);但内容是一次搜索的序列化展开——在流里口头地"提假设→内联自评→放弃→换一个",把一棵 DFS 树拉直写成一条转录稿。所以是"行为上分叉,基底上线性",不是真并行树。**

和真·ToT 的三点差异:
| | R1 内部"搜索" | 外部 ToT/LATS |
|---|---|---|
| 并行 | 无,token-time 里顺序探索 | 能并行 expand K 个子节点 |
| 回溯 | 假回溯,被弃分支仍在 context 占 token | 真回溯,死分支从该路径消失 |
| 评估 | self-eval(模型意见) | 可插 grounded verifier |

诚实边界:R1 内部是否"真搜索"学界无定论,一派认为是 RL 训出的"搜索式启发"而非系统 tree search。能确证的只是外在行为像搜索的线性展开。

### #3 · 哪些"绕 LLM 的结构"会被内化,哪些是永久基建(bitter lesson 的可操作版)
> **判别线:scaffolding 是在"重排模型自己的思考",还是在"把模型接到身外的东西 / 提供它给不了的保证"?前者是临时拐杖,迟早被 RL 内化进权重;后者是永久基建,模型再强也得外部建。**

**会被内化(围绕"认知"):** 只重排模型如何用自己已有知识/推理的脚手架。
| 结构 | 被什么内化 |
|---|---|
| CoT prompting | native reasoning |
| ToT/LATS 外部树搜索 | native reasoning 内部 deliberation |
| ReAct 的 `Thought:/Action:` 文本 hack | native tool-use(结构化 tool_call) |
| 提示工程小技巧、任务分解启发式 | 模型变强后边际归零 / 内部自己 plan |

共性:有界于权重+context、RL 有训练信号、属"内部认知"。

**注定留在外部(连接"世界"与"保证"):**
1. Grounded verification / ground truth(跑测试、查真库、对照现实)
2. 新鲜/私有/外部 state(实时数据、私有文件、系统真实状态)
3. 副作用 / 真实动作(真发邮件、真写文件、真调 API)
4. 硬保证 / 确定性 / 约束(安全边界、权限、限流、事务、审计、可复现 replay)
5. 跨边界持久化(超出 context window 的 durable memory,Lesson 03 第三层)
6. 可观测 / eval(从外部度量模型干了啥)

共性:触及权重+context 之外的现实 / 需要确定性保证。

**一句话压缩:** 模型会吞掉一切关于"思考"的东西;harness 永远守着一切关于"触及现实"和"提供保证"的东西。改进模型"猜得更准"的脚手架终将被内化;提供 ground truth / 副作用 / 硬保证 / 持久化的脚手架是永久基建。

**回填 Lesson 01 三层模型:** Harness 层不会被更强模型吃掉,因为它干的恰是上面"留在外部"那张清单——这是它存在的第一性理由。

---

## 关键概念地图

(待补)

---

## 手做记录

(待补)
