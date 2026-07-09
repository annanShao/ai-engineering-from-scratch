# Lesson 37 · Runtime Feedback Loops

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/37-runtime-feedback-loops/` |
| 类型 | Build(实战)· 加速模式 |
| 前置 | L26(假成功)、L01(observation)、L31(Queue 原语)、L23(feedback vs telemetry) |
| lab | `learning-notes/workbench-lab/run_with_feedback.py` |
| 状态 | ✅ 完成(feedback runner 搭出跑通,succeeded() 只认 exit 0)|

---

## 这节课的真定位:治"假成功"病(L26 执行层)

agent 说"running tests"→"all pass"→现实根本没跑/没读结果/悄悄截断失败行。修法=feedback runner:每命令走 runner,每记录带 command+stdout/stderr+exit_code+duration+agent_note。agent 下轮读,gate 结束读。= Queue 原语 + L26"成功由外部状态验证"的执行层。

---

## 核心金句

### #1 · 确定性截断
> **50MB 日志毁掉循环。head+tail 截断带 `...truncated N lines...`,最终错误/摘要在 tail(agent 要看的在那)。无采样——同输出永远同记录。**

### #2 · feedback ≠ telemetry
> **telemetry(L23)给人跨时间看;feedback 给这次 run 的下一轮。共享字段但不同文件不同保留期。**

### #3 · ⭐ 没 exit 不许前进(No exit, no progress)
> **runner 捕获 exit 前出错→记录 `exit_code: null`+error→agent 循环必须拒绝在 null exit 上宣布成功。** 落地成一行 `succeeded()` 只认 `exit_code == 0`——agent 再也没法自称成功,exit code 是唯一裁判。

### #4 · 生产 pattern
- **Redact at write not read**:任何碰 stdout/stderr 的记录可能泄密。写盘前 redact(`Bearer `/`password=`/`api_key=`/AWS `AKIA...`/Slack `xox...`)。读时 redact 是 foot-gun——磁盘文件才是攻击者够得到的。季度 audit redaction 模式。
- **Rotation 不是单文件**:cap 1MB/文件,溢出转 `.1/.2`,丢 `.5`。agent 只读当前文件(运行时成本有界);CI artifact 存全套。
- **Parent-command id 追 retry 链**:每记录 `command_id`,retry 带 `parent_command_id`。否则 retry 看起来像独立成功,审计藏了失败史。

生产版:Claude Code Bash tool(已捕获 stdout/stderr/exit/duration)——本节 runner 是框架无关等价物。

---

## 手做记录(真 artifact,已跑通)

`run_with_feedback.py`:`run_with_feedback(command, agent_note)` 包 subprocess,捕获 stdout/stderr/exit/duration,写盘前 redact,确定性 tail 截断,append `feedback_record.jsonl`;`succeeded(rec)` 只认 exit 0。

**跑通**:cmd1 pytest→exit 0 succeeded=True;cmd2 exit 3→succeeded=False(agent 不能自称成功);cmd3 崩溃前无 exit→exit=None succeeded=False(null exit 不许前进)。

**运行产物**(feedback_record.jsonl/init_report.json/rule_report.json)已加 gitignore——它们是每次跑生成的,不该进 diff。

### 绑 TPP
你司 trace 里每个 tool span 的 stdout/exit 就是这个 feedback record 的生产形态。区别:feedback 给 agent 下一轮读(热路径),trace 给你事后看(L23 telemetry)。你司 agent 判"成功"是看 exit code 还是信模型自述?值得回去查。

### 钩子
- L38 verification gate:消费 feedback records + scope_check + rule_checker,统一裁决 fails-closed
- L40 handoff:失败 attempt 列表跟 parent_command_id 链
