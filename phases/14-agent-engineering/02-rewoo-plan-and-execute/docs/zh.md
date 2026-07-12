# ReWOO and Plan-and-Execute:解耦式规划 (Decoupled Planning)

> ReAct 把 thought 和 action 交织在一个流里。ReWOO 把它们分开:先一次性出一个大 plan,再执行。token 少 5 倍、HotpotQA 上准确率 +4%,而且你能把 planner distill(蒸馏)进一个 7B 模型。Plan-and-Execute 把它泛化成一个模式;Plan-and-Act 把它扩展到了 web navigation。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 01 (Agent Loop)
**Time:** ~60 分钟

## 学习目标 (Learning Objectives)

- 解释为什么 ReWOO 的 Planner / Worker / Solver 拆分相比 ReAct 的交织 loop 能省 token、更鲁棒。
- 实现一个 plan DAG、一个按依赖排序的 executor,以及一个把 worker output 组合起来的 solver —— 全 stdlib。
- 用 2026 年的"五种 workflow pattern"框架(Anthropic),判断一个任务该跑 plan-then-execute 还是交织式 ReAct。
- 辨认什么时候需要 Plan-and-Act 的合成 plan 数据来做长程(long-horizon)的 web 或 mobile 任务。

## 问题所在 (The Problem)

ReAct 那个交织的 thought-action-observation loop 简单又灵活,但每一次 tool call 都得带上完整的先前上下文 —— 包括之前的每一个 thought。token 用量随深度**二次方**增长。更糟的是:当某个 tool 在 loop 中途失败,模型得从那条 error observation 里把**整个 plan 重新推导一遍**。

ReWOO(Xu 等人,arXiv:2305.18323,2023 年 5 月)注意到了这点,押了一个注:**先把整件事规划好,并行抓取 evidence(证据),最后再组合出答案**。一次 LLM call 做 plan,N 次 tool call 抓 evidence(可以并行),一次 LLM call 做 solve。代价是灵活性变差(plan 是静态的),换来的是好得多的 token 效率和更清晰的 failure mode。

## 核心概念 (The Concept)

### 三个角色 (The three roles)

```
Planner:  user_question -> [plan_dag]
Workers:  [plan_dag]     -> [evidence]        (tool calls, possibly parallel)
Solver:   user_question, plan_dag, evidence -> final_answer
```

Planner 产出一个 DAG。每个 node 指明一个 tool、它的参数,以及它依赖哪些更早的 node(用 `#E1`、`#E2` 这样的 reference)。Workers 按拓扑序(topological order)执行 node。Solver 把所有东西缝合起来。

### 为什么 token 少 5 倍

ReAct 的 prompt 长度随步数**线性**增长。到第 10 步时,prompt 里装着 thought 1 + action 1 + observation 1 + thought 2 + action 2 + observation 2……如此累加。而且每个中间步骤还冗余地重复包含了原始 prompt。

ReWOO 只付:一个 planner prompt(大)、N 个小 worker prompt(每个只是那次 tool call,不带 chain)、一个 solver prompt。论文在 HotpotQA 上测出 token **约少 5 倍**,同时准确率绝对值 **+4**。

### 为什么更鲁棒

在 ReAct 里如果 worker 3 失败,loop 得在流中途把自己从 error 里"想"出来。在 ReWOO 里,worker 3 返回一个 error string;solver 在上下文里连同原始 plan 一起看到它,可以**优雅降级**(degrade gracefully)。失败定位是**per-node**(按节点),而不是 per-step(按步)。

### Planner distillation(规划器蒸馏)

论文的第二个结果:因为 planner **看不到 observation**,你可以用一个 175B teacher 的 planner output 去 fine-tune 一个 7B 模型。小模型负责 planning;推理时不需要大模型。这现在已是标准做法 —— 很多 2026 生产 agent 用一个小 planner + 一个大 executor,或者反过来。

### Plan-and-Execute(LangChain,2023)

LangChain 团队 2023 年 8 月的博文把 ReWOO 泛化成了一个模式名:Plan-and-Execute。前置的 planner 产出一个 step list,executor 逐步执行,一个可选的 **replanner** 可以在观察结果后修订计划。这比 ReWOO 更接近 ReAct(replanner 把 observation 带回了 planning),但保留了 token 节省。

### Plan-and-Act(Erdogan 等人,arXiv:2503.09572,ICML 2025)

Plan-and-Act 把这个模式扩展到长程的 web 和 mobile agent。关键贡献是**合成 plan 数据**(synthetic plan data):一个带标注的 trajectory 生成器产出训练数据,其中 plan 是显式的。用来 fine-tune planner 模型,让它在 WebArena 这类任务上跑过 30–50 步还能保持连贯 —— 而单条 ReAct trajectory 在这种长度上会丧失连贯性。

### 该选哪个 (When to pick which)

| Pattern | 什么时候用 |
|---------|------|
| ReAct | 短任务、环境未知、需要 reactive 的异常处理 |
| ReWOO | 结构化任务、tool 已知、对 token 敏感、evidence 可并行 |
| Plan-and-Execute | 像 ReWOO,但执行一部分后会 replanning |
| Plan-and-Act | 长程(>30 步)、web/mobile/computer-use |
| Tree of Thoughts | 值得为 search 付代价时(Lesson 04) |

Anthropic 2024 年 12 月的指导:**从最简单的开始**。如果任务是一次 tool call 加一段 summary,别去搭 ReWOO。如果任务是一个 40 步的 research 作业,别只用 ReAct。

## 动手做 (Build It)

`code/main.py` 实现了一个 toy ReWOO:

- `Planner` —— 一个脚本化的 policy,从 prompt 产出一个 plan DAG。
- `Worker` —— 通过 registry 派发每个 node 的 tool call。
- `Solver` —— 脚本化的组合逻辑,读取 evidence 并产出 final answer。
- 依赖解析(Dependency resolution)—— 像 `#E1` 这样的 reference 会被替换成更早的 worker output。

这个 demo 回答"What is the population of the capital of France, rounded to millions?(法国首都的人口,四舍五入到百万)",用一个两步 plan:(1) 查首都,(2) 查人口,然后 solve。

运行它:

```
python3 code/main.py
```

trace 先显示完整的 plan,然后是 worker 结果,再是 solver 的组合。把 token 数(我们打印了一个粗略的字符计数)和一次 ReAct 式的交织 run 对比 —— 在这类结构化任务上 ReWOO 胜出。

## 用起来 (Use It)

LangGraph 把 Plan-and-Execute 作为一个 recipe 提供(ReAct 用 `create_react_agent`,plan-execute 用自定义 graph)。CrewAI 的 Flows 直接编码了这个模式:你前置地定义好 task,Flow DAG 来执行它们。Plan-and-Act 的合成数据方法目前仍主要是研究阶段;运行时的模式(显式 plan DAG)已通过 LangGraph 和 CrewAI Flows 在生产里落地。

## 交付出去 (Ship It)

`outputs/skill-rewoo-planner.md` 在给定一个 tool catalog 的情况下,从用户请求生成一个 ReWOO plan DAG。它在交给 executor 之前会**校验**这个 plan(无环、每个 reference 都能解析、每个 tool 都存在)。

## 练习 (Exercises)

1. 为相互独立的 plan node 并行执行 worker。在一个有 2 个并行组的 6-node DAG 上,这能给你带来什么?
2. 加一个 replanner node,在任何 worker 返回 error 时触发。让 ReWOO 变成 Plan-and-Execute 的最小改动是什么?
3. 把 `Planner` 换成一个小模型(7B 级),`Solver` 留在 frontier 模型上。对比端到端质量 —— 这个拆分在哪里会崩?
4. 读 ReWOO 论文第 4 节关于 planner distillation 的部分。在概念上复现 175B -> 7B 的结果:你需要什么训练数据,怎么给 plan 质量打分?
5. 把这个 toy 移植到 Plan-and-Act 的 trajectory 形态:plan 是一个**序列**,不是 DAG。哪些取舍变了?

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| ReWOO | "Reasoning without observations" | 先 plan、再并行抓 evidence、再 solve —— planning prompt 里没有 observation |
| Plan-and-Execute | "LangChain 的 plan-execute 模式" | 带一个可选 replanner node(执行后触发)的 ReWOO |
| Plan-and-Act | "扩展版 plan-execute" | 显式 planner/executor 拆分 + 给长程任务用的合成 plan 训练数据 |
| Evidence reference | "#E1, #E2, ..." | plan-node 占位符,派发时被替换成先前 worker output |
| Planner distillation | "小 planner、大 executor" | 用大 teacher 的 planner trace fine-tune 一个小模型 |
| Token efficiency | "更少的往返" | 论文里 HotpotQA 上比 ReAct 少 5 倍 token |
| DAG executor | "拓扑派发器" | 按依赖序跑 plan node;每一层可并行 |

## 延伸阅读 (Further Reading)

- [Xu et al., ReWOO: Decoupling Reasoning from Observations (arXiv:2305.18323)](https://arxiv.org/abs/2305.18323) —— 那篇标准论文
- [Erdogan et al., Plan-and-Act (arXiv:2503.09572)](https://arxiv.org/abs/2503.09572) —— 带合成 plan 的扩展版 planner-executor
- [LangGraph Plan-and-Execute tutorial](https://docs.langchain.com/oss/python/langgraph/overview) —— 框架 recipe
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) —— 挑能解决问题的最简单模式
