# Self-Refine and CRITIC:迭代式输出改进 (Iterative Output Improvement)

> Self-Refine(Madaan 等人,2023)用一个 LLM 扮三个角色——generate、feedback、refine——跑一个 loop。平均增益:7 个任务上绝对值 +20。CRITIC(Gou 等人,2023)通过把验证步骤路由到外部工具,强化了 feedback 那一步。2026 年这个模式在每个框架里都有,叫 "evaluator-optimizer"(Anthropic)或 guardrail loop(OpenAI Agents SDK)。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 01 (Agent Loop)、Phase 14 · 03 (Reflexion)
**Time:** ~60 分钟

## 学习目标 (Learning Objectives)

- 说出 Self-Refine 的三个 prompt(generate、feedback、refine),并解释为什么 history 对 refine prompt 很重要。
- 解释 CRITIC 的关键洞察:LLM 在没有外部 grounding 时,自我验证(self-verification)不可靠。
- 实现一个 stdlib 的 Self-Refine loop,带 history 和一个可选的外部 verifier。
- 把这个模式对应到 Anthropic 的 "evaluator-optimizer" workflow 和 OpenAI Agents SDK 的 output guardrail。

## 问题所在 (The Problem)

一个 agent 产出了一个**几乎正确**的答案。也许一行代码有语法错。也许 summary 太长。也许一个 plan 漏了一个 edge case。你想要的是:agent **批判自己的输出,然后修好它**。

Self-Refine 证明这件事用单个模型就行,不需要训练数据、不需要 RL。但有个陷阱:**LLM 在硬事实上的自我验证很差**。CRITIC 点明了解法——把 verify 步骤**路由到外部工具**(search、code interpreter、calculator、test runner)。

这两篇论文合起来,定义了 2026 年迭代改进的默认范式:**generate、verify(尽量用外部)、refine,verifier 通过就停。**

## 核心概念 (The Concept)

### Self-Refine(Madaan 等人,NeurIPS 2023)

一个 LLM,三个角色:

```
generate(task)            -> output_0
feedback(task, output_0)  -> critique_0
refine(task, output_0, critique_0, history) -> output_1
feedback(task, output_1)  -> critique_1
refine(task, output_1, critique_1, history) -> output_2
...
当 feedback 说"no issues"或预算耗尽时停。
```

**关键细节:`refine` 看得到完整 history** —— 所有先前的 output 和 critique —— 所以它不会重复犯错。论文做了消融实验:去掉 history,质量急剧下降。

头条:跨 7 个任务(数学、代码、acronym、对话)平均绝对值 +20(含 GPT-4)。无训练、无外部工具、单模型。

### CRITIC(Gou 等人,arXiv:2305.11738,v4 2024 年 2 月)

Self-Refine 的弱点:feedback 步骤是 **LLM 给自己打分**。对事实性论断这不可靠(一个 hallucination 在产生它的模型看来往往很有说服力)。CRITIC 把 `feedback(task, output)` 换成 `verify(task, output, tools)`,其中 `tools` 包括:

- 一个 search engine 查事实性论断。
- 一个 code interpreter 查代码正确性。
- 一个 calculator 查算术。
- 领域特定 verifier(unit test、type checker、linter)。

verifier 产出一个**锚定在 tool 结果上**的结构化 critique。refiner 再以这个 critique 为条件。

头条:在事实性任务上 CRITIC 优于 Self-Refine,因为 critique 是 grounded 的。在没有外部 verifier 的任务上(创意写作、格式化),**CRITIC 退化成 Self-Refine**。

### stop condition(停止条件)

两种常见形态:

1. **Verifier passes(验证器通过)。** 外部测试返回成功。有的话首选(unit test、type checker、guardrail 断言)。
2. **No feedback issued(没提出反馈)。** 模型说"输出没问题"。更便宜但不可靠;要配一个 max-iteration 上限。

2026 默认:**两者结合**。"如果 verifier 通过 OR(模型说没问题 AND 迭代 >= 2)OR 迭代 >= max_iterations 就停。"

### Evaluator-Optimizer(Anthropic,2024)

Anthropic 2024 年 12 月的博文把这个列为五种 workflow pattern 之一。两个角色:

- Evaluator:给输出打分并产出 critique。
- Optimizer:根据 critique 修订输出。

循环到 evaluator 通过。这就是 Anthropic 框架下的 Self-Refine/CRITIC。Anthropic 加的关键工程细节:**evaluator 和 optimizer 的 prompt 应当显著不同**,这样模型才不会只是橡皮图章式地盖个"通过"。

### OpenAI Agents SDK 的 output guardrail

OpenAI Agents SDK 把这个模式作为 "output guardrail" 提供。一个 guardrail 是跑在 agent 最终输出上的 validator。如果 guardrail 触发(抛 `OutputGuardrailTripwireTriggered`),输出被拒,agent 可以重试。guardrail 可以调工具(CRITIC 式)或是纯函数(Self-Refine 式)。

### 2026 的坑 (2026 pitfalls)

- **Rubber-stamp loop(橡皮图章循环)。** 同一个模型用同样的 prompt 风格做生成又做批判,会收敛到"我看挺好"。用**结构上不同**的 prompt,或用一个便宜的小模型做 critique。
- **Over-refinement(过度精修)。** 每一轮 refine 都加延迟和 token。预算 1-3 轮;之后升级到人工 review。
- **在琐碎任务上用 CRITIC。** 如果没有外部 verifier,CRITIC 退化成 Self-Refine;别为一个空壳 verifier 付延迟。

## 动手做 (Build It)

`code/main.py` 在一个 toy 任务上实现 Self-Refine 和 CRITIC:给定一个主题,产出一个短 bullet list。verifier 检查格式(3 条 bullet,每条 60 字符以内)。CRITIC 加一个外部"fact verifier",惩罚已知的 hallucination。

组件:

- `generate` —— 脚本化生产者。
- `feedback` —— LLM 式自我批判。
- `verify_external` —— CRITIC 式 grounded verifier。
- `refine` —— 给定 history 重写输出。
- Stop condition —— verifier 通过或最多 4 轮迭代。

运行它:

```
python3 code/main.py
```

对比 Self-Refine 和 CRITIC 两个 run。CRITIC 抓到一个 Self-Refine 漏掉的事实错误,因为外部 verifier 有 self-critic 没有的 grounding。

## 用起来 (Use It)

Anthropic 的 evaluator-optimizer 就是这个模式的 Claude 友好表述。OpenAI Agents SDK 的 output guardrail 是 CRITIC 形状的(guardrail 能调工具)。LangGraph 提供一个读起来像 Self-Refine 的 reflection node。Google 的 Gemini 2.5 Computer Use 加了一个 per-step 安全 evaluator,是 CRITIC 变体:每个 action 在 commit 前都被验证。

## 交付出去 (Ship It)

`outputs/skill-refine-loop.md` 在给定任务形状、verifier 可用性、迭代预算的情况下,配置一个 evaluator-optimizer loop。产出 generator、evaluator/verifier、optimizer 的 prompt,加一个 stop policy。

## 练习 (Exercises)

1. 用 max_iterations=1 跑这个 toy。CRITIC 还有帮助吗?
2. 把外部 verifier 换成一个嘈杂的(随机 30% 假阳性)。loop 会怎样?这是 2026 大多数 guardrail 栈的现实。
3. 实现一个"generator-critic 用不同模型"的变体:大模型生成,小模型批判。它能打败同模型吗?
4. 读 CRITIC 第 3 节(arXiv:2305.11738 v4)。说出三类 verification-tool,各举一例。
5. 把 OpenAI Agents SDK 的 `output_guardrails` 对应到 CRITIC 的 verifier 角色。SDK 哪里做错了、哪里做对了?

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Self-Refine | "会自我修复的 LLM" | 单模型里的 generate -> feedback -> refine loop,带 history |
| CRITIC | "工具锚定的验证" | 把 feedback 换成外部 verifier(search、code、calc、test) |
| Evaluator-Optimizer | "Anthropic 的 workflow pattern" | 两角色——evaluator 打分,optimizer 修订——循环到收敛 |
| Output guardrail | "事后检查" | OpenAI Agents SDK 在 agent 产出输出后跑的 validator |
| Verify step | "批判阶段" | 承重的决策:grounded 还是 self-rated |
| Refine history | "模型已经试过什么" | 先前 output + critique,prepend 到 refine prompt;去掉则质量崩 |
| Rubber-stamp loop | "自我认同失败" | 同 prompt 批判返回"看着挺好";用结构不同的 prompt 修 |
| Stop condition | "收敛测试" | verifier 通过 OR(无反馈 AND 迭代上限);绝不用单一条件 |

## 延伸阅读 (Further Reading)

- [Madaan et al., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) —— 那篇标准论文
- [Gou et al., CRITIC (arXiv:2305.11738)](https://arxiv.org/abs/2305.11738) —— 工具锚定的验证
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) —— evaluator-optimizer workflow pattern
- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) —— output guardrail 作为 CRITIC 形状的 verifier
