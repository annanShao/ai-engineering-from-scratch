# Lesson 01 · The Agent Loop(Observe, Think, Act)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/01-the-agent-loop/` |
| 类型 | Build |
| 时长 | ~60 分钟 |
| 前置 | Phase 11 (LLM Engineering)、Phase 13 (Tools and Protocols) |
| 关键文件 | `docs/zh.md`(中文翻译)、`code/main.py`(toy ReAct loop) |
| 状态 | ✅ 完成 —— 阅读 + 概念评估 4/4 + Exercise 3 + 5 条金句 |

---

## 核心金句

### #1 · Observation Formatter 原则
> **工具错误必须变成 observation,不能变成 exception。模型修不了它看不见的东西。**

ReAct loop 第 5 个 ingredient。`code/main.py` 的 `ToolRegistry.dispatch` 用 try/except 把 tool error 吃成字符串塞进 observation,下一轮 LLM 看到错误文字才能自纠。若让异常 raise,整个 `for step in range(max_turns)` 主循环死,agent 任务终止。推广到生产:API 400 也必须以 observation 形式喂回去。是 Lesson 05 (CRITIC / Self-Refine) 的雏形。

### #2 · ReAct 循环是 Phase 14 的脊柱
> **Agent 用一个模式解决问题:一个循环,让模型决定暂停、调用工具、读取结果、继续思考。整个 idea 就这么多。Phase 14 后面 41 课都是围绕这个循环搭的脚手架。**

判断后续任何概念(ReWOO / Reflexion / LATS / MemGPT / LangGraph / verification gate / reviewer agent…)的方法:「它在为 ReAct 循环加什么?是替换了哪一步、扩展了哪一步、还是给某一步装监控?」框架间差异都在"循环周边",循环本身是不变量。

### #3 · 2022 `Thought:` → 2026 native reasoning channel
> **Prompt-based `Thought:` 是 hack,native reasoning channel 是模型能力。但 ReAct 循环的控制流是不变量。**

- 2022 普通 LLM 不会想,用 few-shot 诱导它在 output 流里写 `Thought:` / `Action:` 字符串,框架 `text.split()` 解析
- 2026 reasoning model(o1, o3, Claude 3.7+ extended thinking, R1)通过 RL 训出 native reasoning,API 返回结构化 block:`{type:"thinking",...}` 和 `{type:"tool_use",...}` 分开
- OpenAI o-series 把 reasoning 加密(`reasoning.encrypted_content`),客户端读不到明文,下一轮原样塞回去
- Letta V1 弃用 `send_message` + heartbeat 是同一波转向的落地

**Reasoning trace** = 一次 agent run 完整事件序列里 thought 步骤的子集。4 大用途:debug / eval (Lesson 30) / replay (Lesson 24) / distillation。OpenTelemetry GenAI 把 trace schema 标准化(Lesson 23)。

### #4 · CoT vs Native Reasoning
> **Native reasoning IS CoT 进化的终点,但不等于 CoT。CoT 是 prompting 技巧(任何 LLM 可用),native reasoning 是模型能力(RL 训出来的)。**

| 维度 | CoT (2022) | Native reasoning (2024+) |
|---|---|---|
| 本质 | prompting 技巧 | 模型能力 |
| 训练 | 不需要 | 大量 RL |
| 长度 | 几十–几百 token | 几千–十万 token |
| 结构 | 跟答案同一 output 流 | 独立 channel |
| 质量 | 表层 | 会回溯、自纠、试多个假设 |

**推论:** Sonnet / Haiku / GPT-4o 这种非 reasoning 模型,日常调用仍要用 CoT prompting —— 它们没 native channel,但 CoT 还能拉准确率。

### #5 · 自纠的前提是"错误可见" + "模型能重发"
> **让 agent 从 tool error 恢复,要两个零件咬合:(1) error 必须以 observation 形式进 history(金句 #1 的 observation formatter),模型才看得见;(2) 模型下一轮要能读到上一条 observation、判断它是 error、并重发一个修正后的 action。**

Exercise 3 的核心。ToyLLM 把"正确版本"写死在脚本里(`retry_args`,co-locate),是因为它不会推理;真实 reasoning model 从上下文自己想出修正 call。两个工程细节:`respond` 里只重试一次(`pop` 消费修正)防死循环、重试时不动 `cursor` 保住原计划。这是 docs 里 reasoning trace 第三件事("handle exceptions when an action returns an unexpected observation")的最小实现,接 Lesson 05 CRITIC / Self-Refine。

---

## 关键概念地图

**ReAct loop 的五个 ingredient**(缺一个就只是 chat bot,不是 agent):
1. 会增长的 message buffer
2. tool registry(name → callable,带 input validation)
3. stop condition(`finish` / 无 tool call / max turns / max tokens / guardrail)
4. turn budget(防无限循环;2026 agent 每任务跑 40–400 步)
5. observation formatter(tool output → 模型读得懂的字符串;400 error 也要变 observation)

**2026 三个坑:**
- Trust boundary collapse —— tool output 是 untrusted input(Lesson 27)
- Cascading failure —— agent 分不清"我失败"和"任务不可能",常在 400 上谎报成功(Lesson 26)
- Loop length explosion —— 40–400 步,debug 靠 observability (Lesson 23) + eval trajectory (Lesson 30)

**LLM → Agent → Harness 三层进化模型**(已讨论):
- LLM = 一次推理
- Agent = LLM + 5-ingredient 循环
- Harness = Agent + 生产形态包装(lifecycle / session 持久化 / 可观测 / sandbox / subagent 编排 / workbench surface)
- Anthropic SDK 阶梯:`anthropic` Client SDK = LLM 层,`claude-agent-sdk` = Harness 层(库),Claude Code CLI = Harness 层(产品)

---

## 手做记录

### Exercise 3 —— 让 agent 从 error observation 中自纠

**目标:** 验证金句 #1 + #5,做出 2026 CRITIC 式自纠的最小骨架。

**Step 1 —— 注入坏 args,先观察。** 把 script 第一步 `kv_set` 故意漏传 `value`:
```python
{"action": "kv_set", "args": {"key": "base"}}    # 漏了 value
```
跑 `python3 code/main.py`,trace 显示:
- `[02] kv_set({'key':'base'}) -> error: bad args... missing 'value'` —— 错误变 observation,**没 crash**
- 但 `[10] kv_get base -> missing:base`、`[11] final` 仍硬念"成功" —— "瞎子"agent **谎报成功**(Cascading failure 坑现形)

**Step 2 —— 让 `ToyLLM.respond` 会自纠。** 原 respond 只看 `cursor`、不看 `history`,改成:
```python
def respond(self, history):
    last_action = next((t for t in reversed(history) if t.kind == "action"), None)
    if last_action and last_action.observation and last_action.observation.startswith("error:"):
        bad_entry = self.script[self.cursor - 1]
        if "retry_args" in bad_entry:
            fixed = bad_entry.pop("retry_args")          # 消费 → 只重试一次
            return {"kind": "action",
                    "thought": f"observation was an error; retry {bad_entry['action']} with corrected args",
                    "action": bad_entry["action"],       # 用失败步骤自己的 tool 名，不写死
                    "args": fixed}
    if self.cursor >= len(self.script):
        return {"kind": "finish", "content": "no more actions"}
    entry = self.script[self.cursor]
    self.cursor += 1
    return entry
```
坏步骤自带配套修正:
```python
{"action": "kv_set", "args": {"key": "base"},
 "retry_args": {"key": "base", "value": "120"}}
```

**踩过/掰正的坑:**
- 一开始想把修正 hardcode 成 `kv_set` —— 不通用,万一翻车的是 `kv_get` 就帮倒忙。改成读 `bad_entry["action"]`,谁翻车修谁。
- 修正后的 `value`(120)模型推不出来 —— 这是 toy 的根本局限,只能 co-locate 在脚本里;真实 reasoning model 从上下文想出来。
- 重试不动 `cursor`(否则跳过原计划下一步)、`pop` 消费修正(否则死循环)。

**验证标准全中** ✅:trace 出现 `error: ...` observation;agent 没 crash;读到 error → 重发修正(`[04] kv_set(...,'value':'120') -> stored base`)→ 继续完成;`[12] kv_get base -> 120`(对比 Step 1 的 `missing:base`),final 是诚实成功。

**提交:** branch `claude/wonderful-hawking-1247L`,Step 1 = `894919d`,Step 2 = `93415bd`。
