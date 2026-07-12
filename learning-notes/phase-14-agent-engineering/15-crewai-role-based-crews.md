# Lesson 15 · CrewAI:Role-based Crews 与 Flows

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/15-crewai-role-based-crews/` |
| 类型 | Build · ~75 分钟 |
| 前置 | L12 (Workflow vs Agent)、L13 (LangGraph)、L14 (AutoGen) |
| 关键文件 | `docs/en.md`、`code/main.py`(stdlib Crew + Flow) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/15-crewai-role-based-crews/docs/en.md |
| 状态 | ✅ 完成(4 原语 + Crew vs Flow 双形态 + 两个深度追问(Hierarchical 是 router 同构 + LangGraph node 对比) + 真代码示例 + 3/3 体检 + 6 金句) |

---

## 这节课的真定位:Phase 14 第一个把 L12 二分法做进 SDK 表面的框架

CrewAI 是这一相**第一个不用我帮你建尺子、自己就把 L12 的尺子内嵌进 API 表面**的框架。Crew vs Flow 这两条产品线,**就是 L12 spectrum 的两端被产品化**。2026 官方推荐姿势:**从 Flow 起手,把 Crew 包成 `Crew.kickoff()` 嵌进 Flow step——『compose, do not pick』**。

---

## 核心金句

### #1 · CrewAI 没发明新机制,它把前面两节的东西重新打包
> **CrewAI = LangGraph 的『可编程外层图』+ AutoGen 的『多 agent 协作』各拿一半,中间用『role/goal/backstory』这种人类组织语言重新包装。产品价值在『把这种组合做成开箱即用 + 给非工程师可读』,不在底层范式创新。**

学完 L13/L14/L15 你应该看清楚——这就是"看穿营销层"的肌肉。Agent 是『角色化的 actor』,Task 是『带契约的 message』,Crew 是『定义了流程的小团队』。**好处是非工程师能读懂(PM 能看 backstory),代价是工程师容易被『拟人化』带走,以为给 agent 写好 backstory 就完了。**

### #2 · 4 原语 = 整本 CrewAI 心智模型(文档原话压缩)
> **"Agents do not see each other directly. Tasks reference agents. The Crew sequences tasks. The Process decides who picks the next task. That is the whole mental model."**

| 原语 | 是什么 | 关键 |
|---|---|---|
| **Agent** | `role + goal + backstory + tools + (optional) llm` | backstory 是 load-bearing;塑造 tone/判断/何时停 |
| **Task** | `description + expected_output + agent + (optional) context + output_pydantic` | `expected_output` 是契约;`context` 列上游;`output_pydantic` 强制 schema |
| **Crew** | 容器:`agents[] + tasks[] + process + memory + manager_llm` | |
| **Process** | Sequential / Hierarchical / Consensus(planned) | 决定下一个 task 谁选 |

### #3 · Crew vs Flow = L12 二分法的产品化

| | Crew | Flow |
|---|---|---|
| 控制流 | **LLM**(Process 决定) | **代码**(`@start` + `@listen(topic)`) |
| 复现性 | 难 | **deterministic** |
| 适合 | 草稿/研究/头脑风暴(路径本身是答案的一部分) | 生产/合规/on-call 要能 debug |

**生产姿势**:Flow 是脊柱(可审计、可复现),需要创造力的某一步内嵌 `Crew.kickoff()`。**Flow 给审计员事件序列,Crew 给那一步必要的创造力——精准对应 L12 "agent 要挣它的复杂度"。**

### #4 · Hierarchical Process = supervisor pattern 的最贵版本(追问 1)
> **CrewAI Hierarchical = L13 LangGraph Supervisor = L14 AutoGen SelectorGroupChat = 同一个 router + 主 agent 分发的 pattern,只是名字不同。**

但 CrewAI 这一版有一个**让 token tax 更狠**的细节:

| | LangGraph Supervisor | CrewAI Hierarchical |
|---|---|---|
| Manager 调用时带什么 | 当前 state | **全部 task 列表 + 所有历史 task 输出** |
| 为什么 | state 是 dict,精简 | **Task 是 first-class,manager 要看到全图才能选** |

**"CrewAI Hierarchical 是 supervisor pattern 的『最贵版本』——同一个老问题,被『Task 作为一等公民』这个设计放大了 token tax。这也是为什么 CrewAI 文档自己都说『routing 真依赖输出才用 Hierarchical,否则永远 Sequential』。"**

### #5 · 真代码示例:Flow + Crew 嵌套长什么样(追问 2)

**场景:客户合同审查**——4 步 Flow 主线 deterministic,中间 `brainstorm_risks` 这一步 `Crew.kickoff()` 让 3 个角色(legal/finance/ops)自由发散。

```python
class ContractReviewFlow(Flow[ContractReviewState]):
    @start()
    def load_contract(self): ...          # 普通 Python,deterministic
    
    @listen(load_contract)
    def extract_terms(self, text): ...    # 普通 Python,deterministic
    
    @listen(extract_terms)
    def brainstorm_risks(self, terms):    # ⭐ 这一步是创造力孤岛
        risk_crew = build_risk_crew(terms)
        result = risk_crew.kickoff()
        return result.pydantic.risks       # 拿 typed 结果回 Flow
    
    @listen(brainstorm_risks)
    def validate_and_store(self, risks): ...  # 普通 Python,deterministic
```

**类比帮记**:`Flow 调 Crew` ≈ `Bash 调 subprocess` ≈ `Claude Code 调 Task tool`。**Flow 不关心 Crew 内部 3 个 agent 怎么吵的、用了几个 tool、token 烧了多少——它只关心 Crew 返回的那个 typed 契约。这就是 "agent 进笼子" 的具体长相。**

### #6 · LangGraph node 写 agent vs CrewAI Crew(追问 2 深一层)
> **真正的决策规则:那个『创造力孤岛』里是**一个 LLM 用 tools**,还是**一群 LLM 用人格 riff**? 一个 LLM → LangGraph node 够了;一群 LLM → 才掏 CrewAI Crew。否则你在为没用上的东西付钱。**

| 维度 | LangGraph node 里写 agent | CrewAI Crew |
|---|---|---|
| 笼子典型规模 | 一个 LLM + tools | 3+ 个 LLM 用不同人格 riff |
| 多 agent 协作语义 | 自己写 | 开箱即有(Process) |
| Memory 4 件套 | 自己接 | `memory=True` 一行 |
| role + goal + backstory | 自己塞进 prompt | first-class,PM 可读 |
| **Durability 粒度** | **node 级 checkpoint**(细,L13 杀手锏) | **Flow step 级**(Crew 内部**不可中断**——崩了整个 Crew 重跑) |
| State 谁拥有 | 整图共享 typed state | 每个 agent 私有 + 通过 Task 传话(更像 actor) |
| 心智成本 | 工程师视角 | 入门低 + 有"拟人化"陷阱 |

**进阶 taste**:CrewAI Crew 是**不可中断的黑盒**——Flow checkpoint 只到 step 级,Crew 内部 3 个 agent 跑到一半崩,resume 时整个 Crew 从头跑。**"嵌一个 Crew 进 Flow 实际上是『用 audit/replay 粒度换 role-based 多 agent 协作的开箱即用』——这是真实交易,不是免费午餐。"**

---

## 关键概念地图

**4 个翻车点(必须记到肌肉):**

| 翻车 | 修法 |
|---|---|
| Prompt-bloat from backstories(2000 字 × 5 个 agent) | 每个 backstory < 200 字;house style 写一份不要复制 5 份 |
| Manager-LLM token tax(Hierarchical 翻 3 倍 token) | routing 真依赖输出才用 Hierarchical,否则 Sequential |
| Brittle handoffs(Task N 给 free text 下游猜) | `output_pydantic` 锁 schema |
| **⭐ Crew-as-prod**(自由 Crew 直接生产,无 audit/replay) | **用 Flow 包住——这是 L13 "conditional edge 滥用" 在 CrewAI 上的同形重演** |

**Memory 4 件套(CrewAI 相对 LangGraph 真挣到钱的地方):**

| 类型 | 是什么 | 对应学过的 |
|---|---|---|
| Short-term | 单 run 内 buffer,跑完清 | L01 conversation history |
| Long-term | 跨 run 持久,vector DB + 相似度 | L09 Mem0 archival |
| Entity | 按实体 key 存事实 | L08 entity memory |
| Contextual | assembly-time 检索 | L09 fusion 运行时形态 |

`memory=True` 一行启用。**纯 LangGraph 你要自己接 4 个组件。**

**何时不该上 CrewAI(taste):**
- Deterministic DAG 严格顺序 → LangGraph(graph shape 是对的抽象,role 框架是摩擦)
- Sub-second 延迟 → Hierarchical 加 round trip,Sequential 也要序列化 backstory + 上游输出
- 单 agent 循环 → 跳过框架,L01 agent loop + tool registry 更短

**用尺子收口:**

| CrewAI 部件 | 性质 |
|---|---|
| agent `role/goal/backstory` | 内化(LLM prompt 主体) |
| Task `expected_output` | 外部 contract(L01 observation formatter 同源) |
| `output_pydantic` | 外部 schema 锁(L06 tool schema 同形) |
| Crew memory 4 种 | 外部记忆基建(L08/L09 工业版) |
| **Flow `@start` / `@listen`** | **工程师拥有的事件图**(L13 graph 同源,事件驱动) |
| `Crew.kickoff()` from Flow step | **agent 进笼子——L12 thesis 产品化** |

---

## 体检 · 3/3 ✅

| # | 题 | 答 | 点评 |
|---|---|---|---|
| Q1 | 2026 官方生产姿势 | C(Flow 起手 + 嵌 Crew 进 step) | "compose, do not pick" |
| Q2 | Hierarchical 5 步 token 翻 3 倍根因 | B(每个 specialist 前一次 manager LLM,带全任务列表 + 历史输出) | 直达根因 |
| Q3 | 合同审查(audit + diff + 头脑风暴需要创造力) | C(Flow 主线 + brainstorm step 嵌 Crew) | 精准对应 2026 推荐姿势 |

---

## 手做记录

`code/main.py` 实现 stdlib 双形态(Crew + Flow + 3 agent crew)。**未额外跑**——概念已通过"Hierarchical = 老 supervisor 同构"和"Flow+Crew 真代码"两个深度追问完全消化。

### 留给后续的钩子
- **进 L16 OpenAI Agents SDK 时**:OpenAI 完全不分 Crew/Flow,而是把整个 agent 当 managed 黑盒卖——又一种"包装哲学"。三家对比之后 taste 会再升一档。
- **LangGraph 也有 `create_supervisor` 多 agent topology**——它和 CrewAI Crew 的多 agent 区别又是什么?(再下一层的尺子)
- **Crew 内部 checkpoint 缺失**——为什么生产系统嵌入 Crew 一般会做"sub-flow 拆分"或回退 LangGraph,是值得专门复盘的运维 trade-off。
