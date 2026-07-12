# Lesson 08 · Memory Blocks 与 Sleep-Time Compute(Letta)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/08-memory-blocks-sleep-time-compute/` |
| 类型 | Build · ~75 分钟 |
| 前置 | Lesson 07 (MemGPT) |
| 关键文件 | `docs/zh.md`、`code/main.py`(`Block` + `BlockStore` + `PrimaryAgent`/`SleepTimeAgent`) |
| zh.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/08-memory-blocks-sleep-time-compute/docs/zh.md |
| 状态 | ✅ 完成(阅读 + 3 钩子深挖 + 代码走读 + 4 金句) |

---

## 核心金句

### #1 · 三层化的本质:把"自动时序记录"和"主动沉淀知识"拆成两个层
> **MemGPT 两层的语义重叠在于:被 evict 的对话 tail 和 agent 主动写的任意事实,混在同一个外部 store 里,来源和用途完全不同却不区分。Letta 拆成 recall(对话历史,自动 turn logging,时序原始,按时间/对话检索)和 archival(任意事实,主动写,提炼知识,按相关性检索)。** 一个回答"我说过什么",一个回答"我知道什么"。混在一起会互相污染检索质量(查项目名不该被寒暄淹没)。

三层:Core(始终可见,主 prompt 内)/ Recall(对话历史,可检索)/ Archival(任意事实,vector+KV+graph)。

### #2 · Sleep-time compute = "在线 serving path vs 离线 batch job" 搬到 memory
> **主 agent = 在线接口,卡 SLA 用快模型;sleep-time agent = 夜间 batch,无 SLA,用慢而强的模型(Opus/reasoning)做重整理。** 因为它在关键路径外,所以延迟无要求 → 能跑更强模型。而且一招治三病:同时解决 Lesson 07 三大坑——latency(搬下关键路径)、memory rot(有空窗 dedup/失效)、structure(有算力做结构化重写)。

形状和生物记忆巩固(memory consolidation)同构:白天编码,睡眠时把短期记忆迁移到长期皮层。Letta 不是随便取名 "sleep-time"。

### #3 · typed block 强在"把隐含约定提升成一等公民"(dict → class 的同构)
> **flat dict 是裸值,挂不上治理规则;typed block 有 id/label/value/limit/description,于是能:(a) description 让模型自治知道"何时该写这个 block"(像 tool description,承重);(b) limit 触发 block_summarize;(c) 挂策略——Safety block 标只读+二次评审、Persona block 版本化追 diff。** 这和编程里 dict→dataclass、Lesson 06 的 tool schema 是同一个设计动作:结构显式化之后,才谈得上校验、权限、版本、自治管理。

### #4 · primary 故意留脏,sleep-time 才清理 —— 延迟与正确性的解耦
> **primary 阶段只管把 raw 写入怼进去保证低延迟,故意不在关键路径上清理(trace 里 human block 同时存 Berlin+Lisbon、archival 留着过时的 a002);sleep-time pass 才做矛盾检测+失效(发现 archival Berlin 与 block 最新 Lisbon 冲突 → 标 INVALID)。** 这就是 Lesson 03 说的"显式失效",Mem0 conflict detector / Letta sleep-time 都干这个。诚实难点:consolidation 要全面且不误删很难(toy 里 sleep-time 只失效了 archival,没清 block 内并存脏值)。

---

## 关键概念地图

**Memory block:** core 层里类型化、持久、LLM 可编辑的 section。原始两种:Human block(用户事实)、Persona block(agent 自我概念)。Letta 泛化到任意:Task / Project / Safety。每个有 id/label/value/limit/description。
工具表面:`block_append` / `block_replace` / `block_read` / `block_summarize`。

**三层对照:**
| 层 | 范围 | 住哪 | 谁写 |
|---|---|---|---|
| Core | 始终可见 | 主 prompt | agent tool + sleep-time |
| Recall | 对话历史 | 可检索 | 自动 turn 日志 |
| Archival | 任意事实 | vector+KV+graph | agent tool + sleep-time |

**Sleep-time 的三个红利:** 零延迟成本 / 允许更强模型 / 天然整理窗口(dedup、summarize、失效矛盾)。

**Letta V1 + native reasoning:** 弃用 `send_message`/heartbeat 和 inline `Thought:`,转 native reasoning(独立 channel,跨 turn 传递,生产加密)。control loop 仍 ReAct,thought trace 结构化非 prompt 形状。(呼应 Lesson 01 金句 #3)

**三个坑:** Block bloat(无限 append 撞 limit → 写前接 summarizer)/ Silent drift(sleep 重写 block 主 agent 不知 → 版本化+露 diff)/ Poisoned consolidation(sleep 把攻击内容整理进 core → Lesson 27)。

**生态定位:** Letta(参考实现)/ Claude Agent SDK skill(skill = block 形状的命名版本化知识,按需加载)/ 自建(用 Letta API 契约便于迁移)。

**Phase 14 主线:** Lesson 07 隐含的"core 钉死 vs messages FIFO"在这节被明确成三层 + typed block;Lesson 03 的 memory rot 在这节有了工程答案(sleep-time consolidation)。

---

## 手做记录

### 跑 demo(双 agent 拆分:primary 快写 + sleep-time 整理)

```
primary turns(快、原始,版本在跳):
  human v1 → human v2   (ava 改地址 Berlin→Lisbon)
  task  v1 → task  v2   (受众改 senior+staff)
  计数 (72/180) = limit 实时盯着,接近就 summarize

留下的脏数据(memory rot 现场):
  human v2: city=Berlin city=Lisbon (两个都在)
  archival a002: ava lives in Berlin (过时还躺着)

sleep-time pass(旁路整理):
  invalidate a002 (与 block 最新 Lisbon 冲突 → stale)
  → archival: a001 [VALID] / a002 [INVALID]

trace 收尾明说: primary-turn latency is unchanged by consolidation.
```

**实证闭环:**
- 金句 #2:`latency unchanged by consolidation` = 整理在主链路外
- 金句 #4:primary 留脏(Berlin+Lisbon 并存)→ sleep-time 做矛盾检测+失效
- 金句 #3:version 跳动(human v1→v2)= typed block 的版本能力
- 诚实难点:sleep-time 只失效 archival,没清 block 内并存脏值 → consolidation 全面且不误删很难

### Exercises
概念已覆盖。代码未额外实现(双 agent demo 已涵盖核心拆分)。
