# Learning Notes · AI Engineering from Scratch

个人学习笔记,跟随 `phases/` 课程推进。

## 结构约定

```
learning-notes/
├── README.md                              # 本文件
└── phase-<NN>-<phase-name>/
    └── <NN>-<lesson-name>.md              # 一节课一篇
```

每篇 lesson 笔记四段式:
1. **课程坐标** —— 路径、时长、前置、关键文件
2. **核心金句** —— 这节课沉淀的 1~N 条 takeaway
3. **关键概念地图** —— 概念之间的关系、对比表
4. **手做记录** —— exercise 改了什么、跑出什么、踩了什么坑

## 进度

| Phase | Lesson | 状态 |
|---|---|---|
| 14 · Agent Engineering | 01 · The Agent Loop | ✅ 完成(阅读 + 4/4 评估 + Exercise 3 + 5 金句) |
| 14 · Agent Engineering | 02 · ReWOO / Plan-and-Execute | ✅ 完成(阅读 + Exercise 2 + 2 金句) |
| 14 · Agent Engineering | 03 · Reflexion / Verbal RL | ✅ 完成(概念深挖 + 5 金句) |
| 14 · Agent Engineering | 04 · Tree of Thoughts / LATS | ✅ 完成(MCTS 深挖 + 3 金句) |
| 14 · Agent Engineering | 05 · Self-Refine and CRITIC | ✅ 完成(CRITIC vs Self-Refine + 3 金句) |
| 14 · Agent Engineering | 06 · Tool Use and Function Calling | ✅ 完成(Toolformer/BFCL 深挖 + 代码 + 4 金句) |
| 14 · Agent Engineering | 07 · Memory / Virtual Context / MemGPT | ✅ 完成(OS 类比 + 4 金句) |
| 14 · Agent Engineering | 08 · Memory Blocks / Sleep-time Compute | ✅ 完成(三层+sleep-time + 4 金句) |
| 14 · Agent Engineering | 09 · Hybrid Memory / Mem0 | ✅ 完成(两层融合 + 4 金句) |
| 14 · Agent Engineering | 10 · Skill Libraries / Voyager | ✅ 完成(lifelong learning 飞轮 + 5 金句) |
| 14 · Agent Engineering | 11 · Planning: HTN and Evolutionary | ✅ 完成(HTN/ChatHTN + AlphaEvolve/MAP-Elites + loop-engineering 跨框架综合 + 3/3 体检 + 6 金句) |
| 14 · Agent Engineering | 12 · Anthropic Workflow Patterns | ✅ 完成(5 模式光谱 + 决策透镜 + "反向到达"元收获 + 3/3 体检 + 5 金句) |
| 14 · Agent Engineering | 13 · LangGraph / Stateful Graphs | ✅ 完成(graph 四零件 + durable execution + supervisor vs tool-call 派 + checkpoint 翻车 4 例 + 3/3 体检 + 5 金句) |
| 14 · Agent Engineering | 14 · AutoGen / Actor Model | ⏭ 下一站 |

## 里程碑

- **Phase 14: 13/42 完成** —— L13 把 L12 的 taste 落到第一个工业级框架;接下来 L14 换尺子(actor 模型 vs graph 模型,两种并发世界观)
