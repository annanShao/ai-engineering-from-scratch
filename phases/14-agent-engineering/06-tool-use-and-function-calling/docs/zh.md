# Tool Use and Function Calling(工具使用与函数调用)

> Toolformer(Schick 等人,2023)开启了 self-supervised 的 tool annotation。Berkeley Function Calling Leaderboard V4(Patil 等人,2025)设定了 2026 的标杆:40% agentic、30% multi-turn、10% live、10% non-live、10% hallucination。单轮(single-turn)已被解决。memory、动态决策、长程 tool chain 还没有。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 01 (Agent Loop)、Phase 13 · 01 (Function Calling Deep Dive)
**Time:** ~60 分钟

## 学习目标 (Learning Objectives)

- 解释 Toolformer 的 self-supervised 训练信号:只在"执行 tool 能降低 next-token loss"时才保留这条 tool annotation。
- 说出 BFCL V4 的五个评估类别,以及各自测什么。
- 实现一个 stdlib 的 tool registry,带 schema 校验、参数 coercion(强制转换)和执行 sandboxing。
- 诊断 2026 的三个开放难题:长程 tool chaining、动态决策、memory。

## 问题所在 (The Problem)

早期 tool use 问的是:模型能不能**预测出一个正确的函数调用**?现代 tool use 问的是:模型能不能在 **40 步**里串起多个 tool,带着 memory、在部分可观测下、能从 tool 失败中恢复、且**不幻觉出不存在的 tool**?

Toolformer 立了 baseline:模型能用 self-supervision 学会**何时**调 tool。BFCL V4 定义了 2026 的评估目标。这两者之间的 gap,就是生产 agent 生活的空间。

## 核心概念 (The Concept)

### Toolformer(Schick 等人,NeurIPS 2023)

想法:让模型**给自己的预训练语料标注候选 API call**。对每个候选,执行它。**只有当"包含这个 tool 结果"能降低下一个 token 的 loss 时,才保留这条标注。** 在过滤后的语料上做 fine-tune。

覆盖的 tool:calculator、QA 系统、search engine、translator、calendar。self-supervision 信号纯粹关于"这个 tool 帮不帮助预测文本"——**没有人工标注**。

规模结果:**tool use 是随规模涌现的(emerges at scale)**。小模型被 tool annotation 拖累;大模型获益。这就是为什么 2026 frontier 模型自带强 tool use,而大多数 7B 模型需要显式 tool-use fine-tune 才可靠。

### Berkeley Function Calling Leaderboard V4(Patil 等人,ICML 2025)

BFCL 是 2026 事实上的评估标准。V4 构成:

- **Agentic(40%)** —— 完整 agent trajectory:memory、multi-turn、动态决策。
- **Multi-Turn(30%)** —— 带 tool chain 的交互式对话。
- **Live(10%)** —— 用户提交的真实 prompt(更难的分布)。
- **Non-Live(10%)** —— 合成测试用例。
- **Hallucination(10%)** —— 检测"什么时候不该调任何 tool"。

V3 引入了 **state-based evaluation(基于状态的评估)**:一段 tool 序列之后,检查 API 的**实际状态**(如"文件创建了吗?"),而不是去匹配 tool call 的 AST。V4 加了 web search、memory、format sensitivity 类别。

2026 关键发现:**单轮 function calling 近乎解决**。失败集中在 memory(跨轮携带上下文)、动态决策(基于先前结果选 tool)、长程 chain(20+ 步后 drift)、以及 hallucination 检测(没有合适 tool 时拒绝调用)。

### Tool schema(工具 schema)

每个 provider 都有一套 schema。细节不同,但共享同一个形状:

```
name: string
description: string(它干啥、何时用)
input_schema: JSON Schema(properties、required、types、enums)
```

Anthropic 直接用 `input_schema`。OpenAI 用 `function.parameters`。两者都吃 JSON Schema。**description 是承重的** —— 模型读它来挑对的 tool。**烂的 tool description 是"选错 tool"失败的头号根因。**

### Argument validation(参数校验)

**不要信任任何 tool call。** 校验:

1. **Type coercion(类型强制转换)。** 模型可能在 schema 要 int 的地方返回字符串 `"5"`。无歧义就转换;有歧义就拒绝。
2. **Enum validation。** schema 说 `status in {"open","closed"}`,模型吐了 `"in_progress"` → 用描述性 error 拒绝。
3. **Required fields。** 缺必填字段 → 立刻把 error observation 喂回模型,**不是 crash**。
4. **Format validation。** 日期、email、URL —— 用具体的 parser 校验,别用 regex。

每个校验失败都该返回一个**结构化 observation**,让模型能带着正确的形状重试。

### Parallel tool calls(并行工具调用)

现代 provider 支持在一个 assistant turn 里并行调多个 tool。loop:

1. 模型发出 3 个 tool call,带各不相同的 `tool_use_id`。
2. runtime 执行它们(独立的话就并行)。
3. 每个结果作为一个 `tool_result` block 送回,**按 `tool_use_id` 关联**。

工程铁律:**把 correlation ID 当承重件**。交换它们,你会得到"错的 tool 配错的结果"的路由错误。

### Sandboxing(沙箱)

tool 执行是 sandbox 边界。详见 Lesson 09。简版:每个 tool 都该指定 read/write surface、网络访问、timeout、内存上限。通用的 `run_shell(cmd)` 是危险信号;具体的 `git_status()` 更安全。

## 动手做 (Build It)

`code/main.py` 实现了一个生产形状的 tool registry:

- JSON Schema 子集 validator(纯 stdlib)。
- 带 description、input schema、timeout、executor 的 tool 注册。
- 参数 coercion 和 enum 校验。
- 带 correlation ID 的并行 tool dispatch。
- error observation 作为结构化字符串。

运行它:

```
python3 code/main.py
```

trace 显示一个 mini agent 在一个 turn 里调三个 tool,其中一个**故意写坏的 call** 被一个"模型可据此行动的描述性 error"拒绝。

## 用起来 (Use It)

每个 provider 都有自己的 tool schema —— Anthropic、OpenAI、Gemini、Bedrock。如果需要多 provider,用一个翻译层(OpenAI Agents SDK、Vercel AI SDK、LangChain tool adapter)。BFCL 是参考 benchmark —— 如果 tool use 是产品核心,上线前拿它跑一遍你的 agent。

## 交付出去 (Ship It)

`outputs/skill-tool-registry.md` 为给定任务域生成一个 tool catalog、schema 和 registry。含 description 质量检查(每个 tool 的 description 有没有告诉模型何时用它?)。

## 练习 (Exercises)

1. 加一个 "no-op" tool,让模型能显式拒绝使用任何别的 tool。在一个 BFCL 式 hallucination 测试上测量。
2. 为 int-as-string 和 float-as-string 实现参数 coercion。coercion 从哪里开始会**掩盖真正的 bug**?
3. 加一个 per-tool timeout 和一个 circuit breaker(连续 3 次失败后拒绝该 tool 60 秒)。这对模型如何恢复有什么改变?
4. 读 BFCL V4 描述。挑一个类别(如 "multi-turn"),跑 10 个示例 prompt 过你的 agent。报告 pass rate。
5. 把 stdlib validator 移植到 Pydantic 或 Zod。Pydantic/Zod 抓到了 toy 漏掉的什么?

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Function calling | "Tool use" | 带校验 schema 的结构化输出 tool 调用 |
| Toolformer | "self-supervised tool annotation" | Schick 2023 —— 保留那些"结果能降低 next-token loss"的 tool call |
| BFCL | "Berkeley Function Calling Leaderboard" | 2026 benchmark:40% agentic、30% multi-turn、10% live、10% non-live、10% hallucination |
| Tool schema | "给模型的函数签名" | name、description、参数的 JSON Schema |
| tool_use_id | "Correlation ID" | 把一个 tool call 和它的结果绑定;并行 dispatch 必备 |
| Hallucination detection | "知道何时不该调" | V4 类别:没有合适 tool 时拒绝调用 |
| Argument coercion | "string 转 int 修复" | 对可预测 schema 不匹配的窄修;有歧义则拒绝 |
| Sandboxing | "tool 执行边界" | per-tool 的 read/write surface、网络、timeout、内存上限 |

## 延伸阅读 (Further Reading)

- [Schick et al., Toolformer (arXiv:2302.04761)](https://arxiv.org/abs/2302.04761) —— self-supervised tool annotation
- [Berkeley Function Calling Leaderboard (V4)](https://gorilla.cs.berkeley.edu/leaderboard.html) —— 2026 eval benchmark
- [Anthropic, Tool use documentation](https://platform.claude.com/docs/en/agent-sdk/overview) —— Claude Agent SDK 里的生产 tool schema
- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) —— function tool type 和 Guardrails
