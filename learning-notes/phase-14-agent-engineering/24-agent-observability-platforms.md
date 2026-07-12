# Lesson 24 · Agent Observability Platforms:Langfuse / Phoenix / Opik

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/24-agent-observability-platforms/` |
| 类型 | Concept · ~50 分钟 |
| 前置 | L23 (OTel schema)、L19 (评测)、L05 (CRITIC)、L09 (RAG)、L16/L27 (guardrail) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/24-agent-observability-platforms/docs/en.md |
| 状态 | ✅ 完成(三平台押不同生命周期 + "trace 不 eval = 昂贵日志" + LangSmith 追问 + 免体检直接过) |

---

## 这节课的真定位:从"看见"到"判断"

L23 给 schema(span 长什么样),L24 给吃这个 schema 的平台。核心升级:**L23 让你看见 agent 跑了什么(trace),L24 让你判断跑得好不好(eval)。看见 → 判断,是 observability 第二跳。**

---

## 核心金句

### #1 · 精修:它们不是"评测平台",是"以 trace 为地基的 LLMOps 全栈"
> **分层(从下到上):Trace/Observability 层(substrate,一切地基)→ Dataset/Experiment 层 → Evaluation 层 → Prompt 管理层。你评测不了你追踪不到的东西——所以必然"observability 优先,eval 其次"。三家差异不在地基(都吃 trace),在往地基上盖哪层楼盖得最高。**

| 平台 | License | 押哪层 | 呼应 |
|---|---|---|---|
| Langfuse | MIT(最开放) | prompt 管理闭环 + 全能 | 工程化基建 |
| Phoenix | Elastic 2.0 | RAG 评测 + 行为漂移(无 prompt 版本) | L09 检索 + L19 分布/回归 |
| Opik | Apache 2.0 | 自动优化 + guardrail(PII/话题) | L16/L27 防御 |

### #2 · 全节最狠一刀:tracing 不 evaluation = 昂贵日志
> **只记录 agent 做了什么但不评估做得对不对,你能 debug 单条却发现不了系统性回归——看见不等于判断。这直接呼应 L19:评测从"上线前一次性"变成"生产里对每条 trace 持续跑"。observability 的终点不是看见,是持续判断对错。**

### #3 · 自搭 LLM-judge 不接 ground truth = L05 CRITIC 的错误版
> **不接外部工具的 LLM-judge 退化成 L05 Self-Refine(闭环自评),有天花板,会和被评的 agent 犯同样的事实错误——它俩一起自信地错下去。评测可信度取决于 judge 的独立性,不是聪明程度。这是 L05『独立性 外部工具 > 异模型 > 异 prompt』在评测场的直接复用。**

第三翻车:prompt 版本没绑 trace → 生产回归了没法 bisect 到哪次 prompt 改动。→ Langfuse 强调 prompt 版本 + trace 绑定。

**产业事实(Maxim 2026)**:89% 组织已部署 observability;质量问题仍是生产头号障碍(32%)。→ 看见已标配,评测+修复才是真瓶颈。

---

## LangSmith 追问(用户提问)

**LangSmith = 同一个品类(LLMOps 观测+评测平台),LangChain 官方出的,闭源商业 SaaS。**

**结构洞察:每个 agent 框架生态都会长出一个"第一方观测平台":**

| | 第一方(绑框架) | 第三方开源(框架无关) |
|---|---|---|
| 例子 | LangSmith(LangChain)/ 用户司阿里 TPP 平台(deepagent) | Langfuse / Phoenix / Opik |
| 特点 | 零配置 trace 自动流,但闭源 + 绑生态 | 要配置,但开源 + 自由 |

**LangSmith vs 三开源,四个轴:**

| 轴 | LangSmith | 三开源 |
|---|---|---|
| 开源 | ❌ 闭源 SaaS(企业版可自托管) | ✅(Langfuse MIT/Opik Apache/Phoenix ELv2) |
| 框架绑定 | 深绑 LangChain/LangGraph(设环境变量 trace 自动流) | 框架无关,SDK/OTel 接 |
| trace 格式 | 历史自有 "runs" 格式,现加 OTel 接入 | 更 OTel-native |
| 商业角色 | LangChain Inc. 变现引擎(开源 LangChain 免费,LangSmith 收费养公司) | 开源 + 云托管收费 |

功能高度重叠,区别不在"能干什么",在"开不开源 + 绑不绑 LangChain + trace 格式"。

**决策金句**:全家桶用 LangChain → LangSmith 阻力最小(亲儿子零配置),代价是闭源 + 绑生态;Langfuse 存在的理由就是给"想要 LangSmith 能力但不想闭源/被绑"的人 MIT 出路。**第一方 = 零配置换锁定;第三方开源 = 要配置换自由(L17/L18 尺子)。**

**接回用户司 TPP 平台**:它 = 阿里版 LangSmith(第一方、绑内部 deepagent、自有 `alibaba.association.properties.*` 格式往 OTel 迁移——`telemetry.sdk.name: opentelemetry`)。迁出 TPP 就面临"换平台",正是"第一方 = 锁定"的代价。

---

## 关键概念地图

**选型表**:全能+prompt 管理→Langfuse;深度 RAG 评测+漂移→Phoenix;自动优化+guardrail→Opik;开放 license 不要 ELv2→Langfuse(MIT)/Opik(Apache);Datadog/New Relic 集成→都行(都导出 OTel)。

**用尺子收口**:三平台押不同生命周期段 = L18 价值分层"生命周期版";tracing 不 eval = L19 评测搬到生产持续;LLM-judge 接 ground truth = L05 CRITIC vs Self-Refine;prompt 版本绑 trace = 出事二分定位;Opik guardrail = L16/L27 防御进平台。

**"L23+L24 = observability 完整故事:L23 给标准的眼睛(span 树),L24 给判断的大脑(eval+回归检测)。agent 生产化不是让它更聪明,是让它每一步既可见又可判断:看见做了什么(L23)+ 判断对不对(L24)+ 变坏时定位原因(prompt-trace 绑定),三件凑齐才算'可运营'。"**

---

## 手做记录

概念课,未跑代码。核心通过 LangSmith 追问 + "trace 是 substrate,eval 是上层" 的分层洞察完全消化。

### 钩子
- **L30 Eval-driven agent development**:评测从平台功能上升为开发方法论
- LangSmith/TPP 第一方 vs 开源第三方的选型,是 L17/L18 尺子的又一次应用
