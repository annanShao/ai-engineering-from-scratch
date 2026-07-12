# Lesson 07 · Memory:Virtual Context 与 MemGPT(虚拟上下文)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/07-memory-virtual-context-memgpt/` |
| 类型 | Build · ~75 分钟 |
| 前置 | Lesson 01 (Agent Loop)、Lesson 06 (Tool Use) |
| 关键文件 | `docs/zh.md`、`code/main.py`(两层 memory:MainContext + ArchivalStore + 5 tool) |
| 状态 | ✅ 完成(阅读 + 3 钩子深挖 + 代码走读 + 4 金句) |

---

## 核心金句

### #1 · OS 虚拟内存的"不变量",整套搬到了 LLM context
> **MemGPT 的核心不是"加一个外部 store",而是把 OS 虚拟内存的不变量整套搬过来:进程以为有无限内存、实际只为活跃部分付钱、OS 透明 paging。** 映射:RAM = main context、Disk = archival、Page fault = memory tool、OS kernel = ReAct loop。

一个关键差别:OS 的 page fault 是**非自愿**的(CPU 撞缺页 → OS 接管);MemGPT 的 page fault 是 agent **主动调 memory tool**。但"暂停 → 取数据 → 继续"这个形状完全一样,正是 Unix `read()` 系统调用的形状。

**这是金句 #3(Lesson 04)"留在外部"清单里"跨边界持久化"那一项的工程实现。** Lesson 03 我们说 memory 三层生命周期;这节给中间那层(跨 trial、跨 session 的持久化)做出第一个系统化设计。

### #2 · 大 context window 修不了 memory,因为 dilution 是 attention 问题不是容量问题
> **三种 failure mode:overflow / dilution / persistence。大窗口对 overflow 部分缓解、对 persistence 完全无能、对 dilution 修不了甚至更糟——dilution 不是"装不下",是模型对长输入的 attention 退化("lost in the middle")。** 所以 Mem0 测出 128k window 反而被 4k window + 外部 memory 打败:**有选择地检索 >> 无差别地塞**;外部 memory 起的是"信号过滤器"作用,把相关的捞出来,而不是把全部噪声塞进窗口。

| failure | 大窗口能修吗 | 原因 |
|---|---|---|
| Overflow | 部分缓解 | 装得更多,但终归有限 |
| Dilution | 不能,反而更糟 | attention 在长输入上"lost in the middle" |
| Persistence | 完全无能 | 新 session 仍空,与窗口无关 |

### #3 · memory-as-interrupt:机制同一,角色不同
> **memory tool 走的是和普通 tool call 完全一样的 dispatch 路径(tool_use → tool_result → observation),Lesson 06 的整套基建。但 agent 自我认知里它扮演的角色不同——普通 tool call 是"对世界做事"(有 side effect),memory tool 是"延伸自我记忆"(读自身状态、无 side effect)。** 所以论文用 Unix `read()` 类比:同步、阻塞、无副作用、太常用所以给独立 API 表面。这条桥接了"tool use(对外)"和"memory(对内)"——共用同一条 plumbing,承担不同角色。

### #4 · 即使 "RAM" 层也有子层级:core(钉死)vs messages(FIFO)
> **`main_context` 不是一个扁平 buffer:`core` 像内核段(persona / user,永不淘汰),`messages` 像堆栈(FIFO,超 cap 就 evict)。** 所以"两层模式"里顶层自己又分层。这正是 Letta 三层化(core / recall / archival)的伏笔——它只是把 main context 里隐含的"钉死 vs 流动"区分**明确化**了。

trace 实证:eviction 发生时 `[core]` 两条岿然不动,`[messages]` 旧 3 条被踢;后续通过 `archival_memory_search` 从 disk 取回内容,通过 `conversation_search` 扫到 evict 掉的 user turn。

---

## 关键概念地图

**MemGPT(Packer 2023→Letta 2024):** 两层(main + archival)+ memory tool 表面 + interrupt 模式。研究 repo `cpacker/MemGPT` 仍在,产品演进为 Letta。

**5 个 memory tool 表面:**
- `core_memory_append(section, text)` —— 钉住 section 追加
- `core_memory_replace(section, old, new)` —— 钉住 section 编辑
- `archival_memory_insert(text)` —— 写外部
- `archival_memory_search(query, top_k)` —— 检索外部
- `conversation_search(query)` —— 扫历史 turn

**3 种生产模式的坑(都是 Lesson 03 memory rot 的具体形态):**
1. **Memory rot** —— 写比读累积快,检索淹噪声里。修法:Letta sleep-time consolidation、Mem0 显式失效、TTL+relevance 打分。
2. **Memory poisoning(新概念,重要)** —— 外部 memory 是会被重吃进 prompt 的文本。攻击者污染一条 memory note,下个 session 又被喂一次。**Lesson 27 prompt injection 在时间维度上的版本**。
3. **Citation loss** —— "用户让我交付 X"但说不出哪 turn。修法:每个 archival 写入存 `(session_id, turn_id, source_url)`。

**生态(都是 MemGPT 的变体):**
- Letta(Lesson 08)—— 三层 + native reasoning + sleep-time
- Mem0(Lesson 09)—— vector + KV + graph 混合 + 评分层
- OpenAI Assistants —— thread + file 的托管 memory
- Claude Agent SDK —— skill + session store

挑选维度:**运维形态(自托管 / 托管 / 框架内置),而不是核心模式**——核心模式就是 MemGPT。

**这节在 Phase 14 主线的位置:** Lesson 03 提出"memory 三层生命周期",这节给中间层"跨 trial / 跨 session 持久化"做出第一个系统设计。承上(Lesson 03)启下(Lesson 08 Letta、Lesson 09 Mem0)。

---

## 手做记录

### 跑 demo(完整 OS 虚拟内存往返,无真 LLM)

```
写入两类:
  core_memory_append × 2  → main context 的钉住 section(persona/user)
  archival_memory_insert × 3  → external store(带 tag)

填 main context 到上限触发 eviction:
  [core] persona / user                                  ← 钉死,不动
  [messages] 3 current                                   ← 旧 3 条被 evict
  3 evicted

page in 往返:
  archival_memory_search('tool chains drift')
    → 取回 a002(就是之前 insert 进去的那条)             ← RAM→disk→retrieve 完整闭环

历史扫描:
  conversation_search('retrieval bot')
    → 找回已 evict 的 user turn(Letta recall 层的雏形)
```

**实证闭环:**
- 金句 #4:trace 里 `[core]` 不动 / `[messages]` 被 evict —— 顶层自己又分层
- 金句 #1:整套"暂停 → 取数据 → 继续"和 OS 一致;唯一差别是 agent 主动调
- 金句 #3:memory tool 和 Lesson 06 普通 tool call 走同一 dispatch 路径,但语义是"自我延伸"
- 接 Lesson 03 #2:这节是"跨 trial / 跨 session 持久化"那层的工程兑现

### Exercises
概念已覆盖。代码未额外实现(stdlib 两层 demo 已涵盖核心模式)。
