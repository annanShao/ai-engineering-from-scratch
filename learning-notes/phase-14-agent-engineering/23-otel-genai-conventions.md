# Lesson 23 · OpenTelemetry GenAI Semantic Conventions

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/23-otel-genai-conventions/` |
| 类型 | Concept + Build · ~50 分钟 |
| 前置 | L21 (per-step trace)、L22 (metrics observer)、L27 (content capture)、L17 (W3C trace context) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/23-otel-genai-conventions/docs/en.md |
| 状态 | ✅ 完成(散落观测需求的统一标准 + 真实生产 trace 逐层拆解 + 3/3 体检 + 3 金句) |

---

## 这节课的真定位:把散落的观测需求标准化

每家框架发明自己的 span 命名,导致 ops 要为每个框架单独搭 dashboard。OTel GenAI SIG 定义一套整个生态对齐的标准。**L01-L22 学"agent 怎么跑",L23 是"用一套通用语言把它跑的时候发生的一切记下来"——换框架换模型 dashboard 不用重写。**

---

## 核心金句

### #1 · span 树 = per-step trace + metrics + 轨迹的统一结构
> **L21 的 per-step trace、L22 的 metrics observer、L19/L20 的轨迹,其实是同一个东西,OTel 只是给了它标准结构。observability 不是事后加的,是你决定『agent 的每一步要不要留痕』的架构选择。**

三类 span:
| 类 | 覆盖 | 谁发出 |
|---|---|---|
| Model/client span | 裸 LLM 调用 | provider SDK |
| Agent span | `create_agent` + `invoke_agent` | 框架 |
| Tool span | 每 tool 一个,parent-child 挂 agent span 下 | 框架 |

span kind:CLIENT(远程 agent 服务)/ INTERNAL(in-process 框架)。**parent-child 结构让一次运行成为可展开的树。**

### #2 · content capture 外存写进标准(印证 L27 追问)
> **OTel 默认规则:instrumentation 不应默认捕获输入/输出。捕获 opt-in,推荐外存(S3/日志库)+ span 记引用(指针 ID 非 prose)。文档原话:"This is the Lesson 27 content-poisoning defense wired into observability."**

**你 L27 追问"外存了 LLM 怎么理解",我说外存是日志层不是推理层——OTel 把这标准化了:span 默认不抓 prose。你的直觉就是 OTel SIG 写进标准的东西。默认不捕获 = privacy-by-default。**

### #3 · 绑标准别绑 vendor 私有命名
> **OTel GenAI 还 experimental(2026-03,要 stable 得 `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`),但现在就该按它埋点——标准的价值不在成熟,在共识。早对齐的人换后端/框架零成本。这和框架篇『绑原理别绑 API』同源:绑标准(活很久),别绑 vendor 私有 span 命名(会过期)。**

关键 attribute:`gen_ai.provider.name`(多 provider dashboard 命根子)/ `request.model` vs **`response.model`**(抓 routing 真相——请求 A 实际路由到 B,生产"突然变笨"常是这个)/ `operation.name` / `data_source.id`(RAG 来源)。

Datadog v1.37+ 原生映射;Grafana/Honeycomb/Jaeger 支持 raw attribute。

---

## 关键概念地图

**四个翻车**:Capturing full prompts in spans(PII 进 trace,外存)/ No `gen_ai.provider.name`(多 provider dashboard 崩)/ Spans without parent links(孤儿 span,无法还原路径,always propagate context)/ Not setting stability opt-in(后端升级 attribute 被改名)。

**用尺子收口**:span 树 = L21+L22+L19/L20 统一结构;parent-child + context 传播 = L17 W3C trace context 标准化;content 外存 = L27 防御进标准;request vs response.model = L18 router 真相;默认不捕获 = privacy-by-default。

**"Observability 是 agent 从『能跑』到『能运营』的分水岭。看不见内部的 agent 在生产里是定时炸弹——它会在你没监控的尾部 case 失败,直到用户投诉才知道。"**

---

## 真实生产 trace 逐层拆解(用户贴的阿里 TPP / deepagent trace)

一张 66 节点的真实 trace,几乎把 L01-L23 全部塞进一棵树。逐层对应:

| trace 里的 | 对应的课 |
|---|---|
| 基建外壳(RR/MESH/GLAUCUS/ab.detail) | 公司 RPC mesh + 灰度实验(agent 之前的世界) |
| `POST /threads/{thread_id}/runs/stream` | L16/L17 agent SDK server 形状(thread=session,run=一次运行,stream=流式) |
| `AGENT LangGraph.WORKFLOW`(69s) | **L23 agent span**(INTERNAL kind),底座 **L13 LangGraph** |
| `router.TASK` → LLM → `transfer_to_product-publish-agent.TOOL` | **⭐ L16 handoff=tool + L13/L14 supervisor**——生产实体 |
| `product-publish-agent.TASK`(62s) | handoff 落地的子 agent |
| `SkillsSyncMiddleware.before_agent` 等 middleware | **L17 hooks**(before_agent/before_model/after_model)+ `SkillsSync`=**L10 skill library** |
| `model→tools→model→tools` ×5 | **L01 ReAct 循环**教科书形状 |
| `run_cli.TOOL` → `sandbox.exec` | **L06 tool 沙箱 + L27 安全边界**(sandbox.id/slot_id) |
| `telemetry.sdk.name: opentelemetry` | **⭐ 字面就是 L23 OTel** |
| `langgraph_node: tools` / `langgraph_step: 8` / 嵌套 `checkpoint_ns` | **L13 checkpointer node/step 粒度**——精确印证 A5 的困惑(LangGraph 是 node/step 级,非 Temporal 的 activity 级) |
| `thread_id` / `run_id` | L17 session |

**诊断三连(observability 的真正用途——把黑盒变可诊断的故事):**
1. **Token 爬坡** Σ3996→10407→12173→12645→15966→17322(输入 10263→17008 单调涨)= **L07 上下文累积真实现场**,ReAct 每轮 append tool 结果;是"该上压缩了吗"的早期信号。
2. **第 4 轮 model 20.781s**(其他 4-9s,输出 1043 token 远超其他)= **L19 尾部延迟**,同模型这一次慢 4-5 倍,大概率长输出。
3. **LLM 占 ~78% 时间**(54s/69s)= 瓶颈在推理不在工具,优化方向是减轮数/换快模型,不是优化工具。

**"这张 trace 是 L01-L23 的合影。没学过的人看到『一堆调用』;你看到『supervisor handoff 给子 agent,子 agent 在沙箱跑 5 轮 ReAct,上下文 4k 涨到 17k,第 4 轮生成长文卡 20 秒』——这就是 observability 的意义:把黑盒变成可诊断的故事。"**

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(每家发明 span 命名,标准让生态对齐) | 没停在"更快/防注入" |
| Q2 | b(抓 routing 真相,请求 A 实际给 B) | L18 router 真相 |
| Q3 | c(L27 content capture 进标准,privacy-by-default) | 呼应自己的追问 |

---

## 手做记录

`code/main.py` stdlib span emitter 匹配 GenAI 约定。**用户贴了真实阿里 TPP/deepagent trace 做了逐层拆解**——比 toy 代码有价值得多,概念已通过实物完全落地。

### 钩子
- **L24 Observability 平台**(Langfuse/Phoenix/Opik)= 用户看的那个阿里内部平台的开源对应物
- content 外存机制细节可回 L27
