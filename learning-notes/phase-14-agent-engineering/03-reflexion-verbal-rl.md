# Lesson 03 · Reflexion(Verbal Reinforcement Learning)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/03-reflexion-verbal-rl/` |
| 类型 | Build · ~60 分钟 |
| 前置 | Lesson 01 (Agent Loop)、Lesson 02 (ReWOO) |
| 关键文件 | `docs/zh.md`、`code/main.py`(Actor / Evaluator / Self-Reflector / EpisodicMemory) |
| 状态 | ✅ 完成(阅读 + 3/3 钩子 + 概念深挖 + 5 金句;Ex2/Ex3 概念已挖,代码未实现) |

---

## 核心金句

### #1 · 自然语言是"在 run 之间携带失败教训"的介质
> **自然语言是一种足够丰富的介质,能在 run 之间携带"我从失败里学到了什么"。**

这是 Reflexion(以及所有"自我学习 / 记录错误信息"模式)的灵魂洞察。传统 RL 用 gradient 把教训写进 weight(几千次 trial + GPU 集群);Reflexion 用一段自然语言 reflection 把教训写进 episodic memory,下一次 trial prepend 进 prompt 就"学到了"——不更新权重,故称 Verbal RL。

由此派生出几乎所有生产级"自愈"agent:Letta sleep-time compute、Claude Code 的 `CLAUDE.md` / `/memory` learnings、pro-workflow 的 `/learn-rule`、LangGraph reflection node——都在用自然语言跨 run 携带"失败教训"。

### #2 · memory 的三层生命周期
> **区别全在"活过哪条边界":run 内的 message buffer(每次重试清空)/ 跨 trial 的 episodic memory(同一任务累积)/ 跨 session 的 persistent memory(`CLAUDE.md`、memory block,显式外化才不丢)。** Reflexion 处在中间那层;把 episodic memory 外化到 `CLAUDE.md` 就升到了第三层。

### #3 · Evaluator 和 Self-Reflector 是两职,别混
> **Evaluator 打分(回答"成没成 / 多差"),Self-Reflector 写教训(回答"下次怎么改")。** 之所以 self-eval 和 Self-Reflector 看着像,是因为 self-eval 那种情况下两件事都由 LLM 看自己的 trace 来做——但仍是两个动作:先 evaluate 再 reflect。换成 scalar evaluator(外部 pass/fail)就泾渭分明了。

### #4 · TTL 帮忙还是添乱,取决于任务是否平稳(stationary)
> **任务不变、反思捕获的是真不变量 → 删掉它会重新犯错、来回震荡 → TTL 添乱;任务漂移、或反思是一次性偶发的迷信(superstition)→ 留着误导 → TTL 帮忙。** 所以 TTL 本质是一个"赌任务会变"的赌注。固定 TTL 太粗暴(太短健忘、太长 rot);更好是 relevance/recency 打分 + 去重 + consolidation(多条相似反思合并成一条 rule)。

### #5 · heuristic 只抓症状,不抓病因
> **heuristic evaluator(如"同一 action 重复=卡住"、">50 步=低效")只抓症状,诊断病因还得靠 Self-Reflector。** 它的价值是便宜、确定性、不需要 ground truth,当安全护栏;它的失败特征会**塑造 reflection 的方向**(scalar 说"差多远"→ 微调;heuristic 说"你卡住了"→ 换策略)。风险:误报会逼出不必要的探索。

---

## 关键概念地图

**三个组件 + 一个数据结构:**
```
Actor          : 生成一条 trajectory(ReAct 式 loop)
Evaluator      : 给 trajectory 打分(scalar / heuristic / self-eval)
Self-Reflector : 对失败写一段自然语言 reflection
Episodic memory: 先前 reflection 的有界 list，prepend 到下一次 trial 的 prompt
```

**术语层级(所有 memory 类模式的地基):**
```
step  = loop 一次迭代(thought→action→observation)
trial = 对任务的一次完整 attempt(含很多 step)，被当整体 evaluate ≈ 一次操作路径
session = 用户与 agent 的一次交互坐席，可跨多个任务/turn
```
注意:trial ≠ 一次消息往返(turn),trial 内部可能有一堆 step。Reflexion 论文里真正的容器是"同一任务的多次 trial"。

**三种 evaluator(2026 分层叠加，非三选一):**
| 类型 | 是什么 | 强弱 |
|---|---|---|
| Scalar | 外部二元/数值信号(测试 pass/fail) | 信号最强 |
| Heuristic | 预定义失败特征(stuck-loop、步数过多) | 便宜、确定性,当护栏 |
| Self-eval | LLM 评自己的 trace | 弱、可能谎报成功,配 tool-grounded verification(Lesson 05 CRITIC) |

**Verbal RL 的本质:** 传统 RL 把教训写进 weight(几千 trial + GPU);Reflexion 把教训写进 context(一段 reflection prepend 进 prompt)。学习活在 context 里、不在参数里 → 故 per-task、不持久化就丢、受 context 窗口约束 → 这是 **memory rot** 的根源。

**何时有用/无用:** 有清晰 failure signal + 任务可复现 + action budget 够 → 有用;第一次就成功 / 失败是外部原因(网络挂)/ 反思变迷信 → 无用。

---

## 手做记录

### 跑 demo(scripted,伪代码体感)
任务:在 [1..9] 选 3 个整数和为 20。
```
BASELINE(无 memory): trial 1-4 全是 [1,2,3] sum=6   → 永远卡死，从不适应
REFLEXION(有 memory): [1,2,3]→反思"差14挑大的"→[5,6,7] sum=18→反思"差2"→[6,7,7] sum=20 成功
```
实证金句 #1:Actor 和任务完全一样,唯一区别是 prompt 里有没有 reflection。那段 `"sum X is N short; pick larger"` 字符串就是充当"梯度"的自然语言。

### Exercise 2 / 3
概念已深挖(见金句 #4 TTL、#5 heuristic)。代码暂未实现(scripted demo 已足够说明流程)。
