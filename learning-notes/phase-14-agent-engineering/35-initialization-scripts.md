# Lesson 35 · Initialization Scripts

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/35-initialization-scripts/` |
| 类型 | Build(实战)· 加速模式 |
| 前置 | L33(Startup 类别/rules)、L34(state 新鲜度)、L26(fail loud)、L31(Trigger 原语) |
| lab | `learning-notes/workbench-lab/init_agent.py` |
| 状态 | ✅ 完成(6 探针启动体检搭出跑通 + fail-loud halt 演示)|

---

## 这节课的真定位:启动前体检(Trigger 原语 + L33 Startup 类别落地)

问题:开 session,agent 猜 Python 版本/测试命令/入口,一万 token 烧在本该一个脚本搞定的 setup。修法:一个 init 脚本在 agent 干任何事前跑,写 `init_report.json` 让 agent 启动读。

---

## 核心金句

### #1 · Fail loud, fail fast, fail in one place
> **探针失败=halt 交给人,不许"agent 自己会搞定"。init 的全部意义是:工作台坏了就拒绝启动。** 不是让 agent 带残缺工作台硬跑,是门口就拦住。

探针清单:runtime 版本(错版本=静默 wrong-version bug)/ 依赖可用/ 测试命令可解析(agent 必须知道怎么验证)/ repo 路径(一次解析钉死)/ 环境变量(缺 KEY 是失败面不是运行时谜)/ state+board 新鲜度(崩溃 session 的陈旧 state 是 footgun)/ last-known-good commit(handoff diff 锚点)。

### #2 · 幂等 + 热路径无网络无 LLM
> **连跑两次第二次是 no-op(除新时间戳)——才能挂 CI/hook。探针是确定性管道:调 LLM 分类失败的"探针"不是探针是 workflow;超 3 秒的探针=workbench 异味,移出 init 或缓存。**

### #3 · Init vs rules
> **Rules(L33)描述"要为真才能行动";init 建立"这些 rules 能被检查"。Rules without init = 'be careful'(空话);init without rules = 抛光过的失败。**

### #4 · 生产 pattern
- **LKG commit 锚定**:探当前 commit vs 上次成功合并的 `LKG` 文件,diff 超预算(默认 50 文件)拒启动要人批。Cloudflare AI Code Review 用它 scope reviewer,每 session 锚同一 LKG 不跨 session 累积漂移。
- **Lock files with TTL**:首次探针通过写 `prereqs.lock`,N 小时(默认 24h)内 + manifest hash 匹配就 short-circuit 跳过昂贵探针(=Docker layer cache:幂等探针+内容 hash=skip)。
- **热路径无惊喜**:见 #2。

生产接入:Claude Code `pre-task` hook / GitHub Actions `setup-agent` job / Docker entrypoint。**init 脚本可移植因为不调特定框架。**

---

## 手做记录(真 artifact,已跑通)

`init_agent.py`:6 探针(python>=3.8 / dep:pytest / test-target / rules-file / state-valid(复用 StateManager)/ board-valid)→ 写 `init_report.json` → 有 block 失败 exit 1。

**跑通**:全绿 exit 0 "READY";藏起 rules 文件重跑 → `FAIL[block] rules-file` → HALT + exit 1 "agent will NOT start"。**fail-loud 落地:工作台坏了门口拦住。**

### 绑 TPP
你司若用 Claude Code 类 hook,`pre-task` 就该挂这种 init;TPP 的 `_ruyi_runtime_context.before_agent` middleware 部分就是这类启动探针(检查运行时上下文就绪)。

### 钩子
- L36 scope contract(write-tool 预防层)· L37 feedback · L38 verification gate · L39 reviewer · L40 handoff(LKG diff 锚点在这里用)
