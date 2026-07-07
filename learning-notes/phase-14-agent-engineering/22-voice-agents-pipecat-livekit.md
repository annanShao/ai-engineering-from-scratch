# Lesson 22 · Voice Agents:Pipecat 与 LiveKit

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/22-voice-agents-pipecat-livekit/` |
| 类型 | Concept + Build · ~60 分钟 |
| 前置 | L01 (loop)、L14 (actor 消息控制)、L16 (黑盒 vs 透明)、L20 (grounding)、L27 (untrusted) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/22-voice-agents-pipecat-livekit/docs/en.md |
| 状态 | ✅ 完成(延迟预算新尺子 + loop 时序重构 + Pipecat/LiveKit 两路线 + 3/3 体检 + 3 金句) |

---

## 这节课的真定位:第一个"延迟即正确性"的 surface

语音 agent 不是文本 loop 接 TTS。它带来一个前 21 节从没认真出现的硬约束:**延迟预算(~600ms)**。前面 agent 可以"想 5 分钟",语音 agent 迟 200ms 用户就觉得卡。这重写了所有工程取舍。

---

## 核心金句

### #1 · 延迟即正确性(全新尺子)
> **语音 agent 是 Phase 14 第一个『延迟即正确性』的场景。前面 agent 迟 2 秒无所谓,答案对就行;语音 agent 迟 500ms 用户就重复、打断、挂断——慢本身就是一种错。**

延迟预算(2026 典型,加法关系):VAD 20-60ms + STT partial 100-250ms + LLM first token 150-400ms + TTS first audio 100-200ms + Transport RTT 30-80ms。
- **450-600ms = 高端**(像真人)/ 800-1200ms = 常见 / **>1500ms = 感觉坏了**

**残酷在于是加法**:5 环节每个"还行",加起来爆预算。语音工程核心不是"某环极致",是"每环都被延迟预算约束着取舍"。**上线前必须把整条链加起来。**

### #2 · "不是文本 loop 接 TTS":loop 时序被重构
> **文本 agent 的 loop 是回合制(你一句我一句,边界清晰);语音 agent 的 loop 是实时对抗(双方可能同时出声,边界要模型判断,还要能中途急刹)。turn detection 是个模型、barge-in 是条反向通道——这俩在文本世界根本不存在。**

| 维度 | 文本 agent | 语音 agent |
|---|---|---|
| 输入 | 一次完整 message | 持续流入音频分片(partial audio 默认) |
| "说完没" | 显然(按回车) | **要模型判断**(turn detection/VAD) |
| 打断 | 不存在 | **barge-in**——随时插话,agent 立刻闭嘴 |
| 延迟 | 秒级无所谓 | **~600ms 生死线** |

### #3 · MultimodalAgent vs VoicePipelineAgent = 延迟 vs 控制(L16 取舍语音版)
> **直接音频(Realtime)最快,但中间没文字你就没法做 guardrail/日志/文字层改写——你把控制权换成了速度。级联(STT→LLM→TTS)有文字层什么都能插手,但每次转换吃延迟。这和 L16『SDK 收多少进黑盒』是同一种取舍在语音场重演:黑盒换速度,透明换控制。**

---

## 关键概念地图

**两条路线(自己搭 vs 靠平台,框架篇选择的语音重演):**

**Pipecat——帧级流水线**:`Frame → FrameProcessor` 链,两流向:
- DOWNSTREAM(源→汇,主数据流):VAD(Silero)→ STT → LLM → TTS → transport
- UPSTREAM(反馈/控制,反向):cancellation(barge-in)/ metrics / 控制
- **双向设计正为 barge-in 而生**:用户打断,cancel frame 从 UPSTREAM 逆流而上掐掉 TTS。→ **UPSTREAM cancel = L14 actor 消息控制的实时版(逆流急刹);实时系统容错不是『重放』(L13)是『丢弃并追上现在』**

**LiveKit——WebRTC 平台**:`Agent/AgentSession/entrypoint/AgentServer`。两类:
- MultimodalAgent(直接音频,最快,无文字层)
- VoicePipelineAgent(STT→LLM→TTS 级联,有文字控制层)
- 还有:semantic turn detection(transformer)、native MCP、SIP 电话、50+ 模型免 key

**商业平台**:Vapi(~450-600ms)/ Retell(~600ms),建在上面。没 WebRTC 团队就用平台(L18 价值分层第 6 把尺子)。

**四个翻车(全是实时性崩塌):**

| 翻车 | 本质 |
|---|---|
| No barge-in handling(用户打断 agent 还在说) | 没 UPSTREAM cancel 通道 |
| **STT confidence ignored(低置信转录当圣旨)** | **感知误差当真相——L20 grounding / L27 untrusted 的语音版** |
| TTS mid-sentence cutoff | cancel 信号没传到 TTS |
| Latency budget ignored | 没把整条链加总就上线 |

**用尺子收口**:延迟预算=全新尺子;partial audio=L01 observation 实时形态;UPSTREAM cancel=L14 消息控制实时版;Multimodal vs Pipeline=L16 黑盒 vs 透明;STT confidence gate=L20+L27 感知误差(perception-based agent 通病:文本 agent 没这问题,一旦要"感知"屏幕/声音,感知误差就成新失败源);Vapi/Retell=L18 价值分层。

**"语音 agent 教你的核心不是『怎么接语音』,是『当延迟变成硬约束,agent 工程所有取舍都要重算』。这教训会外溢:任何实时 agent(语音/游戏/交易/机器人)都活在延迟预算里——语音只是第一个逼你直面『快也是一种正确』的 surface。"**

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(loop 时序被重构) | 没停在"模型更强/成本更高" |
| Q2 | b(延迟 vs 控制) | L16 黑盒/透明取舍语音版 |
| Q3 | c(L20 grounding/L27 untrusted——感知误差是新失败源) | 跨 3 surface(屏幕/文本/语音)看到同一抽象 |

---

## 手做记录

`code/main.py` 帧级 toy pipeline。未额外跑——概念已通过延迟预算 + loop 时序重构完全消化。

### 钩子
- **L23 Observability**:接 L22 的 metrics/tracing observer + L21 per-step trace + L27 content capture
- 实时 agent 的延迟预算思维会在 L29 production runtimes 再现
