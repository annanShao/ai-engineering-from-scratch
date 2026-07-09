# Lesson 42 · Agent Workbench Capstone(Phase 14 收官)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/42-agent-workbench-capstone/` |
| 类型 | Build(实战)· 打包收官 |
| 前置 | L31-L41 全部 |
| lab | `learning-notes/workbench-lab/agent-workbench-pack/`(可安装 pack) |
| 状态 | ✅ 完成(整套工作台打包成可一键安装的版本化 pack,installer 实测)|

---

## 这节课的真定位:把工作台从"散落的脚本"变成"版本化可安装 pack"

活在 Google Doc + chat + 三个半记得的脚本里的工作台,每季度重建一次。解药:版本化 pack——一个 repo/目录装着 surface、schema、脚本 + 一键 installer,能装进任何目标 repo。

---

## 手做记录(真 artifact,installer 实测)

`agent-workbench-pack/`:
```
├── VERSION (1.0.0, semver)
├── README.md (surface->primitive 映射表)
├── docs/     agent-rules.md + reviewer-rubric.md
├── schemas/  agent_state.schema.json + scope_contract.example.json
├── scripts/  init/rule/scope/feedback/verify/reviewer/handoff/state_manager (8 个)
└── bin/install.sh
```

**installer 实测**:`install.sh <target>` 把 pack 装进目标 repo 的 `.agent-workbench/`,拒绝覆盖已存在(除非 --force),检测 `.github/workflows` 提示接 CI,打印 next steps。跑通:装进临时目录,13 个文件就位。

**什么进/什么不进**:进=surface schema(契约)+ 脚本(runtime)+ docs(规则/rubric);不进=项目特定任务(归目标 repo 的 board)/ vendor SDK 调用(pack 框架无关)/ onboarding 散文。

**Versioning**:VERSION semver,schema/脚本改需迁移则 bump major,doc-only bump patch;目标 repo 的 agent_state.json 记初始化时的 pack 版本。

---

## 🎓 Phase 14 全 42 节收官

**理论(L01-L11)→ 框架(L12-L18)→ 运营(L19-L29)→ 评测方法论(L30)→ 实战工作台(L31-L42)全部完成。**

实战相把前 30 节的原理落成一个能跑、能装的工作台:七个 agent-facing surface,底下八个分布式原语。核心贯穿始终:

> **agent 失败大多不是 model bug 是 workbench bug。你不 fix 模型,你 gate 它——在模型决定和真实世界之间,每一步设一道读外部真相的独立关。术语在变,工程不变;harness 是 function/worker/trigger/runtime/queue/persistence/policy 接对了线。**

**沉淀的可复用资产**:`workbench-lab/`(完整工作台)+ `agent-workbench-pack/`(可装进任何 repo 的 v1.0.0 pack)。

### 绑 TPP
你可以拿这个 pack 的结构去对照你司 deepagents/TPP:哪些 surface 已有(state/checkpoint/middleware)、哪些缺(独立 reviewer?可 review 的 rules 声明?生成的 handoff 包?)。缺的那些,就是你能带回去的最高杠杆。
