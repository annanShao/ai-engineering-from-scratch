# Lesson 40 · Multi-session Handoff(第七个 surface,循环闭合)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/40-multi-session-handoff/` |
| 类型 | Build(实战)· 加速模式 |
| 前置 | L32(state)、L38(verdict)、L39(review)、L37(feedback)、L31(Trigger 原语) |
| lab | `learning-notes/workbench-lab/generate_handoff.py` |
| 状态 | ✅ 完成(handoff 生成器搭出跑通,cleanup check 当场逮住脏树)|

---

## 这节课的真定位:七个 surface 最后一个,循环闭合

session 结束 agent 说"有进展",下 session 问"到哪了"答案没了→重新发现、重跑、重问,30 分钟找回上个 session 最后 30 秒。修法=session 结束自动生成 handoff 包。= Trigger 原语(session-end 生成,session-start 读)+ session persistence。

---

## 核心金句

### #1 · next_action 是承重字段
> **handoff 有一切但没 next_action = status report,不是 handoff。** 七字段:summary/changed_files/commands_run/failed_attempts/open_risks(带 severity)/**next_action**/verdict_pointer。

### #2 · 生成的不是手写的
> **手写的 handoff 忙的时候会被跳过。generator 读 workbench artifact 吐包。agent 的活是把工作台留成 generator 能总结的样子,不是写总结。** 两形态:handoff.md(人)+ handoff.json(下个 agent),同源,分歧时 JSON 赢。

### #3 · ⭐ 干净 state ≠ 好 handoff(cleanup 是独立 check phase)
> **完美 handoff.md 也救不了下个 session 撞见半应用 diff、忘删 temp、跑不起来的测试。cleanup 是独立 phase,在 handoff 前跑,是 check 不是习惯(习惯忙时被跳)。cleanup 吐 clean_state.json,空列表是 generator 写包前的前提。脏树上的 handoff 不是 handoff,是转发的烂摊子。**

cleanup 五查:working tree(每改动提交或 stash 带 note)/temp artifacts(无 *.tmp/scratch/debug print)/tests(绿,或红但在 open_risks 命名)/feature board(反映现实)/branch(对的分支无 detached HEAD)。

### #4 · feedback 裁剪
> **完整 feedback_record.jsonl 可能几百条。handoff 只带最后 K + 每条非 0 exit。下 session 需要才 load 全量,包保持小。**

---

## 手做记录(真 artifact,已跑通)

`generate_handoff.py`:`cleanup_check()`(git status 查脏树 + 查 *.tmp)+ `load_snapshot()`(汇 state/verdict/review/feedback)+ `generate_handoff()`(7 字段 payload + handoff.md)。feedback 裁剪=最后 K + 所有非 0 exit。

**跑通(真实彩蛋)**:cleanup_check **当场逮住脏树**——generate_handoff.py 自己没提交时,检测到"1 个未提交路径"→拒绝生成 handoff。不是模拟,是当场逮住我们。handoff.md 生成含承重 next_action。**cleanup 作为 check 的价值:当场逮住,不靠习惯。**

### 绑 TPP
你司多 session/多 agent 接力时,下个 session 是读一个 handoff 文件还是重放 chat?你 trace 里 `thread_id` 跨 session 持久,但"上次到哪+还剩什么+失败过什么"有没有一个生成的包?没有的话,每个 session 都在花 30 分钟找回 30 秒。

### 钩子
- L41 真 repo:把整套 workbench 搬到真实 monorepo
- L42 capstone:端到端跑一遍完整 workbench
