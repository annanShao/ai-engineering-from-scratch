# Lesson 25 · Multi-Agent Debate 与协作

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/25-multi-agent-debate/` |
| 类型 | Concept + Build · ~60 分钟 |
| 前置 | L05 (Self-Refine/CRITIC)、L14 (topology)、L12/L13/L16 (落地积木)、L22 (延迟预算) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/25-multi-agent-debate/docs/en.md |
| 状态 | ✅ 完成(L05 第三种模式 + Society of Minds + 稀疏拓扑 + debate 的赌注 + 3/3 体检 + 3 金句) |

---

## 这节课的真定位:L05 那道题的第三个答案

Self-Refine(自评,groupthink 风险)vs CRITIC(接外部工具,但工具不总有)。**Debate 是第三种:N 个模型实例各自独立作答,互相批评,靠分歧收敛。核心:没有外部 ground truth 时,用多样性人造独立性。**

独立性阶梯(L05):**外部工具(CRITIC)> 异模型 debate(L25)> 异 prompt > 同模型自评(Self-Refine)**。

---

## 核心金句

### #1 · Debate = 没有外部真相时,用多样性人造独立性(赌注)
> **CRITIC 借的是外部世界的真(工具/DB/代码);debate 借的是『N 个视角不会同时错在同一处』的统计假设。前者是真独立,后者是赌独立——debate 的成败全看那个赌注:这 N 个 agent 真的独立吗?**

**Society of Minds(Du et al., ICML 2024)**:N 实例独立作答 → R 轮各自读别人答案+批评+更新 → 收敛。原始 N=3,R=2。难题上 agent 越多轮越多准确率越高(MMLU/GSM8K/象棋/传记)。**跨模型 > 单模型(ChatGPT+Bard > 任一)**——直接验证赌注:同模型多实例会犯相似错(同源偏见),异构模型才是真独立,量化了 L05『异模型 > 异 prompt』。

### #2 · 成本在连接密度不在节点数(呼应 L14 topology)
> **Full-mesh critique 是 O(N²),sparse(star/ring/hub-spoke)是 O(N)。N=5 R=3:full-mesh 60 次 critique,star 12 次,降 80% 成本准确率持平。多 agent 系统成本主要在连接密度不在节点数量——debate 工程艺术是设计连接结构,不是加更多 agent。**

和 CrewAI Hierarchical token tax、LangGraph conditional edge 滥用同一个教训:**连接结构决定成本**。

### #3 · Debate 是贵的重武器,只对"多合理答案 + 错误代价高"值得
> **有用:事实性(交叉验证降幻觉)/ 规则遵循(象棋一个漏别人抓)/ 开放推理(多 framing 收敛)。有害:延迟敏感 UX(N×R 串行轮次——呼应 L22 延迟预算,语音里用不起)/ 成本敏感规模(N×R 倍 token)/ 简单事实查询(查一次比 debate 五次便宜)。**

L12"复杂度是债务":debate 必须用"降低的错误率"挣回"N 倍成本",挣不回别用。

---

## 关键概念地图

**三个翻车(全是独立性崩塌):**

| 翻车 | 本质 | 缓解 |
|---|---|---|
| Convergence collapse(全收敛到第一个错答案) | 群体思维 | 强制"分歧轮" |
| Hub failure(star 里坏 hub 污染所有人) | 中枢单点故障 | 轮换/多 hub |
| **Prompt homogenization(同 prompt→同答案)** | **假独立——头号死法,看着 N 个 agent 其实是 1 个** | 多样 prompt/模型 |

**"你开 5 个 agent 用同一 prompt 同一模型,以为有 5 个独立视角,实际有 5 个几乎一样的视角,一起犯同一错。debate 价值=独立性,假独立=花 5 倍钱买 0 收益。第一设计问题永远是:怎么保证这 N 个 agent 真的不一样?"**

**2026 落地形态(全是学过的积木)**:Anthropic orchestrator-workers+synthesis(L12)/ LangGraph supervisor+specialist(L13,debate 作为 node)/ OpenAI SDK handoff 迭代批评(L16)/ debate+evaluator-optimizer 做 eval 信号(L05+L24)。**debate 没发明新原语。**

**用尺子收口**:debate = L05 独立性阶梯第三档;稀疏拓扑 = L14 topology 成本工程;延迟敏感 = L22 延迟预算;贵重武器 = L12 复杂度是债务。

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(多样性人造独立性,L05 第三档) | 锁定核心 |
| Q2 | b(成本在连接密度 O(N²) vs O(N)) | 呼应 L14 |
| Q3 | b(假独立=花 5 倍钱买 0 收益) | 直击 debate 命门 |

---

## 手做记录

`code/main.py` debate toy。未额外跑——概念已通过"debate 的赌注 = 独立性"完全消化。

### 钩子
- **L26 Failure Modes**:debate 三翻车 + L13/L14/L22 散落翻车点收成系统表
- debate 作为 eval 信号(L30 eval-driven)
