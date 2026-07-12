# Memory Blocks 与 Sleep-Time Compute(Letta)

> MemGPT 在 2024 年变成了 Letta。2026 的演进加了两个想法:**离散的、功能性的 memory block** —— 模型可以直接编辑;以及 **sleep-time agent** —— 主 agent 闲下来时,它在后台异步整理 memory。这就是怎么把 memory 扩展超出一次对话。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 07 (MemGPT)
**Time:** ~75 分钟

## 学习目标 (Learning Objectives)

- 说出 Letta 的三层 memory(core、recall、archival)以及各自角色。
- 解释 memory-block 模式:Human block、Persona block,以及用户自定义 block 作为**一等类型化对象**。
- 描述什么是 sleep-time compute,为什么它**不在关键路径上**,以及为什么它能跑一个比主 agent 更强的模型。
- 实现一个脚本化的双 agent loop:主 agent 服务响应,sleep-time agent 在两次 turn 之间整理 block。

## 问题所在 (The Problem)

MemGPT(Lesson 07)解决了 virtual-memory 的控制流。生产里浮现出三个问题:

1. **Latency(延迟)。** 每个 memory 操作都坐在**关键路径**上。如果 agent 要在用户等着的时候 prune / summarize / 调和事实,**尾延迟会爆炸**。
2. **Memory rot(记忆腐烂)。** 写入累积。矛盾的事实留着。检索淹没在过时内容里。
3. **Structure loss(结构丢失)。** 一个扁平的 archival store **无法表达**:"Human block 始终在 prompt 里;Persona block 始终在 prompt 里;Task block 每个 session 换。"

Letta(letta.com)是 2026 的重写。**memory block 把结构显式化,sleep-time compute 把整理工作搬下关键路径。**

## 核心概念 (The Concept)

### 三层 (Three tiers)

| 层 | 范围 | 住在哪 | 谁写 |
|------|-------|----------------|------------|
| Core | 始终可见 | 主 prompt 内 | agent tool call + sleep-time 重写 |
| Recall | 对话历史 | 可检索 | 自动 turn 日志 |
| Archival | 任意事实 | vector + KV + graph | agent tool call + sleep-time 摄入 |

Core 就是 MemGPT 的 core。Recall 就是对话 buffer(包括被 evict 的尾巴)。Archival 就是外部 store。**这个拆分清理了 MemGPT 两层模式的语义重叠。**

### Memory block

一个 block 是 core 层里**类型化、持久、可编辑**的 section。MemGPT 原论文定义了两个:

- **Human block** —— 关于用户的事实(name、role、preferences、goals)。
- **Persona block** —— agent 的自我概念(identity、tone、constraints)。

Letta **泛化成任意用户自定义 block**:`Task` block 装当前目标、`Project` block 装代码库事实、`Safety` block 装硬约束。每个 block 有 `id`、`label`、`value`、`limit`(字符上限)、`description`(让模型知道何时该编辑它)。

block 通过下面这套 tool 表面来编辑:

- `block_append(label, text)`
- `block_replace(label, old, new)`
- `block_read(label)`
- `block_summarize(label)` —— 把接近 limit 的 block 浓缩。

### Sleep-time compute

**2025 年 Letta 的关键添加**:在背景里跑**第二个 agent**,**不在关键路径上**。sleep-time agent 处理对话 transcript 和代码库 context,把 `learned_context` 写进共享 block,整理或失效 archival 记录。

它带来的几个属性:

- **零延迟成本。** 主响应不等 memory 操作。
- **允许更强的模型。** sleep-time agent 可以是更贵、更慢的模型,因为它**不受延迟约束**。
- **天然的整理窗口。** 用户不在等的时候去 dedup、summarize、失效矛盾事实。

**这个形状和人怎么工作一致**:你做任务,睡一觉,长期记忆在过夜里沉淀好。

### Letta V1 与 native reasoning

Letta V1(`letta_v1_agent`,2026)弃用了 `send_message`/heartbeat 和 inline 的 `Thought:` token,转向 **native reasoning**。Responses API(OpenAI)和带 extended thinking 的 Messages API(Anthropic)在**独立 channel** 上发出 reasoning,跨 turn 传递(生产中跨 provider 时加密)。**control loop 仍然是 ReAct。thought trace 是结构化的,不是 prompt 形状的。**

### 这个模式哪里会出问题

- **Block bloat(块膨胀)。** 无限 `block_append` 很快撞 limit。在那条会撞 cap 的写入**之前**接一个 block summarizer。
- **Silent drift(无声漂移)。** sleep-time agent 重写了一个 block,主 agent 从没注意到。**给 block 加版本,在 trace 里露出 diff。**
- **Poisoned consolidation(中毒整理)。** sleep-time agent 把攻击者可达内容**整理进 core**。Lesson 27 也适用于 sleep-time 表面。

## 动手做 (Build It)

`code/main.py` 实现了:

- `Block` —— id、label、value、limit、description。
- `BlockStore` —— CRUD + `near_limit(label)` 辅助。
- 两个脚本化 agent —— `PrimaryAgent` 服务一个 turn,`SleepTimeAgent` 在两次 turn 之间整理。
- 一个 trace,显示三轮对话(带 block 写入)+ 一次 sleep-time pass(summarize 一个 block 并失效一条过时事实)。

运行它:

```
python3 code/main.py
```

transcript 显示这个拆分:主 turn 快、产出原始写入;sleep pass 压缩并清理。

## 用起来 (Use It)

- **Letta**(letta.com)—— 参考实现。自托管或托管 cloud。
- **Claude Agent SDK skill** —— 把 skill 当作 block 形状的知识:**一个 skill 就是一个命名、有版本、可检索的指令 block,agent 按需加载**。
- **自建** —— 团队要控制 storage backend。用 Letta API 契约,以后好迁移。

## 交付出去 (Ship It)

`outputs/skill-memory-blocks.md` 为任意 runtime 产出一个 Letta 形状的 block 系统,带 sleep-time hook、安全规则、citation 接线。

## 练习 (Exercises)

1. 加一个 `block_summarize` tool,当 `near_limit` 返回 true 时用模型生成的 summary 替换 block value。**触发阈值定多少**能同时把 summarization 调用数和 block overflow 降到最小?
2. 在 archival 上实现 **sleep-time dedup**:两条 token 重叠 >90% 的记录合成一条。**只在 sleep pass 里做,绝不在关键路径上做。**
3. 给 block **加版本**。每次写入记录旧 value 和 diff。露出 `block_history(label)`,这样运维能调试"agent 为什么忘了 X"。
4. 把 sleep-time agent 当作**不可信写者**。它碰 Persona 或 Safety block 时,要求**第二个 agent 评审**才能提交。
5. 把示例移到用 Letta API(`letta_v1_agent`)。block schema 变了什么,native reasoning 怎么改变 trace 形状?

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Memory block | "可编辑的 prompt section" | core memory 里类型化、持久、LLM 可编辑的段 |
| Human block | "user memory" | 关于用户的事实,钉在 core |
| Persona block | "agent identity" | 自我概念、tone、constraints,钉在 core |
| Sleep-time compute | "async memory 工作" | 第二个 agent 在关键路径外做整理 |
| Core / Recall / Archival | "三层" | 三层 memory 拆分:始终可见 / 对话 / 外部 |
| Block limit | "上限" | 每个 block 的字符上限;强制 summarization |
| Native reasoning | "thinking channel" | provider 层的 reasoning 输出,不是 prompt 层的 `Thought:` |
| Learned context | "sleep 产出" | sleep-time agent 写进共享 block 的事实 |

## 延伸阅读 (Further Reading)

- [Letta, Memory Blocks blog](https://www.letta.com/blog/memory-blocks) —— block 模式
- [Letta, Sleep-time Compute blog](https://www.letta.com/blog/sleep-time-compute) —— 异步整理
- [Letta, Rearchitecting the Agent Loop](https://www.letta.com/blog/letta-v1-agent) —— native reasoning 重写
- [Packer et al., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) —— 起点
