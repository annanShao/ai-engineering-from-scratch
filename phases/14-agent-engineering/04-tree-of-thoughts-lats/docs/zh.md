# Tree of Thoughts and LATS:刻意搜索 (Deliberate Search)

> 单条 chain-of-thought 的 trajectory 没有回溯的余地。ToT(Yao 等人,2023)把推理变成一棵树,每个 node 上都做 self-evaluation。LATS(Zhou 等人,2024)在 Monte Carlo Tree Search(MCTS)框架下把 ToT、ReAct、Reflexion 统一起来。Game of 24 从 4%(CoT)涨到 74%(ToT);LATS 在 HumanEval 上打到 92.7% pass@1。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 01 (Agent Loop)、Phase 14 · 03 (Reflexion)
**Time:** ~75 分钟

## 学习目标 (Learning Objectives)

- 把推理框定为搜索:node 是"thought",edge 是"expansion",value 是"有多 promising"。
- 实现一个 stdlib 的 ToT 式 BFS 树搜索,带 self-evaluation 打分。
- 扩展成一个 toy LATS MCTS loop,含 select / expand / simulate / backpropagate。
- 判断什么时候搜索值得那个 token 倍率(Game of 24、代码生成),什么时候单条 trajectory 就够(简单 Q&A)。

## 问题所在 (The Problem)

Chain-of-thought 是一次**线性行走**。如果第一步错了,后面每一步都建立在错误前提上。在 Game of 24(用四个数字 + − × ÷ 凑出 24)上,GPT-4 CoT 只有 4% 准确率。模型早早选错了子表达式,然后**无法恢复**。

推理需要的是:**提出多个候选、评估它们、挑出 promising 的、遇到死路时回溯**的能力。这就是搜索(search)。Tree of Thoughts 和 LATS 是两个标准表述。

## 核心概念 (The Concept)

### Tree of Thoughts(Yao 等人,NeurIPS 2023)

每个 node 是一个连贯的中间步骤("一个 thought")。每个 node 可以 expand 出 K 个子 thought。LLM 用一个打分 prompt 对每个 node 做 self-evaluate。搜索去探索这棵树 —— BFS、DFS 或 beam。

```
                     (root: "find 24 from 4 6 4 1")
                    /               |            \
           ("6 - 4 = 2")    ("4 + 1 = 5")    ("4 * 6 = 24")  <- Score: HIGH
              /   \              |                  |
          ...    ...          ...                finish
```

**self-evaluation 是承重件。** 论文给了三种变体:`sure / likely / impossible` 分类、`1..10` 数值打分、候选间投票。三种在 Game of 24 上都大幅打败 CoT(GPT-4 下 4% -> 74%)。

### LATS(Zhou 等人,ICML 2024)

LATS 在 MCTS 下统一了 ToT、ReAct 和 Reflexion。LLM 扮演三个角色:

- **Policy**:提出候选的下一步 action(ReAct 式)。
- **Value function**:给一条部分 trajectory 打分(ToT 式 self-eval)。
- **Self-reflector**:失败时写一段自然语言 reflection(Reflexion 式),并用它给未来的 rollout 重新播种(reseed)。

环境反馈(observation)被混进 value function,所以搜索是被**真实 tool 结果**告知的,而不只是模型意见。论文当时结果:HumanEval pass@1 92.7%(GPT-4,SOTA),WebShop 平均 75.9(GPT-3.5,逼近基于梯度的 fine-tuning)。

### MCTS,最小版 (MCTS, minimally)

每次迭代四个阶段:

1. **Select** —— 用 UCT(树的置信上界)从 root 走到一个 leaf。
2. **Expand** —— 通过 policy 生成 K 个子节点。
3. **Simulate** —— 从一个子节点用 policy 做 rollout,用 value function(或环境 reward)给 leaf 打分。
4. **Backpropagate** —— 沿路径向上更新 visit count 和 value 估计。

UCT 公式:`Q(s, a) + c * sqrt(ln N(s) / N(s, a))`。第一项是 exploitation(利用);第二项是 exploration(探索)。`c` 按任务调。

### 成本现实 (The cost reality)

搜索会让 token **爆炸**。ToT 在 Game of 24 上用掉 CoT 的 100–1000 倍 token。LATS 类似。这不是免费的;把搜索留给:

- 单条 trajectory **明显不够**的任务(Game of 24、复杂代码)。
- wall-clock(墙钟时间)不如正确性重要的任务。
- 有一个**便宜、可靠的 value function** 的任务(代码的 unit test、数学的显式 target)。

如果你的任务有唯一正确答案、但 evaluator 很嘈杂,搜索往往**让事情更糟** —— 它会找到一个"打分很高"的错误答案。

### 2026 定位 (2026 positioning)

大多数生产 agent **不跑 LATS**。它们跑的是带 tool-grounded verification 的 ReAct(CRITIC,Lesson 05)。搜索出现在一些专门的小生境里:

- 把跑测试当 value function 的 coding agent(HumanEval 式)。
- 探索多条 query 路径的 deep-research agent。
- LangGraph subgraph 里规划密集的 workflow。

AlphaEvolve(Lesson 11)是 2025 年的极端案例:在代码上做演化搜索,机器可验证的 fitness,frontier 级增益(56 年来首次改进 4x4 矩阵乘法)。

## 动手做 (Build It)

`code/main.py` 实现了:

- 在一个风格化的"挑算术运算"任务上的小型 ToT BFS。
- 同一任务上的 toy LATS MCTS loop(Select / Expand / Simulate / Backpropagate),带 UCT 选择。
- 一个 value function,组合了一个符号分数加一个 self-eval 分数。

运行它:

```
python3 code/main.py
```

trace 显示 ToT 用 BFS 每个 node 展开三个候选,对比 LATS 通过 MCTS 收敛到最佳 rollout。两者的 token 计数都会打印。

## 用起来 (Use It)

LangGraph 把 ToT 式探索作为 subgraph 模式提供;LangChain 团队关于 LATS 的博文(2024 年 5 月)是参考教程。LlamaIndex 提供一个 `TreeOfThoughts` agent。对大多数 2026 生产 agent,这个模式活在一个 `if task_complexity > threshold: use_search()` 的 gate 后面 —— 见 Lesson 05 的 evaluator-optimizer 模式。

## 交付出去 (Ship It)

`outputs/skill-search-policy.md` 在给定任务形状、预算、evaluator 保真度的情况下,在 linear ReAct、ToT、LATS、演化搜索之间做选择。

## 练习 (Exercises)

1. 用 UCT c=0.1 对比 c=2.0 跑 toy LATS。trace 里有什么变化?
2. 把 value function 换成更嘈杂的打分器(加随机抖动)。MCTS 还能找到最佳 leaf 吗?它能容忍的最低信噪比是多少?
3. 实现 beam-search ToT(每层保留 top-k),和 BFS 对比。在紧张的 token 预算下哪个更好?
4. 读 LATS 第 5.1 节。复现 HumanEval 的 trajectory 计数:打到论文报告的 pass@1 需要多少次 rollout?
5. 读 LATS 论文里"什么时候 LATS 帮助变小"的讨论。写一段决策规则,把任务形状映射到搜索策略。

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Tree of Thoughts | "分叉的 CoT" | Yao et al. —— 带 self-evaluation 的 thought node 树 |
| LATS | "给 LLM 的 MCTS" | Zhou et al. —— 在 MCTS 下统一 ToT + ReAct + Reflexion |
| UCT | "置信上界" | 平衡 exploitation(Q)和 exploration(ln N / n)的 select 公式 |
| Value function | "这个 state 有多好" | prompt 出来的 LLM 分数或环境 reward;喂给 backprop |
| Policy | "action 提议器" | ReAct 式生成器;产出候选的下一个 thought/action |
| Rollout | "模拟的 trajectory" | 用 policy 从一个 node 走到 leaf,用 value 打分 |
| Backpropagate | "更新祖先" | 把 leaf 的 reward 沿路径上推,更新 visit count 和 Q |
| Search cost | "token 爆炸" | Game of 24 上是 CoT 的 100-1000 倍;采用前先算预算 |

## 延伸阅读 (Further Reading)

- [Yao et al., Tree of Thoughts (arXiv:2305.10601)](https://arxiv.org/abs/2305.10601) —— 那篇标准论文
- [Zhou et al., LATS (arXiv:2310.04406)](https://arxiv.org/abs/2310.04406) —— 带 Reflexion 反馈的 MCTS
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) —— 搜索的 subgraph 模式
- [AlphaEvolve (arXiv:2506.13131)](https://arxiv.org/abs/2506.13131) —— 带程序化 evaluator 的演化搜索
