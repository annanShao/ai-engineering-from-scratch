# Lesson 09 · Hybrid Memory(Vector + Graph + KV / Mem0)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/09-hybrid-memory-mem0/` |
| 类型 | Build · ~75 分钟 |
| 前置 | Lesson 07 (MemGPT)、Lesson 08 (Letta Blocks) |
| 关键文件 | `docs/zh.md`、`code/main.py`(VectorStore + KVStore + GraphStore + Mem0 facade + fusion scoring) |
| zh.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/09-hybrid-memory-mem0/docs/zh.md |
| 状态 | ✅ 完成(阅读 + 概念深挖 + 4 金句;代码未额外跑) |

---

## 核心金句

### #1 · 单一 store 对三类 query 永远错俩 —— hybrid 的根本动机
> **memory query 至少三类:语义相似(vector 赢)、精确事实(KV 赢)、关系推理(graph 赢)。生产 agent 在一个 session 里这三类都会发。** 单一 store 的 memory 总会对其中两类是错的——这就是 Mem0 把三种 store 都拉进来、用 fusion 当统一入口的根本动机。

**三种 store 是"同一份事实的三种索引",不是"三个版本":** 提炼出的事实只有一份逻辑内容,但被三种不同数据结构索引了一遍(像图书馆按书名/作者/主题各存一张卡片柜)。物理上:每个 store 各存一份拷贝(payload 模式,查询路径自包含、快、但要三处同步),或三个 store 只存 id、canonical 主表存全文(范式化、一致性好、多一跳)——经典的"反范式换速度 vs 范式化保一致性"权衡。

### #2 · 融合是"两层",不是一层
> **第一层(store 层融合):三个 store 各返回一个候选 list,合并去重成 union 候选集;对 union 里每条记录,把它在三个 store 的命中合成一个 relevance 分(常见手法:取最大 / 加权和 / RRF reciprocal rank fusion)。一条记录命中多个 store,relevance 天然更高 —— 多个独立信号都说它好,比单一信号更可信(回想 Lesson 05 独立性)。**
>
> **第二层(维度层融合):对每条候选的 relevance + importance + recency,加权合成最终分。** 公式 `final = w_rel·relevance + w_imp·importance + w_rec·recency`。
>
> **输出 = 一个统一的 top-k 列表**,不是各 store 各选一条;每条记录带最终分、命中了哪些 store(可解释)、原始 text。

### #3 · 加权 vs 分层 + 归一化怎么做
> **分层 = 字典序、第一维一票否决(`ORDER BY A, B, C`)—— 一条"高度相关但去年的"会永远碾压"稍弱但今天的",维度间无补偿。加权和 = 维度间是"可交换的汇率",允许"虽然 relevance 弱一点但 recency 拉满 importance 也高,加起来能反超" —— memory 要的就是这种补偿。**

权重是**产品方的配置旋钮**(chat→w_rec 高、compliance→w_imp 高、retrieval→w_rel 高);实务由糙到精:手调起步 → 离线 grid search → learning-to-rank(核心场景才上,要数据要防刷分)。

**归一化(解决量纲不可比)**:
- **min-max** `(x-min)/(max-min)`:简单直观,但**被极值绑架**——一个离群点把正常数据全压成 0
- **Z-score + sigmoid**:`(x-μ)/σ` → `1/(1+e^(-z))` ——衡量"偏离均值几个 σ"而非"在 min/max 间位置",对长尾鲁棒;sigmoid 再把无界的 z 平滑挤进 (0,1) 不让离群把别人压爆
- recency 长尾常见 → Z-score+sigmoid;cosine 本来就在 [0,1] → 常不用归一化

### #4 · 失效思想的三段演进(同一思想的成熟度阶梯)
> **Reflexion TTL(Lesson 03)→ Letta sleep-time(Lesson 08)→ Mem0g temporal invalidation(本节)是同一个"软删除"思想从粗到精的三个版本。**

| Lesson | 形态 | 能做什么 | 局限 |
|---|---|---|---|
| 03 TTL | 到期硬删 | 简单 | 丢历史,无法回答"过去某刻是什么状态" |
| 08 Letta | 标 invalid 不删 | 软删通用形态 | 不一定维护完整时间轴 |
| 09 Mem0g | 软删 + valid_from/valid_to | compliance 级,能时点回溯 | 实现复杂 |

整条线一句话:**从"删除"→"标记"→"版本化带时间轴",越来越不丢信息、越来越能回答"过去某刻是什么状态"。** Mem0g 在合规场景(金融/医疗/法务)是必需:审计要追溯"这条事实曾经为真、何时失效"。

---

## 关键概念地图

**三个 store 各擅长:**
| Store | 数据结构 | 擅长 query | 命中信号 |
|---|---|---|---|
| Vector | 向量索引(embedding) | 语义相似("聊过 X 没") | cosine(0~1) |
| KV | dict + 复合键 (user_id, type, entity) | 精确事实("电话号是啥") | hit 布尔 |
| Graph(Mem0g) | typed edge(subject, relation, object, valid) | 关系推理("谁和 X 共用 Y") | 路径权重 |

**Mem0 的 `add(text, user_id, metadata)` 流程:**
1. LLM 提取候选事实(fact extraction)
2. 写 vector(embedding)
3. 写 KV(以 (user_id, fact_type, entity) 为 key)
4. 写 graph(typed edge 入图)

**Scope 分类法(隐私/多租户红线):**
- User memory(跨 session,以 user_id 为 key)
- Session memory(单 thread 内)
- Agent memory(per-agent 实例)
- **混 scope 不分会出"助手把 Bob 的项目告诉了 Alice"事故**

**Benchmark 数字(2025):** LoCoMo 91.6 / LongMemEval 93.4 / BEAM 1M 64.1,普遍打过 128k full-context、flat vector、flat KV 10+ 分。

**三个坑:**
- Embedding drift(语料增长后 vector 退化)→ 周期性 re-embed top-N
- KV schema creep(每个团队加自己的 type)→ 季度审计
- Graph explosion(嘈杂 extractor 每条消息加 50 edge)→ 写入封顶 + 丢低置信 edge

**生态:** Mem0(Apache 2.0,自托管/managed)/ Letta(三层 + 自带后端)/ Zep(商业)/ 自建(compliance 或 recency 主导场景)。

**Phase 14 主线位置:** memory 三部曲收官。Lesson 07 解决了 memory 的**控制流**(怎么 page),Lesson 08 解决了**结构**(三层 + typed block + sleep-time),**Lesson 09 解决了 archival 内部的数据结构**(三种 store + fusion)。三节合起来就是 2026 production memory 的完整画像。

---

## 手做记录

代码未额外跑(toy `code/main.py` 实现 `VectorStore` token-overlap + `KVStore` dict + `GraphStore` typed edge + Mem0 facade,fusion scoring 可调权重看排名翻转)。核心机制在概念深挖里已通过"fact_001 vector+KV 命中、fact_007 vector+graph 命中"的手算 trace 完整跑过,见金句 #2 的并集+排序逻辑。

### Exercises
概念已覆盖。代码未额外实现(stdlib 三 store + fusion demo 已涵盖核心模式)。

---

## 本节最值钱的几次追问(我自己留的)

1. **"truth 怎么存"** —— 暴露了"索引"比喻的边界:三个 store 各存一份 payload(冗余换速度)vs 只存 id 回 canonical 主表(范式换一致性)。这是反范式 vs 范式化的经典工程权衡在 memory 上的具体形态。
2. **"为什么不能分层"** —— 锁死了"字典序一票否决 vs 加权和允许补偿"的本质区别。memory 要的是补偿,不是绝对优先级。
3. **"Z-score+sigmoid 怎么算"** —— 长尾/离群场景的归一化标准做法,延伸到任何"多信号融合"的工程问题都有用,不限于 memory。
4. **"加权的意义 / 输出是什么"** —— 揭开了"两层融合"的真相(我之前把它讲混了):store 层把三个 store 的命中合成 relevance,维度层把 relevance+importance+recency 合成 final;输出是 union → top-k 不是各取一条。
