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
| 14 · Agent Engineering | 14 · AutoGen / Actor Model | ✅ 完成(换尺子时刻 + actor 三原语 + 一戒律三奢侈品 + DLQ 补刀 + 3/3 体检 + 4 金句) |
| 14 · Agent Engineering | 15 · CrewAI / Role-based Crews | ✅ 完成(4 原语 + Crew vs Flow 双形态 + Hierarchical = supervisor 同构 + LangGraph node 对比 + Flow+Crew 真代码示例 + 3/3 体检 + 6 金句) |
| 14 · Agent Engineering | 16 · OpenAI Agents SDK | ✅ 完成(5 原语 + Handoff=tool 机制深挖 + Guardrails 真能防什么诚实评估 + defense-in-depth 5 层 + 3/3 体检 + 6 金句) |
| 14 · Agent Engineering | 17 · Claude Agent SDK | ✅ 完成(四家光谱收口 + harness-first 哲学 + 5 组件 + Temporal sidebar(durable workflow engine 平行宇宙)+ 3/3 体检 + 4 金句) |
| 14 · Agent Engineering | 18 · Agno and Mastra Runtimes | ✅ 完成(框架篇 coda + 价值分层模型(第 6 把尺子)+ agent loop 内核拆解 + 3/3 体检 + 4 金句) |
| 14 · Agent Engineering | 19 · Benchmarks: SWE-bench, GAIA | ✅ 完成(从造到审的第一步 + 三锚定 benchmark + 污染 + 分布>均值 + 3/3 体检 + 4 金句) |
| 14 · Agent Engineering | 20 · Benchmarks: WebArena, OSWorld | ✅ 完成(评测另一半:界面操作 + GUI grounding 新失败维度 + 轨迹效率 + 3/3 体检 + 4 金句) |
| 14 · Agent Engineering | 21 · Computer Use Agents | ✅ 完成(评测→产品闭环 + untrusted input 铁律 + 行动安全 + 5 层防御具体化 + 3/3 体检 + 4 金句) |
| 14 · Agent Engineering | 27 · Prompt Injection Defense(插队) | ✅ 完成(Greshake 攻击理论 + 6 条防御教义 + PVE 架构 + 两轮红队级追问「结构硬/模型软」「锚点搬到动作-意图一致性」+ 免体检直接过) |
| 14 · Agent Engineering | 22 · Voice Agents: Pipecat, LiveKit | ✅ 完成(延迟预算新尺子 + loop 时序重构 + Pipecat/LiveKit 两路线 + 3/3 体检 + 3 金句) |
| 14 · Agent Engineering | 23 · OTel GenAI Conventions | ✅ 完成(散落观测需求的统一标准 + 真实生产 trace 逐层拆解(阿里 TPP/deepagent,L01-L23 合影)+ 3/3 体检 + 3 金句) |
| 14 · Agent Engineering | 24 · Agent Observability Platforms | ✅ 完成(三平台押不同生命周期 + "trace 不 eval = 昂贵日志" + LangSmith/第一方 vs 开源第三方追问 + 免体检直接过) |
| 14 · Agent Engineering | 25 · Multi-agent Debate | ✅ 完成(L05 第三种模式 + Society of Minds + 稀疏拓扑 O(N²)→O(N) + debate 的赌注=独立性 + 3/3 体检 + 3 金句) |
| 14 · Agent Engineering | 26 · Failure Modes (Agentic) | ✅ 完成(运营篇总账本 + 5 大失败 + 假成功幻觉 + 每步设 gate + 3/3 体检 + 3 金句) |
| 14 · Agent Engineering | 28 · Orchestration Patterns | ✅ 完成(四拓扑收束 + 升级阶梯 + hop counter=TTL 的 agent 版追问 + topology-first 反模式 + 免体检直接过) |
| 14 · Agent Engineering | 29 · Production Runtimes | ✅ 完成(六种运行时形态 + "形状决定失败能否活下来" + debug case(trace≠checkpoint) + checkpoint invoke 在哪处理 + 免体检直接过) |
| 14 · Agent Engineering | 30 · Eval-driven Agent Development | ✅ 完成(前 30 收官 + 三层评测 + eval 当代码养(agent 版 TDD)+ Tying Phase 14 together + 3/3 体检 + 3 金句) |
| 14 · Agent Engineering | 31 · Agent Workbench: Why Models Fail | ✅ 完成(七面/八原语框架 + workbench vs harness 追问 + subagent=worker 解码器 + 免体检直接过) |
| 14 · Agent Engineering | 32 · Minimal Agent Workbench | ✅ 完成(三文件最小 workbench 搭出并跑通 + agent_state schema 设计评审 + 绑 TPP) |
| 14 · Agent Engineering | 33 · Instructions as Executable Constraints | ✅ 完成(规则声明+检测器搭出跑通 + "软约束vs硬强制"分层追问 + 归类/check/severity 评审) |
| 14 · Agent Engineering | 34 · Repo Memory and State | ✅ 完成(schema 校验 + 原子写 StateManager 搭出跑通,拒绝坏写入) |
| 14 · Agent Engineering | 35 · Initialization Scripts | ✅ 完成(6 探针启动体检搭出跑通 + fail-loud halt 演示) |
| 14 · Agent Engineering | 36 · Scope Contracts | ⏭ 下一站 |

## 里程碑

- **Phase 14: 35/42 完成** —— L35 给 lab 加 `init_agent.py`(启动前体检:6 探针,坏了 fail-loud halt exit 1,agent 不启动)。= Trigger 原语 + L33 Startup 类别落地。演示藏 rules 文件→立刻 HALT。

- **Phase 14: 34/42 完成** —— L34 把 L32 静态 state schema 升级成活记忆系统:`agent_state.schema.json`(锁 pattern/enum/必填)+ `state_manager.py`(JSON Schema 子集校验 + 原子 temp/fsync/replace 写)。demo 跑通:坏写入(enum/pattern 违规)被拒不碰磁盘。核心:坏写入=被拒写入 + 半写比没有更糟(L26 静默损坏)。加速模式(揭秘+建+看)。

- **Phase 14: 33/42 完成** —— L33 给 lab 加了"Instructions"surface:`docs/agent-rules.md`(声明)+ `rule_checker.py`(检测器,读 git 真相抓违规)。用户自撞题眼"规则不也是软的吗"→ 沉淀"声明(软)vs 预防+检测(硬)"四层架构,提前预见 L36 write-tool 预防。检测器 demo 跑通:偷改测试→2 block 违规拒绝。

- **Phase 14: 32/42 完成** —— 实战相换挡:从"讲+quiz"变成"设计+评审+真搭"(模式①②③混合)。`learning-notes/workbench-lab/` 是逐节累积的真 artifact:L32 搭好三文件最小 workbench(AGENTS.md 路由/agent_state.json 游标/task_board.json 队列),核心 state schema 由用户设计、reviewer 加三处工程锁(关注点分离/board-state 外键分工/assumptions 带 verified)。靶子=under-validated create_user(2 passed/3 xfail)。L33+ 逐节把 surface 加到 lab 上。

- **🎉 Phase 14 前 30 节正式收官(30/42)** —— 理论(L01-L11)+ 框架(L12-L18)+ 运营(L19-L29)+ 评测方法论(L30)全部完成。L30 拱顶石:Phase 14 不是 30 个孤立知识点,是一套可逐条写成 eval、CI 里 gate 的质量标准。已沉淀 6+ 把尺子 + 完整安全模型 + 生产运行时选型 + eval-driven 方法论。**L31-L42 转入 Agent Workbench 实战相:从"学概念"变成"真 repo 上做项目"。**
