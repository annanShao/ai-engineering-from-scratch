# Lesson 38 · Verification Gates

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/38-verification-gates/` |
| 类型 | Build(实战)· 加速模式 |
| 前置 | L33(rules)、L36(scope)、L37(feedback)、L27(defense-in-depth)、L31(Verification 原语) |
| lab | `learning-notes/workbench-lab/verify_agent.py` |
| 状态 | ✅ 完成(verification gate 搭出跑通,汇流 3 checker,fails-closed)|

---

## 这节课的真定位:收口节点——一道 agent 贿赂不了的确定性门

agent 太容易宣布成功("Looks good"/"Tests passed"无记录/"Acceptance met"松散解释)。修法=一道 gate 读 agent 已产出的 artifact 自己裁决。确定性、进版本控制、挂 CI、agent 贿赂不了。= Verification function 原语,L33+L36+L37 所有 check 的汇流。

---

## 核心金句

### #1 · 确定性不概率,gate 侧无 LLM judge
> **同一 artifact 集永远同裁决。LLM judge 属于 reviewer(L39,做定性"is it good"),不属 gate(做 status"did it pass")。混在一起 collapse 信号。** = Anthropic 2026 Hybrid Norm:verifiable rewards(unit test/schema/exit code)答"解决了吗",LLM rubric 答"可读/安全/on-style 吗";gate 跑第一类,reviewer 跑第二类。

### #2 · 一报告一路径
> **`verification_report.json` 一份写 `outputs/verification/<task_id>.json`,CI 读同一路径。多 gate 多路径=fork 真相源。**

### #3 · 拒绝无例外
> **block 违规 agent 不能 override,只有人能,带 `override_reason`+`overridden_by`。override 是签名变更不是 agent 决定。**

### #4 · Defense-in-depth 不是单 gate
> **pre-commit hook(不可绕,不依赖 agent 听话)→ CI status → pre-tool authz → pre-merge gate。每层确定性,一层漏下层接。** 呼应 L27 纵深防御。verification gate 坐在 CI/pre-merge 层。

---

## 手做记录(真 artifact,已跑通)

`verify_agent.py`:`verify(task_id, changed_files)` 汇流三 checker——scope_check(L36)+ rule_checker(L33)+ 重跑 acceptance 命令(L37,null exit/非 0 都 block)→ 任一 block 则 `passed=False` → 写 `outputs/verification/<task_id>.json`。

**跑通**:
- 场景 A(干净 in-scope)→ passed=True → 放行 reviewer
- 场景 B(creep+改测试)→ 4 条 block(scope×2+rule×2)→ passed=False → 拒绝 done 交给人

**agent 贿赂不了它**:不读自述,读 git 真相 + 重跑验收。**"看着挺好"永远到不了 main。** gate 输出目录 `outputs/` 入 gitignore。

### 绑 TPP
你司 CI 里若有"agent 改动合并前的检查",那就是这个 gate;若合并靠人肉 review "感觉行",就缺这道确定性门。关键区分:gate=确定性 status(能不能过),reviewer=定性质量(好不好)——你司这两个混了没?

### 钩子
- L39 reviewer:gate passed 之后的定性复审(LLM judge,读 gate 放行的 diff)
- L40 handoff:gate 裁决 + override 记录进交接包
