# Reflexion:Verbal Reinforcement Learning(言语强化学习)

> 基于梯度的 RL 要修一个 failure mode,得跑成千上万次 trial、烧一个 GPU 集群。Reflexion(Shinn 等人,NeurIPS 2023)用自然语言做这件事:每次 trial 失败后,agent 写一段 reflection(反思),存进 episodic memory(情景记忆),并让下一次 trial 以这段 memory 为条件。这就是 Letta sleep-time compute、Claude Code 的 CLAUDE.md learnings、以及 pro-workflow 的 learn-rule 背后的模式。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 01 (Agent Loop)、Phase 14 · 02 (ReWOO)
**Time:** ~60 分钟

## 学习目标 (Learning Objectives)

- 说出 Reflexion 的三个组件(Actor、Evaluator、Self-Reflector)以及 episodic memory 的角色。
- 实现一个 stdlib 的 Reflexion loop,带 binary evaluator、reflection buffer 和全新重试(fresh re-attempts)。
- 针对给定任务,在 scalar、heuristic、self-evaluated 三种 feedback 来源之间做选择。
- 解释为什么 verbal reinforcement(言语强化)能抓住那些 gradient-based RL 要成千上万次 trial 才能修的错误。

## 问题所在 (The Problem)

一个 agent 把任务搞砸了。在标准 RL 里你会再跑几千次 trial、算 gradient、更新 weight。又贵、又慢,而且大多数生产 agent 没有"给每个失败都配一份训练预算"的条件。

Reflexion(Shinn 等人,arXiv:2303.11366)问了个不一样的问题:**如果 agent 就只是想一想自己为什么失败,然后带着这个想法塞进 prompt 再试一次呢?** 不更新 weight、没有 gradient,只是在 trial 之间用自然语言存点东西。

结果:在 ALFWorld 上它打败了 ReAct 和其他没微调的 baseline。在 HotpotQA 上它优于 ReAct。在代码生成(HumanEval/MBPP)上它当时刷到了 SOTA。**全程没有一步 gradient。**

## 核心概念 (The Concept)

### 三个组件 (The three components)

```
Actor         : 生成一条 trajectory(ReAct 式的 loop)
Evaluator     : 给 trajectory 打分 —— binary、heuristic 或 self-eval
Self-Reflector: 对失败写一段自然语言的 reflection
```

外加一个数据结构:

```
Episodic memory: 一个由先前 reflection 组成的 list,prepend 到下一次 trial 的 prompt 前面
```

一次 trial 跑 Actor。Evaluator 给它打分。如果分低,Self-Reflector 产出一段 reflection("我选错了 tool,因为我把问题误读成在问 X,其实它问的是 Y")。这段 reflection 进 episodic memory。下一次 trial **从头开始,但看得到这段 reflection**。

### 三种 evaluator 类型 (Three evaluator types)

1. **Scalar** —— 一个外部的二元信号。ALFWorld 成功或失败。HumanEval 测试通过或不通过。最简单、信号最强。
2. **Heuristic** —— 预定义的 failure signature(失败特征)。"如果 agent 连续两次产出相同 action,标记为卡住。""如果 trajectory 超过 50 步,标记为低效。"
3. **Self-evaluated** —— LLM 给自己的 trajectory 打分。在没有 ground truth 时需要它。信号较弱;和 tool-grounded verification 搭配很好(Lesson 05 —— CRITIC)。

2026 的默认做法是混用:有 scalar 用 scalar,没有就 self-eval,heuristic 当安全护栏。

### 为什么这能泛化

Reflexion 与其说是一个新算法,不如说是一个**命名的模式**。几乎每个生产级"自愈"agent 都跑着某种变体:

- Letta 的 sleep-time compute(Lesson 08):一个独立的 agent 反思过去的对话,写进 memory block。
- Claude Code 的 `CLAUDE.md` / "save memory" 模式:reflection 被捕获成 learnings,prepend 进未来的 session。
- pro-workflow 的 `/learn-rule` 命令:把纠正捕获成显式 rule。
- LangGraph 的 reflection node:一个 node 给 output 打分,需要时路由去 refine。

它们都源自同一个洞察:**自然语言是一种足够丰富的介质,能在 run 之间携带"我从失败里学到了什么"。**

### 什么时候有用、什么时候没用

Reflexion 有用,当:
- 有清晰的 failure signal(测试失败、tool error、答案错)。
- 任务类型可复现(同一类问题可以再被问一次)。
- reflection 有改进 trajectory 的余地(action budget 够)。

Reflexion 没用,当:
- agent 第一次就成功了。
- 失败是外部原因(网络挂了、tool 坏了)—— 反思"网络挂了"对未来的 run 没帮助。
- reflection 变成了**迷信**(superstition)—— 把一次偶发的 flaky run 编成一段叙事存下来。

**2026 的坑:memory rot(记忆腐烂)。** reflection 不断累积;有些过时或错误;re-run 随 episodic buffer 增长而变慢。缓解:周期性 compaction(Lesson 06)、给 reflection 加 TTL、或一个独立的 sleep-time 清理 agent(Letta)。

## 动手做 (Build It)

`code/main.py` 在一个 toy puzzle 上实现 Reflexion:产出一个三元素的 list,使其和等于某个 target。Actor 产出候选 list;Evaluator 检查和;Self-Reflector 写一行"哪里错了"。这段 reflection 进 episodic memory 供下一次 trial 用。

组件:

- `Actor` —— 一个脚本化的 policy,看到 reflection 时会改进。
- `Evaluator.binary()` —— 对 target sum 做 pass/fail。
- `SelfReflector` —— 生成一行失败诊断。
- `EpisodicMemory` —— 一个带 TTL 语义的有界 list。

运行它:

```
python3 code/main.py
```

trace 显示三次 trial。trial 1 失败,存一段 reflection;trial 2 看到 reflection 有改进但仍失败;trial 3 成功。和一个 baseline run(无 reflection)对比 —— 它会一直卡在 trial 1 的答案上。

## 用起来 (Use It)

LangGraph 把 reflection 作为一个 node 模式提供。Claude Code 的 `/memory` 命令和 pro-workflow 的 `/learn-rule` 把 episodic buffer 外化成一个 markdown 文件。Letta 的 sleep-time compute 在停机时跑 Self-Reflector,让主 agent 保持 latency-bound(受延迟约束)。OpenAI Agents SDK 不直接提供 Reflexion;你用一个自定义 Guardrail(按分数拒绝 trajectory)加一个能跨 run 存活的 memory `Session` 来搭它。

## 交付出去 (Ship It)

`outputs/skill-reflexion-buffer.md` 创建并维护一个 episodic buffer,带 reflection 捕获、TTL 和去重。给定一个任务类型和一次失败,它产出一段**真能帮到下一次 trial** 的 reflection(而不是泛泛的"小心点")。

## 练习 (Exercises)

1. 从 binary 切换到返回距离度量(离 target 多远)的 scalar evaluator。收敛更快吗?
2. 给 reflection 加一个 10 次 trial 的 TTL。过了这个点后,旧 reflection 是帮忙还是添乱?
3. 实现 heuristic evaluator:同一 action 重复就标记为卡住。它和 Self-Reflector 怎么互动?
4. 用一个无视 reflection 的对抗式 Actor 跑 Reflexion。要让 Actor 注意到 reflection,最少需要多少 reflection prompt engineering?
5. 读 Reflexion 论文第 4 节关于 AlfWorld 的部分。在概念上复现那 130% 的成功率提升:相对 vanilla ReAct 的关键 delta 是什么?

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Reflexion | "Self-correction" | Shinn et al. 2023 —— Actor、Evaluator、Self-Reflector 加 episodic memory |
| Verbal reinforcement | "无梯度学习" | prepend 到下一次 trial prompt 的自然语言 reflection |
| Episodic memory | "per-task reflections" | 一个任务类型的、由先前 reflection 组成的有界 buffer |
| Scalar evaluator | "二元成功信号" | 来自 ground truth 的 pass/fail 或数值分 |
| Heuristic evaluator | "基于模式的检测器" | 预定义的 failure signature(如 stuck-loop、步数过多) |
| Self-evaluator | "LLM-as-judge 评自己的 trace" | 没 ground truth 时的弱信号兜底 —— 要和 tool-grounded verification 搭配 |
| Memory rot | "陈旧的 reflection" | episodic buffer 塞满过时条目;用 compaction/TTL 修 |
| Sleep-time reflection | "异步自反思" | 把 Self-Reflector 放在热路径之外跑,让主 agent 保持快 |

## 延伸阅读 (Further Reading)

- [Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning (arXiv:2303.11366)](https://arxiv.org/abs/2303.11366) —— 那篇标准论文
- [Letta, Sleep-time Compute](https://www.letta.com/blog/sleep-time-compute) —— 生产中的异步反思
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) —— 把 episodic buffer 作为 context 的一部分来管理
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) —— reflection node 模式
