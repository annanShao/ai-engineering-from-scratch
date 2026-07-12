# Lesson 28 · Orchestration Patterns:Supervisor / Swarm / Hierarchical

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/28-orchestration-patterns/` |
| 类型 | Concept · ~55 分钟 |
| 前置 | L12 (workflow vs agent)、L13/L14/L15 (拓扑)、L16 (handoff)、L25 (debate)、L07 (context 预算) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/28-orchestration-patterns/docs/en.md |
| 状态 | ✅ 完成(四拓扑收束 + 升级阶梯 + hop counter 追问 + topology-first 反模式 + 免体检直接过) |

---

## 这节课的真定位:编排的收束课

把散在 L13/L14/L15/L25 的四种拓扑收成一个升级阶梯 + Anthropic 定海神针。核心不是教四种拓扑(都学过),是给"什么时候升到下一档"的判断。**就是 L12『谁拥有控制流图』用在『要不要多 agent、多到什么程度』上。**

---

## 核心金句

### #1 · 升级阶梯:每一档升级都要具体可证伪的痛点
> **从单 agent 开始,让痛点推着你升级,而不是让『multi-agent 听起来高级』拉着你升级。你无法说出上一档具体在哪撑不住,就没资格升下一档。这是 L12『复杂度是债务』可操作版——债务不是不能借,是每一笔都要有一张写明用途的借条。**

Anthropic 决策顺序:
```
1. 单 agent + workflow(L12)          ← 永远从这里开始
   ↓ 有 2-4 个真专家
2. Supervisor-worker
   ↓ 延迟比推理清晰度更重要
3. Swarm
   ↓ supervisor context 装不下所有专家描述
4. Hierarchical                       ← 严格:是 context 预算问题不是组织架构
   ↓ 准确率 > 成本
5. Debate
```

### #2 · 四拓扑(全学过)

| 拓扑 | 结构 | 特点 | 学过 |
|---|---|---|---|
| Supervisor-worker | 中央 router 派专家,专家不互通,全走中枢 | 清晰可控,换手过中枢 | L13/L14/L15 |
| Swarm/peer-to-peer | agent 直接握手,无中央 router | 延迟低(hops 少),难推理 | L13/L16 |
| Hierarchical | supervisor 管 sub-supervisor 管 worker | 撑大规模,运维复杂 | L13/L15 |
| Debate | 并行提议+交叉批评 | 不算编排算验证 | L25 |

**Supervisor 又见 2026 LangChain 改口**:用直接 tool call 做 supervision 而非 `create_supervisor`,给更细 context engineering 控制(你决定每个专家看到什么)——**L13→L16 折叠中间层这条线的官方终点。**

### #3 · Topology-first thinking 是反模式(L12 第一问的多 agent 版)
> **先决定要 multi-agent 再去找它解决什么问题——拿解决方案找问题,L12 反模式极致。正确顺序反过来:先有具体痛点(单 agent context 爆了/需要 2-4 个真专家/延迟压不下来),痛点自己会告诉你升到哪一档。L12 第一问『要不要 agent』在 L28 变成『要不要多 agent、多到哪档』,答案默认都是『先别』。**

---

## hop counter 追问(用户提问)

**handoff drift(交接漂移)**:swarm/handoff 模式里两个 agent 互相踢皮球无限交接(Billing→Support→Billing→...),没人觉得"这是我的活"。每个 agent 单看合理,合起来是**活锁(livelock)**——不崩溃但卡死,每跳烧 token(每 handoff 一次 LLM 调用)。

**hop counter**:hop=一次 handoff,数它跳几次,超阈值(如 max_hops=5)强制停(转人工/兜底/告警)。

```python
hops = 0
while True:
    result = current_agent.run(state)
    if result.is_handoff:
        hops += 1
        if hops >= max_hops: return escalate_to_human(state)
        current_agent = result.target_agent
    else: return result.final_answer
```

**为什么用"计数"不用"检测循环"**:漂移不一定是简单环(A→B→C→A→B→D→A),检测任意模式难,但"转太多次"信号简单可靠。**用粗但可靠的上限,替代精确但复杂的检测。**

**它的三个亲戚(同一个思想:给可能无限的传递链设硬上限)**:IP 包 TTL(每过路由器-1)/ 递归最大深度 / HTTP 最多重定向次数。**hop counter = TTL 搬到 agent 编排层。**

**呼应 L26**:handoff drift 不是模型不够聪明,是编排缺了一道 gate(hop 上限)——**你不 fix agent 让它更会判断,你 gate 它。"你不 fix 它,你 gate 它"。**

---

## 关键概念地图

**三个翻车(全是"为拓扑而拓扑")**:Topology-first thinking(识别问题前就要 multi-agent)/ Bouncing handoffs in swarm(A→B→A,用 hop counter)/ Fake hierarchy(三层因为"enterprise"实际两团队,折叠掉)。

**CrewAI Crew vs Flow 正交于拓扑但映射**:Flow(确定,生产起点)通常 supervisor/hierarchical;Crew(自主)通常 supervisor+LLM router。

**用尺子收口**:升级阶梯=L12 复杂度是债务可操作版;supervisor 改推 tool call=L13→L16 折叠中间层官方终点;hierarchical 升级条件=L07 context 预算;topology-first=L12 第一问多 agent 版;hop counter=L26 gate 思想。

**"agent 工程的成熟标志不是你会搭多复杂的系统,是你知道多简单就够、以及升级的每一步都指得出一个具体撑不住的地方。Anthropic『造适合你需求的系统,不是最复杂的系统』是这一整相的墓志铭。"**

---

## 手做记录

概念收束课,未跑代码。核心通过升级阶梯 + hop counter(TTL 的 agent 版)追问完全消化。

### 钩子
- **L29 Production Runtimes**:编排落到真上线运行时
- hop counter / 每步 gate 在自己实践里落地
