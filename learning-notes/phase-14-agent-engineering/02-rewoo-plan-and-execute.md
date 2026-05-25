# Lesson 02 · ReWOO and Plan-and-Execute(解耦式规划)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/02-rewoo-plan-and-execute/` |
| 类型 | Build · ~60 分钟 |
| 前置 | Lesson 01 (Agent Loop) |
| 关键文件 | `docs/zh.md`、`code/main.py`(toy ReWOO:Planner / Worker / Solver) |
| 状态 | ✅ 完成(阅读 + 3/3 钩子 + Exercise 2 + 2 金句) |

---

## 核心金句

### #1 · ReAct vs ReWOO 的本质 = "编排智能放在 runtime 还是 plan-time"
> **ReAct 里 LLM 自己就是 router,每步现场决定下一个 tool;ReWOO 把 routing 拆出来——planner 一次性产出 DAG,一段确定性 executor(拓扑排序 + `#En` 替换 + tool 派发)无脑执行,全程只有 planner / solver 两次 LLM call。省 token 的根子和"中途不能改路"的代价,都来自这次"智能前移"。**

推导链:既然 worker 阶段没有 LLM 来"决定下一步走哪",那"谁先跑、谁依赖谁、`#En` 怎么替换"就**必须由一段确定性编排脚本(DAG executor)承担**。所以 ReWOO 比 ReAct"前期工程更重"——你得真写一个 executor;而 ReAct 的编排器就是模型本身。

| | 谁来 routing | 何时决定 |
|---|---|---|
| ReAct | LLM 本身就是 router,每步现场决定 | runtime,每步一次 |
| ReWOO | planner 一次性决定整个 DAG,executor 无脑执行 | plan-time 一次 + 确定性执行 |

### #2 · Plan-and-Execute = ReWOO + "observation 流回 planning"
> **让 ReWOO 变成 Plan-and-Execute 的最小改动,本质就一行:`plan = replanner.replan(question, plan, evidence)`。原 planner 只吃 question、看不到 observation;replanner 吃 evidence。把 observation 带回规划环节,就是这两个模式的分水岭。**

其余都是脚手架:把一锤子的 `run_workers` 包进"执行 → 查 `error:` → replan → 重执行"的有界 loop(`max_replans` 防无限,对应 Lesson 01 的"只重试一次")。replan 时 replanner 在**完整 plan + 全部 evidence** 的上下文里看错,所以能精准定位翻车的 node 重规划。

---

## 关键概念地图

**三个角色:**
```
Planner:  user_question -> [plan_dag]              (1 次 LLM；看不到 observation)
Workers:  [plan_dag]     -> [evidence]            (纯 tool dispatch，0 次 LLM，可并行)
Solver:   question, plan, evidence -> answer       (1 次 LLM)
```

**省 token 的根子:** `2 次有界 LLM call` vs ReAct `N 次且每次重发全历史`(≈ 步数的二次方)。论文 HotpotQA ~5x fewer tokens、+4 准确率。

**`#E1` / `#E2` evidence reference:** plan-node 占位符,派发时**字符串替换进 tool 的 args**(不是喂模型的 prompt)。toy 里 `search('population of #E1')` → `#E1` 换成 `Paris`。

**鲁棒性:** 失败定位 **per-node**(只看前置节点,信噪比高)而非 ReAct 的 per-step(全周期 context 里捞)。solver 连同原始 plan 看到 error string,可优雅降级。

**代价:** planner 看不到 observation → 静态 plan **中途不能适应**。evidence 推翻假设也改不了 → 这正是 Plan-and-Execute 加 `replanner` 的原因。

**模式选择表:**
| Pattern | 何时用 |
|---|---|
| ReAct | 短任务、环境未知、要 reactive 异常处理 |
| ReWOO | 结构化、tool 已知、token 敏感、evidence 可并行 |
| Plan-and-Execute | 像 ReWOO,但执行后会 replanning(把 observation 带回 planning) |
| Plan-and-Act | 长程 >30 步、web/mobile/computer-use,用合成 plan 数据训 planner |
| Tree of Thoughts | 值得为 search 付代价(Lesson 04) |

**Planner distillation:** planner 不看 observation → 可用 175B teacher 的 plan output fine-tune 7B planner。小 planner + 大 executor 是 2026 常见配置。

---

## 手做记录

### 跑 demo
`python3 code/main.py` → plan(E1→E2→E3 DAG)→ evidence(`#E1` 替换成 Paris)→ solver 组合。toy token 比 1.76x(论文 ~5x,toy 步数少)。

### Exercise 2 —— 加 replanner,把 ReWOO 变 Plan-and-Execute
新增 `ScriptedReplanner`(吃 evidence,返回修订 plan)+ `run_plan_execute`(把 `run_workers` 包进有界 replan loop)。demo 造一个 E2 用错 kwarg(`q` 而非 `query`)的 broken_plan:

```
EXECUTE (initial plan)
  E2 -> error: TypeError: ... unexpected keyword argument 'q'   # 翻车
  E3 -> unknown                                                  # 级联：拿到 error 字符串就废
  >> replanner fires (it sees the evidence; planner never did)
EXECUTE (replan #1)
  E2 -> 11.2 million metro                                       # 修正后干净
  E3 -> 11 million
  >> all clean
FINAL: ... rounded population is 11 million.
```

**最小改动的本质 = `replanner.replan(question, plan, evidence)` 把 evidence 流回 planning。**
**踩到的点:** per-node 失败会向下游**级联**(E2 错 → E3 `unknown`);好在 replanner 在完整 plan+evidence 上下文里能定位到是 E2。`max_replans=1` 防无限 replan。

**提交:** branch `claude/wonderful-hawking-1247L`。
