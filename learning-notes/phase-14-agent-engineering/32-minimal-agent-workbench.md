# Lesson 32 · The Minimal Agent Workbench(动手第一课)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/32-minimal-agent-workbench/` |
| 类型 | Build(实战)· 设计+评审模式 |
| 前置 | L31(七面/八原语)、L07(context 预算)、L14(反 state 漂移)、L17(session) |
| lab | `learning-notes/workbench-lab/`(动手搭的真 artifact) |
| 状态 | ✅ 完成(三文件最小 workbench 搭出来并跑通 + agent_state schema 设计评审) |

---

## 这节课的真定位:把 L31 宣言落成三个文件

最小 workbench = 三文件,各是一个原语:`AGENTS.md`=路由器(policy)/ `agent_state.json`=session persistence / `task_board.json`=queue。三文件是**地板不是天花板**,后面所有 surface 都假设它们先存在。

---

## 核心金句

### #1 · AGENTS.md 是路由器不是手册
> **Long manuals get ignored. Short routers get followed. 根文件只放"去哪找"(state/board/深层规则/验证命令),细节 just-in-time 加载。同 L07 MemGPT page-in、L17 skill 渐进披露——context 是预算不是容器。**

### #2 · agent_state.json 是 system of record
> **它是文件因为 chat 不可靠:session 会死、对话会被裁剪,文件不会。agent 每轮读它,下个 session 读它而不是重放 chat。** = L29 追问的 checkpoint 最朴素形态(agent 能读能写的持久大脑)。

### #3 · task_board.json 是 queue,故意保持小
> **board 超过一屏 = planning 问题不是 board 问题。工具容量暴露的往往是上游问题,别用扩容掩盖规划失败。** owner 字段(builder/reviewer/human)提前埋 L39 reviewer + HITL 钩子。

### #4 · 生产 AGENTS.md pattern(可直接用)
- **嵌套 + nearest-wins**:OpenAI 主 repo 88 个 AGENTS.md,从工作文件往根走拼接;子目录扩展根文件。
- **Augment 实测**:最好的 AGENTS.md ≈ 把模型从 Haiku 升到 Opus,最差的比没有还糟——印证 L31"钱在工作台里",一个写对的路由文件=免费换一档模型。
- **反模式**:冲突指令(AMBIG-SWE 48.8%→28%,给优先级编号)/ 不可验证 style 规则(agent 自己编合规,每条配 lint 命令=L30 每 guardrail 配 eval)/ style 领先(命令在前)/ 给人写(简洁是特性)。
- **跨工具 symlink**:单一真相源 `ln -s AGENTS.md CLAUDE.md/.cursorrules`,避免多份漂移。

**"The names change. The shape does not."** Claude Code(CLAUDE.md/.claude/state/hooks)、Codex/Cursor(workspace rules/session memory/sidebar)、自建——名字变形状不变。

---

## 设计评审:agent_state.json schema(模式①,用户设计我评审)

3 个判断题,用户的选择 + reviewer 修订:

### 决策 1 · touched_files 存多细 → 用户选 b(path+改了什么,不含 why)✅
- 用户理由:只存路径模型还得看 diff、不知增删。(次要好处,对)
- **reviewer 升级**:选 b 不选 c 的真正理由是**关注点分离**——"why"是任务级理由,塞进每个文件条目会跨文件复制(L14 反 state 漂移)。touched_files=改了什么(机械),assumptions/task=为什么(存一次)。坑:`change` 别纯自由文本,用 `action` 枚举(added/modified/deleted)+ 一句 summary。

### 决策 2 · next_action 形态 → 用户选结构化指针 ✅(方向对,分工没说透)
- **reviewer 钉死**:数据库类比——task_board=任务队列(任务级,粗,多行)/ agent_state=当前游标(步骤级,细,程序计数器+工作寄存器)。`next_action={"task_id":"T1","step":"...","kind":"edit"}`,task_id 是指向 board 的**外键**(不重复存任务详情)。
- **反漂移铁律**:task 级状态只 board 记(单一真相),state 只存"我在哪个 task 的哪一步"。绝不两处都记 task 状态(否则不知信谁)。

### 决策 3 · 存 assumptions → 用户选存(为事后 retro)✅(只说了 1 个读者)
- **reviewer 升级**:assumptions 服务**三个读者**——下个 session(不重推导)/ **Reviewer L39(事前审查,>事后 retro)** / 你(retro,最晚最贵)。
- **关键**:assumption = 未验证的声明,每条带 `verified:false`。它是**等着被写成 eval case 的东西(L30)**,也是**L26 级联失败的根**(没人审的坏假设,如"我假设 400 是成功")。

### 最终 schema(用户骨架 + reviewer 三处工程锁)
```json
{
  "active_task_id": "T1",
  "touched_files": [{"path":"...","action":"modified","summary":"..."}],
  "assumptions": [{"claim":"...","verified":false,"task_id":"T1"}],
  "blockers": [],
  "next_action": {"task_id":"T1","step":"...","kind":"edit"},
  "last_updated": "ISO8601"
}
```
三处锁:① 关注点分离(改什么 vs 为什么)② board-state 外键分工(任务级 vs 步骤级)③ assumptions 带 verified 标记。

---

## 绑 TPP(用户司 deepagents 生产)

| 我们的 schema | TPP trace 里 | 说明 |
|---|---|---|
| active_task_id | `run_id` | 当前运行标识 |
| session 边界 | `thread_id` | 会话持久化 key(L17) |
| **步骤游标** | **`langgraph_step: 8`** | **印证决策 2:你司 state 就是 step 级游标!** |
| 持久化命名空间 | `langgraph_checkpoint_ns` | LangGraph session persistence 落点 |

**互补**:LangGraph checkpoint=框架自动存全量 state(给机器 resume);agent_state.json=人/agent 可读的显式摘要(给"我在干嘛"快照)。

---

## 手做记录(真 artifact,已 push)

`learning-notes/workbench-lab/`:
- `toy-repo/`(靶子:under-validated create_user + 2 passed/3 xfail 测试)
- `AGENTS.md`(路由:指 state/board + verify 命令 + scope)
- `agent_state.json`(设计评审后的 schema)
- `task_board.json`(T1:加输入校验)

verify 命令跑通:`2 passed, 3 xfailed`。工作台自洽——agent 读三文件即知:干什么(T1)/在哪(游标)/能碰啥(scope)/怎么验(pytest)。

### 钩子(后续 surface 加在这个 lab 上)
- L33 Instructions as executable constraints → `docs/agent-rules.md` + 规则=可执行检查
- L34 repo memory & state → state 演化
- L36 scope contract → AGENTS.md 的 scope 升级成硬约束
- L37 feedback / L38 verification gate / L39 reviewer / L40 handoff → 逐节加到 workbench-lab
