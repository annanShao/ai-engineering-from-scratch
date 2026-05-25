# Lesson 03 · Reflexion(Verbal Reinforcement Learning)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/03-reflexion-verbal-rl/` |
| 类型 | Build · ~60 分钟 |
| 前置 | Lesson 01 (Agent Loop)、Lesson 02 (ReWOO) |
| 关键文件 | `docs/zh.md`、`code/main.py`(Actor / Evaluator / Self-Reflector / EpisodicMemory) |
| 状态 | 🔄 进行中(阅读阶段) |

---

## 核心金句

### #1 · 自然语言是"在 run 之间携带失败教训"的介质
> **自然语言是一种足够丰富的介质,能在 run 之间携带"我从失败里学到了什么"。**

这是 Reflexion(以及所有"自我学习 / 记录错误信息"模式)的灵魂洞察。传统 RL 用 gradient 把教训写进 weight(几千次 trial + GPU 集群);Reflexion 用一段自然语言 reflection 把教训写进 episodic memory,下一次 trial prepend 进 prompt 就"学到了"——不更新权重,故称 Verbal RL。

由此派生出几乎所有生产级"自愈"agent:Letta sleep-time compute、Claude Code 的 `CLAUDE.md` / `/memory` learnings、pro-workflow 的 `/learn-rule`、LangGraph reflection node——都在用自然语言跨 run 携带"失败教训"。

---

## 关键概念地图

(待补)

---

## 手做记录

(待补)
