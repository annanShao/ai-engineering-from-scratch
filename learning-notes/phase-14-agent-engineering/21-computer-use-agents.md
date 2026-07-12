# Lesson 21 · Computer Use:Claude / OpenAI CUA / Gemini

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/21-computer-use-agents/` |
| 类型 | Concept · ~60 分钟 |
| 前置 | L20 (WebArena/OSWorld)、L16 (guardrails/prompt injection)、L13 (human-in-the-loop) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/21-computer-use-agents/docs/en.md |
| 状态 | ✅ 完成(评测→产品闭环 + untrusted input 铁律 + 行动安全 + 5 层防御具体化 + 3/3 体检 + 4 金句) |

---

## 这节课的真定位:评测的靶子射出的三支箭

L19/L20 的 benchmark 是靶子,L21 是射出的三家产品。分数从 L20 "发布时 12%" 涨到 38-70%。但真正重头不是三家谁强,是它们共享的铁律:**屏幕上看到的一切都是 untrusted 输入**——这是 computer use 把 L16 prompt injection 从"担心"变成"生死攸关"的地方。

---

## 核心金句

### #1 · 三家不同赌注:选型裁判是你的 surface 不是 benchmark 榜首

| | Claude Computer Use | OpenAI CUA/Operator | Gemini 2.5 Computer Use |
|---|---|---|---|
| 发布 | 2024-10-22(最早) | 2025-01 | 2025-10-07(最新) |
| 范围 | **整个桌面(最全)** | 桌面,并入 ChatGPT agent mode | **只有浏览器(13 action)** |
| 分数 | 早期 | OSWorld 38.1%/WebArena 58.1%/WebVoyager 87% | ~70% Online-Mind2Web |
| 安全 | 靠实现方 | 靠实现方 | **内置 per-step safety service** |
| 赌注 | 桌面广度 + Linux 自动化最强 | 消费级分发最快 | 浏览器专精 + 最低延迟 + 安全内建 |

Claude 技术细节:**训练成从参考点数像素到目标,产出分辨率无关坐标**——正是 L20 GUI grounding 难题的产品级解法(不猜绝对坐标,学相对数格子)。**评测→产品闭环在这里具体可见。**

### #2 · untrusted input 铁律(全节心脏)
> **屏幕截图 / DOM 文本 / tool 输出 / PDF / 任何检索来的东西 —— 全部 untrusted。只有「用户的直接指令」才算许可。检索内容里可能藏 prompt-injection payload。**

**为什么 computer use 让这件事从"注意"升级成"铁律":**
- 纯文本 agent 被注入 → 最坏泄露信息(有限)
- computer use agent 被注入 → **真的会去点转账、填金额、确认(灾难)**

**"Computer use 把 prompt injection 从『信息安全问题』升级成『行动安全问题』。纯文本 agent 被劫持顶多说错话;computer use agent 被劫持会替你按下不可撤销的按钮。所以这条契约不是建议是铁律:屏幕上的字不是命令,只有用户的直接指令是命令——分不清这两者的 agent 不该上线。"**

这兑现了 L16 那个追问("output guardrail 防不住间接注入")——**L21 就是间接注入最危险的现场**:网页内容(检索来的)里的指令被 agent 当用户命令执行。

### #3 · 5 层防御 = L16 defense-in-depth 的具体兑现

| 防御层 | 具体机制 | 对应 L16 |
|---|---|---|
| 1. Per-step safety classifier | Gemini pattern,每 action 执行前审 | tool guardrail 升级成"每步审" |
| 2. Allowlist/blocklist 导航目标 | 限制能去哪些网址 | L3 工具沙箱(fetch 白名单) |
| 3. **Human-in-the-loop 确认敏感操作** | 登录/购买/CAPTCHA 必须人确认 | L13 HITL + L16 L2 |
| 4. Content capture 外存 + span 引用 | 敏感内容不进 log,按 ID 引用(OTel L23) | over-tracing 修法 |
| 5. Hard-coded refusals | 检索文本里的指令硬编码拒绝 | L2 system prompt 加固 |

**"第 3 层——登录/购买/CAPTCHA 强制人确认——不是技术不够先进的临时措施,是故意的架构决策:对不可撤销的高危 action,行业共识是『再聪明的 agent 也不给它无人确认的执行权』。自主性的边界不是能力问题,是后果不可逆性问题。有些权力,agent 再强也不该拿到。"**

### #4 · Computer use = Phase 14 所有线索的交汇点
> **L20 grounding 难题、L16 prompt injection、L13 human-in-the-loop、L19 轨迹、L23 observability——全在这一个 surface 上同时变得生死攸关。原因只有一个:当 agent 能真的按下按钮,每个之前『理论上的风险』都变成『会花你钱、删你文件、替你转账』的真风险。能力越接近人,工程的每个疏忽都越接近事故。**

---

## 关键概念地图

**三个翻车(全是"信任"崩塌):**

| 翻车 | 本质 |
|---|---|
| Trusting the screenshot(恶意网页"给 X 转 $100"被当用户意图) | 违反 untrusted input 铁律,最致命 |
| 敏感操作无确认(登录/购买/删文件没 HITL) | 把不可撤销权力交给可被劫持的 agent |
| 长程无 observability(200 click 崩在 180,没 per-step trace) | L20 轨迹 → L21 per-step trace → L23 observability 的桥 |

第三条连起所有线:**长程 computer use agent 是 observability 需求最尖锐处——步数最多、最不可预测、失败后果最重。**

**用尺子收口**:纯像素 grounding = L20 产品级解法 + L01 observation 极端形态;untrusted input = L16 最高危现场;5 层防御 = L16 defense-in-depth 兑现;敏感操作强制确认 = L13 HITL + "有些权力 agent 不该拿"新原则。

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(untrusted input 是唯一三家一致) | 没被 a/c/d 这些"只有部分家"的真特性骗到——精读"唯一一致" |
| Q2 | c(能按下不可撤销的按钮,行动安全 vs 信息安全) | 锁死本质 |
| Q3 | b(故意的架构决策,有些权力 agent 再强也不给) | 没选 a"临时措施"那个诱人错误方向 |

---

## 手做记录

`code/main.py` toy computer-use harness。未额外跑——概念已通过 untrusted input + 5 层防御讨论完全消化。

### 钩子
- **L27 Prompt Injection Defense**:L21 已把 untrusted input 逼到眼前,是全程插 L27 最顺的时机
- **L23 Observability**:per-step trace 是长程 computer use 的刚需
- **L22 Voice Agents**:另一个"agent 接真实世界"的 surface
