# Lesson 39 · Reviewer Agent

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/39-reviewer-agent/` |
| 类型 | Build(实战)· 加速模式 |
| 前置 | L38(gate)、L05(独立 verifier)、L31(Worker 原语)、L25(judge bias) |
| lab | `learning-notes/workbench-lab/reviewer_checklist.md` + `reviewer_agent.py` |
| 状态 | ✅ 完成(reviewer 搭出跑通,抓住 gate 抓不到的"right tests wrong problem")|

---

## 这节课的真定位:gate 后的定性复审

gate 说 passed 你合并,两天后发现修的是 bug 错误的一半。acceptance 必要不充分。reviewer 问 gate 问不了的:解决对的问题了吗/scope 偷偷扩了吗/假设写下来了吗/下 session 能接手吗。

---

## 核心金句

### #1 · reviewer 是独立 role 不是独立 model
> **可以同一个模型,纪律在角色分离——不同 system prompt、不同输入、对 diff 无写权限。姿态变=信号变。** = Worker 原语(read-only on diff,write-only on report)。

### #2 · reviewer 不能改 diff
> **它读 diff/state/feedback/verdict,写报告。说"fix this"→下个 builder 轮去改,reviewer 回去 review。混角色就毁了那个 gap。**

### #3 · gate vs reviewer(Hybrid Norm,两个都要)
> **gate 查确定性事实(跑了吗/过了吗/守 scope 吗),reviewer 做定性判断(对的活吗/记录了吗/交接可用吗)。别让 reviewer 重做 gate 已证明的。** 5 维 rubric 各 0-2:problem_fit/scope_discipline/assumptions/verification_quality/handoff_readiness。总分 10;<7 soft fail,<5 hard fail。

### #4 · 生产 pattern(Cloudflare 13 万次 review 数据)
- **Specialist pool 不是一个大 reviewer**:codebase 有 security/perf/docs 面就拆专家(小 prompt),coordinator 去重判 severity。**模型分层自然落出:便宜专家 + 贵 coordinator。**
- **Bias mitigation 是设计要求**:LLM judge 四 bias——position(GPT-4 约 40% 顺序不一致)/verbosity(约 15% 偏长)/self-preference(偏同族)/authority(高看知名作者)。缓解:两种顺序都评只算一致的/1-4 尺度奖简洁/轮换 judge 家族/去掉作者名。
- **Calibration set 不是 vibes**:10-20 个已知正确裁决的历史任务,每次 prompt 改就重跑;与历史一致率 <80% 就得先改 rubric 再上线。

---

## 手做记录(真 artifact,已跑通)

`reviewer_checklist.md`(5 维 rubric + bias 缓解)+ `reviewer_agent.py`(ReviewerInputs 只读 bundle + 5 维打分 + 写 `outputs/review/<task_id>.json`,不改 diff)。

**跑通(抓住 L39 灵魂)**:
- 场景 A(干净)→ 10/10 pass
- 场景 B → **gate 是 passed 的**(测试绿+scope 守住),但 reviewer 6/10 soft_fail——`verification_quality=0`(验收证明弱化版目标不是真目标)+`assumptions=0`(没记录)。**这正是 gate 抓不到只有 reviewer 能抓的"right tests, wrong problem"。gate 查"跑了吗",reviewer 查"对吗"。**

### 绑 TPP
你司 code review 若是 agent 自己 review 自己(builder=reviewer),就没有那个 gap——姿态没变信号没变。真 reviewer 要角色分离 + 对 diff 只读。你司有没有一个独立姿态的 review 步骤,还是 builder 自评?

### 钩子
- L40 handoff:reviewer 报告 + gate 裁决 + 失败 attempt 进交接包,下 session 干净接手
- L41 真 repo / L42 capstone
