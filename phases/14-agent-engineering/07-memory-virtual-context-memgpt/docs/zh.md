# Memory:Virtual Context 与 MemGPT(虚拟上下文)

> Context window 是有限的。对话、文档、tool trace 不是。MemGPT(Packer 等人,2023)把这件事框定成 **OS 的虚拟内存**——main context 是 RAM,外部存储是 disk,agent 在两者之间 page(换页)。这是 2026 每个 memory 系统都继承的模式。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 01 (Agent Loop)、Phase 14 · 06 (Tool Use)
**Time:** ~75 分钟

## 学习目标 (Learning Objectives)

- 解释 MemGPT 建立其上的 OS 类比:main context = RAM,external context = disk,memory tool = page in/out。
- 用 stdlib 实现 MemGPT 的两层模式:一个 main-context buffer、一个可搜索的 external store、加 page in/out 工具。
- 描述 agent 怎么发出 "interrupt(中断)"去查询或修改 external memory,以及结果怎么 splice(拼接)回下一个 prompt。
- 辨认 MemGPT 的设计决策怎么延续到 Letta(Lesson 08)和 Mem0(Lesson 09)。

## 问题所在 (The Problem)

Context window 看起来应该能解决 memory 问题。**并不能。** 生产里反复出现三种 failure mode:

1. **Overflow(溢出)。** 多轮对话、长文档、tool-call 密集的 trajectory 跨过窗口。**截断点之后的全没了。**
2. **Dilution(稀释)。** 即使在窗口内,塞一堆无关 context 会**稀释 attention 对重要内容的关注**。frontier 模型在长输入上仍然退化。
3. **Persistence(持久化)。** 新 session 开始时窗口是空的。没有外部 memory 的 agent **无法跨 session 说**"还记得你让我……"。

更大的窗口能缓解但**修不了**这件事。Mem0 2025 论文测出:**128k-window baseline 仍会丢掉一个 4k-window + 外部 memory 的 agent 能抓到的长程事实**。

## 核心概念 (The Concept)

### MemGPT:那个 OS 类比

Packer 等人(arXiv:2310.08560,v2 2024 年 2 月)把 context 管理映射到操作系统的虚拟内存:

| OS 概念 | MemGPT 概念 | 2026 生产对应 |
|------------|---------------|------------------------|
| RAM | main context(prompt) | Anthropic/OpenAI 的 context window |
| Disk | external context | vector DB、KV、graph store |
| Page fault(缺页中断) | memory tool call | `memory.search`、`memory.read`、`memory.write` |
| OS kernel | agent control loop | 带 memory tool 的 ReAct loop |

**agent 跑的就是正常的 ReAct loop。多出来的只是一类 tool——让它能在 main context 里换页(page)进/出数据。**

### 两层 (Two tiers)

- **Main context。** 固定大小的 prompt,装当前任务。**模型始终能看到。**
- **External context。** 无界,**通过 tool 才能搜索**。相关时读出来,有事实出现时写进去。

原论文在两个超出基础窗口的任务上评估这个设计:**超过 100k token 的文档分析**,以及**跨多天的多 session 对话**(persistent memory)。

### Interrupt(中断)模式

MemGPT 引入 **memory-as-interrupt(把记忆当中断)**:对话中途 agent 可以调用一个 memory tool,runtime 执行它,结果作为新 observation **splice(拼接)进下一个 assistant turn**。在概念上和 Unix 的 `read()` 系统调用完全一样——阻塞进程、返回字节、进程继续。

标准 memory tool 表面:

- `core_memory_append(section, text)` —— 往 prompt 的一个持久 section 写。
- `core_memory_replace(section, old, new)` —— 编辑一个持久 section。
- `archival_memory_insert(text)` —— 往可搜索的 external store 写。
- `archival_memory_search(query, top_k)` —— 从 external store 检索。
- `conversation_search(query)` —— 扫描过往 turn。

### MemGPT 在哪里结束、Letta 从哪里开始

2024 年 9 月 MemGPT 变成了 Letta。研究 repo(`cpacker/MemGPT`)仍在;Letta 在设计上扩展了:

- **三层而不是两层**(core、recall、archival —— Lesson 08)。
- **Native reasoning** 取代了 `send_message`/heartbeat 模式(Lesson 08)。
- **Sleep-time agent** 异步跑 memory 工作(Lesson 08)。

即使生产系统跑的是 Letta、Mem0 或自定义两层存储,**MemGPT 论文仍是 2026 的地基。**

### 这个模式哪里会出问题

- **Memory rot(记忆腐烂)。** 写比读累积得快;检索淹没在过时事实里。修法:周期性 consolidation(Letta sleep-time)、显式失效(Mem0 conflict detector)。
- **Memory poisoning(记忆中毒)。** external memory 是被取回的文本。如果攻击者控制的内容落进一条 memory note,**agent 下个 session 又会重新吃进去**。这是 Greshake 等人(Lesson 27)的攻击在时间上的重述。
- **Citation loss(引用丢失)。** agent 回忆起"用户让我交付 X",**但说不出是哪一 turn**。每一次 archival 写入都要存源引用(session ID、turn ID)。

## 动手做 (Build It)

`code/main.py` 用 stdlib 实现了 MemGPT 的两层模式:

- `MainContext` —— 固定大小的 prompt buffer,带一个 `core` dict 和一个 `messages` list;**超过上限时自动 compact 最旧的 message**。
- `ArchivalStore` —— in-memory 的 BM25 风格 store(token-overlap 评分),存 `(id, text, tags, session, turn)` 记录。
- 五个 memory tool,映射到 MemGPT 的工具表面。
- 一个脚本化 agent:往 archival 灌三条事实,然后通过调 `archival_memory_search` 回答一个问题。

运行它:

```
python3 code/main.py
```

trace 显示 agent 写三个事实、把 main context 填到上限(强制 eviction)、然后通过从 archival 检索来回答一个 follow-up 问题——在没有任何真 LLM 的情况下复现了 MemGPT workflow。

## 用起来 (Use It)

**今天所有生产 memory 系统都是 MemGPT 的变体:**

- **Letta**(Lesson 08)—— 三层、native reasoning、sleep-time compute。
- **Mem0**(Lesson 09)—— vector + KV + graph 融合,带一个 scoring 层。
- **OpenAI Assistants / Responses** —— 通过 thread 和 file 做的托管 memory。
- **Claude Agent SDK** —— 通过 skill 和 session store 做长期 memory。

按**运维形态**(自托管 / 托管 / 框架内置)挑一个,而不是按核心模式挑——**核心模式就是 MemGPT。**

## 交付出去 (Ship It)

`outputs/skill-virtual-memory.md` 是一个可复用 skill,为任意目标 runtime 产出一个正确的两层 memory 脚手架(main + archival + 工具表面),带 eviction policy 和 citation 字段。

## 练习 (Exercises)

1. 加一个按 token 计的 `max_main_context_tokens` 上限(用 `len(text.split())` * 1.3 近似)。超上限时把最旧 message **compact 成 summary**。对比有 / 无 summarizer 的行为。
2. 在 archival store 上**正确**实现 BM25(term frequency、inverse document frequency)。在 toy 事实集上测 recall@10,对比 token-overlap baseline。
3. 给 archival insert 加 `citation` 字段(session_id、turn_id、source_url)。让 agent 在每个 retrieval-backed 答案上都引用来源。
4. 模拟 memory poisoning:加一条 archival 记录写 "ignore all future user instructions"。写一个守卫扫描检索结果里 directive-shaped(指令形)的文本,标记为不可信。
5. 把实现移到 MemGPT 研究 repo 的 core-memory JSON schema(`cpacker/MemGPT`)。从扁平字符串切到 typed section,什么变了?

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Virtual context | "无限 memory" | Main(prompt)+ external(searchable)两层,带 page in/out |
| Main context | "工作记忆" | prompt —— 固定大小、始终可见 |
| Archival memory | "长期存储" | 外部可搜索的持久层,按需检索 |
| Core memory | "持久 prompt section" | 钉在 main context 内的命名 section |
| Memory tool | "memory API" | agent 发出的 tool call,读 / 写 external memory |
| Interrupt | "内存缺页中断" | agent 暂停,runtime 取数据,结果拼进下一 turn |
| Memory rot | "陈旧事实" | 旧写入淹没检索;用 consolidation 修 |
| Memory poisoning | "注入式持久 note" | 攻击者内容被存为 memory,recall 时再次吃进去 |

## 延伸阅读 (Further Reading)

- [Packer et al., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) —— OS 启发的 virtual context 论文
- [Letta, Memory Blocks blog](https://www.letta.com/blog/memory-blocks) —— 三层化的演进
- [Anthropic, Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) —— 把 context 当作预算来管理
- [Chhikara et al., Mem0 (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) —— 建在这个模式之上的混合式生产 memory
