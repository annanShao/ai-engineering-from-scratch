# Lesson 06 · Tool Use and Function Calling(工具使用与函数调用)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/06-tool-use-and-function-calling/` |
| 类型 | Build · ~60 分钟 |
| 前置 | Lesson 01 (Agent Loop)、Phase 13·01 (Function Calling Deep Dive) |
| 关键文件 | `docs/zh.md`、`code/main.py`(stdlib tool registry:schema 校验 + coercion + 并行 dispatch) |
| 状态 | ✅ 完成(阅读 + 3 钩子深挖 + 代码走读 + 4 金句) |

---

## 核心金句

### #1 · Toolformer 的 self-supervised 信号 = perplexity-based 数据筛选
> **用"固定权重模型 forward pass 算出的 next-token loss"当评分器,自动筛哪些 tool 标注值得拿去 fine-tune。loss 在这里扮演"评分函数",不是"梯度信号"。** 整个流程分两阶段:阶段 A 大量 forward pass 筛语料(不动权重),阶段 B 在筛过的语料上做常规 fine-tune(才动权重)。这是一个有名的范式叫 **perplexity-based data selection**,Toolformer 把它专门用在 tool 标注上。

**严谨澄清**:推理过程中**没有 loss,只有 logprobs**。loss 是 logprobs 在已知 label 上的聚合 `-Σ log P(t_truth)`。Toolformer 手里有语料(=label),才算得了 loss。这是个"模型主人的离线数据筛选 pipeline",不是 API 用户的 trick。

**接金句 #3(Lesson 04):** tool-use 时机被编译进权重 → 论文发现 tool use **随规模涌现**(小模型被拖累、大模型获益)→ 这就是 frontier 模型自带强 tool use,7B 模型常要显式 fine-tune 的根因。

### #2 · BFCL 暴露真相:function calling 解决了,agentic 没解决
> **V4 组成 = Agentic 40% + Multi-Turn 30% + Live 10% + Non-Live 10% + Hallucination 10%。单轮近乎解决;失败集中在四块:memory(跨轮)、动态决策(基于先前结果选 tool)、长程 chain(20+ 步 drift)、hallucination 检测(没合适 tool 时拒绝调用)。** 这四块几乎正好落在 Lesson 04 金句 #3 "留在外部"清单上 —— 模型内生的 tool 调用被内化,harness 层的状态/记忆/长程问题依然难,因为它们触及权重之外的世界。

**衍生洞察:** "function calling 能力" ≠ "agentic 能力"。单轮强不代表 agentic 稳——瓶颈早不在 tool-call 语法,在周围的状态/记忆/推理。Hallucination 那 10% 背后是"过度有用"偏置:对齐过的模型有强烈"想帮忙"倾向,没 tool 也硬造。

### #3 · State-based eval = grounded verification 应用到 benchmark 本身
> **BFCL V3 转向:不查"tool call 的 AST 是不是匹配",而查"世界最终是不是对的状态"(文件创建了吗?数据库进新行了吗?)。** AST-matching 误判多解(同目标常有多种合法 tool 序列);state-based 只看结果,不看路径。这跟 CRITIC 是同一套哲学——"验证 > 思考"不只给 agent 用,**给 benchmark 用也一样**。CRITIC 是 agent 内部的 grounded check,state-based eval 是 benchmark 外部的 grounded check。

### #4 · "校验失败必须返回结构化 observation,绝不 raise" —— 闭环金句 #1
> **`dispatch` 三条失败出口(unknown tool / validation error / execution error)全部返回结构化 ToolResult,从不 raise 给 loop。** 进一步:错误字符串本身要是 mini-critique(`"'in_progress' not in ['open','closed','pending']"`),告诉模型**怎么改**,而非"failed"。这是 Lesson 01 金句 #1 在最底层的形态,也是 Lesson 05 grounded critique 驱动 refine 的输入侧——一条好的 error observation,本身就是驱动模型自纠的信号。

工程承重件:
- **`tool_use_id` 是 correlation ID**——并行调用时交换它就"错结果配错 tool"
- **tool description 是承重的**——烂 description 是"选错 tool"失败的头号根因
- **通用 `run_shell(cmd)` 危险,具体 `git_status()` 安全**——sandbox 边界

---

## 关键概念地图

**Toolformer(Schick 2023):** self-supervised tool annotation。流程见金句 #1。覆盖 calculator、QA、search、translator、calendar。

**BFCL V4(Patil 2025):** 2026 事实评估标准,五类目见金句 #2。state-based eval 见金句 #3。

**Tool schema(provider 通用形状):**
```
name + description(承重)+ input_schema(JSON Schema:properties, required, types, enums)
```
Anthropic 用 `input_schema`,OpenAI 用 `function.parameters`,都吃 JSON Schema。

**Argument validation 四类:**
1. Type coercion(string `"5"` → int 5,无歧义就转、有歧义拒绝)
2. Enum validation(描述性 error 告诉合法集合)
3. Required fields(缺必填立刻 error observation,不 crash)
4. Format validation(日期/email/URL 用具体 parser,不用 regex)

**Parallel tool calls 流程:**
1. 模型发 K 个 tool call,各自不同 `tool_use_id`
2. runtime 执行(独立的并行)
3. 每结果作为 `tool_result` block,按 `tool_use_id` 路由回去

**Sandboxing(详见 Lesson 09):** per-tool read/write surface、网络访问、timeout、内存上限。通用 `run_shell` 危险,具体 `git_status` 安全。

**这节在 Phase 14 主线的位置:** 把"最底层那块砖"(tool call 本身)敲实。前五节默认 tool 调用可靠,这节回头建可靠性。

---

## 手做记录

### 跑 demo(5 calls in one turn,展示并行 dispatch + 全部失败模式)

```
catalog (presented to model):
  - add: Add two integers a and b. Use for any integer addition.
  - multiply: Multiply two integers a and b. Prefer multiplication over looped addition.
  - classify: Classify a status as one of the allowed labels.

parallel dispatch:
  u01 OK : 5                                          # 基本 dispatch + tool_use_id
  u02 OK : 20                                         # coercion 把 "4"(str) 转 4(int)
  u03 ERR: 'in_progress' not in ['open','closed','pending']  # enum 校验 + mini-critique
  u04 OK : classified as open                         # enum 合法值
  u05 ERR: unknown tool 'subtract'                    # BFCL Hallucination 类目真人版
```

**代码 → 概念映射:**
- `_coerce()`(line 36)= type coercion(`"4"`→4)
- `validate()`(line 75)= required + enum + min/max 校验,所有失败累积到 errors list 返回
- `dispatch()`(line 123)= 三条失败出口(unknown / validation / execution),全部返回结构化 `ToolResult`,**从不 raise**
- `ToolCall.tool_use_id`(line 24)= correlation ID,5 个并行 call 靠它路由回去

**实证闭环:**
- Lesson 01 #1 在最底层的形态 = `dispatch` 三出口永不 raise
- Lesson 04 #3 留在外部的清单 = BFCL 没解决的四块全在那
- Lesson 05 grounded critique = `u03` 那条 enum 错误字符串本身就是
- Lesson 06 本身 = Toolformer 把 tool-use 内化(bitter lesson)+ BFCL state-based eval 把 grounded 思路上抬到 benchmark 层

### Exercises
概念已覆盖。代码未额外实现(stdlib registry 已涵盖核心生产形态)。
