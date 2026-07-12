# Hybrid Memory:Vector + Graph + KV(Mem0)

> Mem0(Chhikara 等人,2025)把 memory 当作**三个并行的 store**——vector 管语义相似、KV 管快速事实查找、graph 管实体-关系推理。检索时一个 scoring 层把三者融合。这是 2026 外部 memory 的生产标准。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 07 (MemGPT)、Phase 14 · 08 (Letta Blocks)
**Time:** ~75 分钟

## 学习目标 (Learning Objectives)

- 解释为什么单一 store(只有 vector、只有 graph、只有 KV)不足以做 agent memory。
- 说出 Mem0 的三个并行 store,各自为什么优化。
- 描述 Mem0 的 fusion scoring——relevance、importance、recency——以及为什么它是**加权和**而不是**层级**。
- 用 stdlib 实现一个 toy 三 store memory:`add()` 往三个都写,`search()` 融合结果。

## 问题所在 (The Problem)

一个 store 对三类 query 中的某一类总是错的:

- **Semantic similarity(语义相似)** —— "上周我们讨论 agent drift 都说了啥?" vector 赢;KV 和 graph 抓不到。
- **Fact lookup(事实查找)** —— "用户的电话号码是多少?" KV 赢;vector 浪费,graph 杀鸡用牛刀。
- **Relationship reasoning(关系推理)** —— "哪些客户共用同一个 billing entity?" graph 赢;vector 和 KV 根本答不了。

**生产 agent 在一个 session 里这三类都会发。** 单一 store 的 memory 总会对其中两类是错的。Mem0 的贡献是:把三个 store 接在**同一个 `add`/`search` 表面**之后,用一个 scoring 函数融合它们。

## 核心概念 (The Concept)

### 三个并行 store (Three stores in parallel)

Mem0(arXiv:2504.19413,2025 年 4 月)在 `add(text, user_id, metadata)` 时:

1. 从文本里**提取候选事实**(一个 LLM 驱动的步骤)。
2. 把每个事实写进 **vector store**(embedding)供语义搜索。
3. 把每个事实写进 **KV store**,以 `(user_id, fact_type, entity)` 为 key,供 O(1) 查找。
4. 把每个事实写进 **graph store(Mem0g)**,作为 typed edge 供关系查询。

在 `search(query, user_id)` 时:

1. vector store 按 embedding cosine 返回 top-k。
2. KV store 按 query 推导出的 `(user_id, type, entity)` 返回直接命中。
3. graph store 返回从 query 实体可达的子图。
4. 一个 scoring 层融合这三者。

### Fusion scoring(融合打分)

```
score = w_relevance * relevance(q, record)
      + w_importance * importance(record)
      + w_recency * recency(record)
```

- **Relevance(相关性)** —— vector cosine、KV 精确匹配、graph path weight。
- **Importance(重要性)** —— 写入时打 tag 或学出来(有些事实更重要:name、ID、policy)。
- **Recency(新近性)** —— 自上次写/读以来的指数衰减。

**权重按产品调。** chat agent 调高 `w_recency`;compliance agent 调高 `w_importance`;retrieval agent 调高 `w_relevance`。

### Mem0g 与时序推理 (temporal reasoning)

Mem0g 加了一个 **conflict detector(冲突检测器)**。当一个新事实和已有 edge 矛盾时,旧 edge 被**标记为 invalid 但不删除**。时序查询("用户三月时住哪个城市?")遍历**在该时间有效**的子图。

这就是 compliance 级的行为,Letta 的失效模式正是它的泛化。

### Benchmark 数字

Mem0 论文报告(2025):

- **LoCoMo**(长篇对话 memory):91.6
- **LongMemEval**(长程 episodic memory):93.4
- **BEAM 1M**(1M-token memory benchmark):64.1

对比 baseline(full-context 128k LLM、flat vector store、flat KV)全都输 10+ 分。**光看 benchmark 不能决定选型——运维形态才能——但这些数字说明融合设计不是个舍入误差。**

### Scope 分类法 (Scope taxonomy)

Mem0 按 scope(范围)切分 memory:

- **User memory** —— 跨 session 持久,以 `user_id` 为 key。
- **Session memory** —— 在一个 thread 内持久。
- **Agent memory** —— per-agent 实例状态。

**每次写入都挑一个 scope。** 检索可以跨 scope 查,带 per-scope 权重。不加思考地混 scope,就是"助手把 Bob 的项目告诉了 Alice"这类事故的根源。

### 这个模式哪里会出问题

- **Embedding drift(embedding 漂移)。** 前一百个 query 看着对的 vector 结果,随语料增长而退化。**周期性 re-embed** 最常用的 top-N 记录。
- **KV schema creep(KV schema 蔓延)。** `(user_id, type, entity)` 看着简单,直到每个团队都加自己的 `type`。**每季度审计** type 集合。
- **Graph explosion(图爆炸)。** 一个嘈杂的 extractor 每条消息加 50 个 edge。**每次 `add` 调用给 graph 写入封顶**;丢掉低置信 edge。

## 动手做 (Build It)

`code/main.py` 用 stdlib 实现三 store 模式:

- `VectorStore` —— 用朴素的 token-overlap 相似度当 embedding 替身。
- `KVStore` —— 以 `(user_id, fact_type, entity)` 为 key 的 dict。
- `GraphStore` —— typed edge `(subject, relation, object, valid)`。
- `Mem0` —— 顶层 facade,带 `add()`、`search()`、fusion scoring、scope 感知检索。
- 一段在多用户、多 session 对话上的演练 trace。

运行它:

```
python3 code/main.py
```

输出显示三条独立的 recall 路径加上融合后的 top-k。**改 `main()` 顶部的 scoring 权重,看排名怎么变。**

## 用起来 (Use It)

- **Mem0(Apache 2.0)** —— 生产就绪。用 Postgres + Qdrant + Neo4j 自托管,或用托管 cloud。
- **Letta** —— 三层 core/recall/archival;自带你的 vector 和 graph 后端。
- **Zep** —— 商业替代,带 temporal KG 和事实提取。
- **自建** —— 当你需要精确控制 extractor(compliance)或 fusion 权重(recency 主导的语音 agent)时。

## 交付出去 (Ship It)

`outputs/skill-hybrid-memory.md` 生成一个三 store memory 脚手架,带 fusion scorer、scope 分类法、时序失效接线。

## 练习 (Exercises)

1. 把 toy vector 相似度换成真 embedding 模型(sentence-transformers、Ollama、OpenAI embeddings)。在合成长对话上测 recall@10。排名在 1000 次写入后会漂移吗?
2. 加一个时序查询:`search(query, as_of=timestamp)`。只返回那个时间点或之前有效的记录。哪个 store 改动最大?
3. 实现一个 conflict detector:进来的事实和某 graph edge 矛盾时,失效旧 edge 并记录两者。在 "user lives in Berlin" → "user lives in Lisbon" 上测。
4. 给 fusion scorer 加一个 `user_feedback` 维度(对检索到的记录点赞)。怎么防止刷分(agent 只返回它已经喜欢的记录)?
5. 读 Mem0 文档(`docs.mem0.ai`)。把 toy 移植到 `mem0` client 调用。在同样 20 个测试 query 上对比检索质量。

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Hybrid memory | "vector 加 graph 加 KV" | 三个 store 并行写入,检索时融合 |
| Fact extraction | "memory 摄入" | 把文本拆成 (entity, relation, fact) 元组的 LLM 步骤 |
| Fusion scoring | "相关性排名" | relevance、importance、recency 的加权和 |
| Scope | "memory 命名空间" | user / session / agent —— 决定谁能看到什么 |
| Mem0g | "memory graph" | 带时序有效性的 typed edge,供关系查询 |
| Temporal invalidation | "软删除" | 把矛盾的 edge 标 invalid;从不删除 |
| Embedding drift | "检索腐烂" | vector 质量随语料增长而退化;周期性 re-embed |

## 延伸阅读 (Further Reading)

- [Chhikara et al., Mem0 (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) —— 原论文
- [Mem0 docs](https://docs.mem0.ai/platform/overview) —— 生产 API、SDK、托管 cloud
- [Packer et al., MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) —— virtual-context 前身
- [Letta, Memory Blocks blog](https://www.letta.com/blog/memory-blocks) —— 三层化的姊妹设计
