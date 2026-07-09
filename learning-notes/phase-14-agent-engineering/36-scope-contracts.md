# Lesson 36 · Scope Contracts

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/36-scope-contracts/` |
| 类型 | Build(实战)· 加速模式 |
| 前置 | L33(用户预见此预防层)、L26(scope creep/不信自述)、L31(Authorization policy 原语) |
| lab | `learning-notes/workbench-lab/scope_contract.json` + `scope_checker.py` |
| 状态 | ✅ 完成(scope 契约 + 预防/检测双层 checker 搭出跑通)|

---

## 这节课的真定位:L33 预见的预防层

Scope creep 是 agent 最没被监控的失败模式——agent 每步真诚叙述理由。修法不是更严 prompt,是**磁盘契约(承诺了什么)+ 对照 diff 的 check(结果 vs 承诺)**。= Authorization policy 原语 + L33 用户预见的 write-tool 预防层。

---

## 核心金句

### #1 · negative space 是契约的一半
> **没有 forbidden_files 的契约是残缺的。** 契约字段:task_id/goal(一句话 reviewer 可验)/allowed_files(globs)/forbidden_files(globs,连误碰都不行)/acceptance_criteria/rollback_plan/approvals_required。

### #2 · globs 不是裸路径
> **真 repo 会移文件。契约钉 glob(`app/**/*.py`),refactor 跨 session 不会让契约失效。**

### #3 · rollback 是 scope 的一部分
> **列出怎么回滚,逼契约作者想清楚哪里会出错。回滚不了的契约不该被批准。**

### #4 · ⭐ 两个高度:task 契约 vs feature list
> **scope_contract 管一个任务(碰哪些文件);但 agent 能完美待在 login fix 契约内,下一轮又决定项目还需要 settings page+dark mode+重写 router——契约从没被问"项目里哪些活在 scope",只问"任务里哪些文件在 scope"。**

第二高度需要 `feature_list.json`:项目 backlog 的机器可读有序文件,agent session start 读它,只挑一个 `status:todo` 的 feature 写进 active 契约,**禁止同 session 开第二个 feature**。"one feature at a time" 从 prompt 里能被合理化的话,变成磁盘上的值 + gate 强制的 check。
- 不变量"至多一个 in_progress"本身是 startup check(L33):显示两个就拒启动要人解决。
- feature list 是**文件不是 chat 消息**(chat 滚出 context,文件跨 session/agent 持久)。
- **least privilege 组合**:task 契约的 allowed_files 必须落在 active feature 触及范围**之内**,绝不超出。

---

## 手做记录(真 artifact,已跑通)

- `scope_contract.json`——T1 契约:allowed=user_service.py,forbidden=test 文件+release*.sh,含 rollback_plan+approvals_required
- `scope_checker.py`——**预防** `is_write_allowed(path)`(write tool 改前调,forbidden 胜过 allowed=least privilege)+ **检测** `scope_check(git 真相)`(gate 事后调,L26 不信自述)

**跑通(你 L33 预见的两层同时在跑)**:
- 预防:user_service.py→ALLOW;test_user_service.py→BLOCK(forbidden);email_helper.py→BLOCK(off-scope creep)
- 检测:模拟 creep diff 抓 2 violation → gate 会 REFUSE

**scope creep 从"agent 真诚叙述的一步步"变成"改文件前就被拒的硬约束"——你不 fix 它,你 gate 它。**

### 绑 TPP
你司 agent 若有"允许写哪些路径"的配置,就是这个 authorization policy;若没有,scope creep 在你司是不是也靠 prompt 祈祷?值得回去看有没有一层磁盘契约 + diff check。

### 钩子
- L37 feedback(命令输出进循环)· L38 verification gate(消费 scope_check + rule_checker + init 的裁决)· L39 reviewer · L40 handoff(写回 feature status)
