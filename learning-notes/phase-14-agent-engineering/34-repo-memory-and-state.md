# Lesson 34 · Repo Memory and State

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/34-repo-memory-and-state/` |
| 类型 | Build(实战)· 加速揭秘模式 |
| 前置 | L32(state schema)、L13(resume)、L26(静默损坏)、L07/L08 memory |
| lab | `learning-notes/workbench-lab/agent_state.schema.json` + `state_manager.py` |
| 状态 | ✅ 完成(schema 校验 + 原子写 StateManager 搭出跑通,拒绝坏写入)|

---

## 这节课的真定位:把 L32 静态 schema 变成活记忆系统

session persistence 强化版。三个硬机制:① **Schema-first**——坏的写入=被拒绝的写入 ② **原子写**——temp→fsync→rename,半写比没有更糟 ③ **Migration**——`schema_version`,拒绝加载迁移不了的版本。

**"值不值得进 repo"判据**:三个月后 CI 重跑还有用吗?有用→repo,没用→telemetry。

---

## 核心金句

### #1 · 坏的写入 = 被拒绝的写入
> **JSON Schema 是契约。没它,每个 agent 发明新字段、每个 reviewer 学新形状、每个 CI 脚本 special-case 旧版本。有它,bad write is a refused write。** schema 锁:必填键/enum/pattern/禁止值(数组非 null)/version 字段。

### #2 · ⭐ 半写的 state 比没有 state 更糟(原子写的灵魂)
> **没有文件→load 直接失败→fail loud,agent 知道从 board 重建。半写文件→JSON 可能恰好还能 parse 但内容截断→agent 信了一份撒谎的 state(以为只动过 A 其实动过 A/B/C)→重做或双做。又是 L26"静默损坏比崩溃更危险"。原子 rename 保证读者要么看到完整旧文件要么完整新文件,永远没有撕裂态。**

原子写实现:`tempfile.mkstemp`(同目录)→ write → `fsync` → `os.replace`(POSIX+Windows 原子)。Hive 2026 bug:用 `write_text()` 且吞异常→半写→session resume against 损坏 state 无信号。

### #3 · 三个月后 CI 还有用吗(durability filter)
- qwen3-max 模型 id → **不进**(telemetry,vendor 特定)
- email regex 假设 → **进**(影响正确性,reviewer/下 session 都要)
- token 级推理链 → **不进**(telemetry)

进 repo:活动任务 id/动过文件/假设/blocker/下一步。不进:原始 chat/token 级 reasoning/"用户看起来沮丧"/采样/vendor 模型 id。

### #4 · 生产 pattern
- **原子 temp-and-rename 不可选**(见上)
- **每个非幂等 tool 调用带 idempotency key**:crash 后重试会重发邮件/重插 DB。log tool_call_id 进 `pending_calls.jsonl`,重试查 ID 命中就跳过用缓存(=L13 checkpointer 存 pending writes 同理)
- **大 artifact 与 state 分离**:CSV/长 transcript 存单独文件或对象存储,state 只留 path(checkpoint 保持小快)
- **Event sourcing 审计 + snapshot resume**:每次 mutation append `state.events.jsonl`,周期 snapshot;resume 读 snapshot 再 replay 之后事件(=Postgres WAL 同形)
- **Schema migration 或拒绝加载**:`schema_version` 是契约,未知版本拒读,`tools/migrate_state.py` 启动幂等运行

生产版:LangGraph checkpointer(同思想不同存储:SQLite/Postgres)/ Letta memory blocks(L08)/ OpenAI SDK session store。**本节的 schema 就是 checkpointer 死了你要手读 state 时用的东西。**

---

## 手做记录(真 artifact,已跑通)

新增/改 lab:
- `agent_state.schema.json`——锁 active_task_id pattern `^T\d+$` / touched_files.action enum / assumptions.verified boolean / 数组非 null / schema_version 必填
- `agent_state.json`——加 `schema_version: 1`
- `state_manager.py`——JSON Schema 子集校验器 + `atomic_write`(temp/fsync/replace)+ StateManager(load/commit,坏写拒绝)+ demo

**demo 跑通**:load 真 state OK;`action='edited'` 被 enum 拒;`active_task_id='xyz'` 被 pattern 拒;两个坏写入都没碰磁盘。**L32 定的 action 枚举现在是机器强制,不是文档祈祷。**

### 绑 TPP
你司 `langgraph_checkpoint_ns` 就是这个的生产版(LangGraph checkpointer 存全量 state 到 Postgres)。本节手写的 schema+StateManager,是"checkpointer 死了要手读/手修 state"时的底层认知——也呼应 L29 你追问的 fork-resume。

### 钩子
- L36 scope contract → write-tool 预防层(用户已预见)
- L37 feedback / L38 verification gate / L39 reviewer / L40 handoff
