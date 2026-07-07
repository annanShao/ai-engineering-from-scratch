# Lesson 27 · Prompt Injection 与 PVE 防御(插队,在 L21 后)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/27-prompt-injection-defense/` |
| 类型 | Concept + Build · ~70 分钟 |
| 前置 | L16 (guardrails)、L21 (untrusted input)、L06 (tool)、L09/L13 (memory poisoning) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/27-prompt-injection-defense/docs/en.md |
| 状态 | ✅ 完成(Greshake 攻击理论 + 6 条防御教义 + PVE 架构 + 两轮红队级深度追问 + 免体检直接过)|
| 插队原因 | L16 埋钩子,L21 把 untrusted input 讲到骨头,趁热插最顺 |

---

## 这节课的真定位:agent 安全头号问题 + 可落地防御架构

Prompt injection 根源是 LLM 先天缺陷:**分不清"用户指令"和"检索内容里夹带的指令"**。这是 2024-2026 agent 安全的头号问题。这节给:攻击理论(Greshake 2023)+ 6 条防御教义 + PVE 架构。

**中心论断(Greshake)**:处理检索来的 prompt = 让攻击者在你 agent 的 tool 面上执行任意代码。你 agent 有什么 tool,攻击者就能用什么 tool——**tool registry 越强,攻击面越大。功能面 = 攻击面,同一个面。**

---

## 核心金句

### #1 · Indirect prompt injection:攻击者不接触你 agent,埋好 payload 等你撞上去
- Direct(老问题):用户自己输入"忽略指令"——攻击自己,危害有限
- **Indirect(真威胁)**:攻击者控制 agent 会读的内容(网页/PDF/邮件/记忆/搜索结果),agent 检索到就把里面的指令当命令

**5 种真实 exploit**:Data theft(外泄到攻击者 URL)/ Worming(自我传播蠕虫)/ Persistent memory poisoning(存进记忆下次自我再中毒)/ Ecosystem contamination(经共享记忆传染其他 agent)/ Arbitrary tool use(registry 里任何 tool 变可达)。

### #2 · 6 条防御教义全是外部控制(没一条是"训模型识别注入")
| # | 控制 | 见于 |
|---|---|---|
| 1 | 一切检索内容 untrusted(只有用户直接指令算许可) | L21 铁律 |
| 2 | Allowlist/blocklist 导航 | L21 |
| 3 | Per-step 安全评估(每个 action 执行前审) | L21 Gemini |
| 4 | Tool 输入输出加 guardrail | L16 + L06 |
| 5 | Human-in-the-loop 确认(登录/购买/CAPTCHA/发消息) | L21 |
| 6 | Content capture 外存(span 只带引用) | L21 + L23 |

**"这 6 条没一条是让模型更聪明地识别注入——全是外部控制。你不能靠训练模型『别上当』解决它(模型先天分不清指令来源),只能靠外部架构把危险行为拦在模型决定和真实世界之间。安全必须外部,不能内化。"**

### #3 · PVE(Prompt-Validator-Executor)= 核心可落地架构
```
主模型(贵,想调 tool) → 候选 tool 调用(未执行)
   → Validator(便宜快小模型,每个 tool 调用前跑):
       ① 动作和用户声明意图一致吗? ② 碰敏感面吗? ③ 参数有注入形状吗?
   → 通过 → Executor 真执行
   → 拒绝 → 告诉主模型"被拒了,换方法"(L06 error-as-observation)
```
代价:每 tool 调用多一次便宜推理。对绝大多数产品是便宜保险。

**"PVE 把『决定』和『执行』之间插了一道独立的关。validator 是独立的一次推理,问的不是『这内容说什么』而是『这动作符合用户本来意图吗』——用没被污染的视角审可能被污染的决定。这是 L05 CRITIC 独立 verifier 在安全场景的直接应用。PVE = guardrail(blocking)+ L05 独立 verifier + L06 error-as-observation 的组装,老零件重组。"**

### #4 · 防御失败 4 死法:位置比强度重要
| 死法 | 为什么致命 |
|---|---|
| No content-source metadata | 分不清"来自用户"vs"来自网页"→ 从根上无法区分权限,一切防御的地基 |
| All guardrails at the end | 模型已经碰过世界了,事后验证救不了不可撤销动作 |
| Relying on instruction-following alone | prompt 写"忽略 untrusted"不是 enforcement,是请求不是保证 |
| Overtrust of retrieved memory | 昨天的 agent 写毒记忆,今天的读了(L13 翻车 3 安全版) |

**"安全检查的位置比强度更重要——放错位置的强检查,不如放对位置的弱检查。"**

---

## 两轮红队级深度追问(超纲,免体检直接过)

### 追问 A · "Content capture 外存" 的澄清(我课里的歧义)
**外存不是"不让 LLM 看内容",是 observability/日志那一层的措施。** LLM 照常看到全部检索内容(要用它);"外存"指 span/trace 不放 prose、只放引用 ID,内容外存到 blob store。目的:隐私合规(prose 不流到第三方 observability 平台)+ 成本(日志不膨胀)+ 事后取证。**它本身不阻止注入,是 6 条里最不像防御的一条——它解决"出事后能查"。**
→ grep 输出**一定进上下文**(LLM 要拿它干活);能做的是进主模型前扫描/消毒(PVE),不是不让它进。

### 追问 B · 纯文本标签可被伪造 → 真实怎么标来源(红队思维)
**纯文本标签确实可绕**——delimiter injection / tag smuggling:攻击者在检索内容里埋 `</untrusted_content>` 伪造闭合,逃逸出"沙箱"伪装高权限。**押在文本标签上的方案是不可靠的。**

真实系统三层机制(从软到硬):
1. **结构化分离(content block)**——tool 结果走 API 的 `{"type":"tool_result", ...}` 结构块,不是拼进大字符串。攻击者能控制最里层 content 字符串的**内容**,控制不了外面 `type` **结构字段**(代码填的)。边界在消息结构,不在正文文本 → 伪造文本标签失效。
2. **特殊 token(tokenizer 层不可伪造)**——turn 边界用保留特殊 token;检索内容里字面写这个 token 的字符串,tokenizer 编码成**普通文本 token** 而非真正控制 token(独立 token ID,输入文本产生不了)→ 边界下沉到 tokenizer,文本够不着。
3. **安全训练(soft prior)**——训模型对 tool_result/检索内容里的指令默认降权。**但这是软的,不是 enforcement,强注入仍可能压过。**

### ⭐ 追问 B 钉进笔记的地基金句(用户独立推出)
> **"边界可以硬地【传到】模型面前(结构化 block + 特殊 token,不可伪造),但模型如何【对待】这个边界,永远是概率性的软行为。只要最终是一个把所有输入揉进注意力的文本模型,'把 untrusted 内容的指令当真'就永远是一个非零概率事件——这不是 bug,是当前架构的本质属性。"**
>
> **短版:"结构能保证边界不被伪造,但不能保证模型尊重边界。前者是密码学级的硬,后者是统计级的软。"**

**推论:in-band 标记永远会漏 → 真实安全不赌这道墙不漏,而是假设墙会漏,在墙后放不依赖模型正确理解来源的外部关(PVE/allowlist/HITL)。**

### 追问 C · per-step 的 "action" = 每次 tool 调用
审的是"要落地到外部世界的那一下"(tool call 已产生、未 execute 的那刻),不是每个 token、不是每轮对话。纯思考(Thought)不审,伸手碰世界(Action=tool call)才审。computer use 一任务 200 点击 = 审 200 次。

### ⭐ 追问 C/总纲 · 防御锚点从"内容可信度"搬到"动作-意图一致性"
> **"防注入的正确问题不是『我怎么识别恶意内容』(走不通,内容和标记都不可靠),而是『我怎么保证 agent 每个危险动作都符合用户原始意图』。把安全锚点从【内容可信度】搬到【动作-意图一致性】,是 2026 防御教义的思想核心——因为动作和意图是外部能独立判断的,内容可信度不是。"**

例:用户"总结这个网页",网页注入"转 $100"。旧思路判断"网页可信吗"(难,标记会漏);PVE 思路看到要调 `transfer_money`,问"用户让我总结网页怎么冒出转账?**动作和意图不一致**"→ 拦。**根本不需要判断网页可信不可信。**

---

## 完整安全模型(三句话,可自推)
1. **内容全 untrusted**——标记会漏、模型会上当,别赌。
2. **安全必须外部**——不靠训模型"别上当",靠外部架构兜。
3. **锚点是动作-意图一致性**——不问"内容可信吗",问"这动作符合用户原意吗",在决定和执行之间用独立 validator 卡住。

---

## 手做记录

`code/main.py` 实现 PVE(Validator 每 tool 调用跑参数形状检查 + 注入模式扫描;Executor 仅在放行后执行;演示正常调用通过 / 注入调用被抓 / 毒记忆触发拒绝)。未额外跑——概念已通过两轮红队追问远超体检深度。

### 钩子
- **L23 Observability**:content capture 外存 + span 引用的完整机制
- **L26 Failure Modes**:注入是失败模式的一个大类,横向系统化
- **L28 Orchestration / L29 Production**:PVE 在多 agent / 生产 runtime 里怎么部署
