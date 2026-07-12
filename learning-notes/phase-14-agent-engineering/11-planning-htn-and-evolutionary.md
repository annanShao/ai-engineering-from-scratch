# Lesson 11 · Planning:HTN 与 Evolutionary Search(ChatHTN + AlphaEvolve)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/11-planning-htn-and-evolutionary/` |
| 类型 | Concept + Build · ~75 分钟 |
| 前置 | Lesson 02 (ReWOO/Plan-Execute)、Lesson 04 (ToT/LATS)、Lesson 05 (CRITIC)、Lesson 10 (Voyager) |
| 关键文件 | `docs/en.md`、`code/`、`notebook/` |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/11-planning-htn-and-evolutionary/docs/en.md |
| 状态 | ✅ 完成(两半都覆盖:HTN/ChatHTN 概念 + AlphaEvolve/MAP-Elites 深挖 + loop-engineering 跨框架综合 + 3/3 体检;代码未跑) |

---

## 这节课的真正结构(别只记住 AlphaEvolve)

ReAct / ReWOO / Plan-Execute 覆盖大部分 agent 规划,但有**两个洞**补不了。
本节给出**两个不同的答案**,共享同一个哲学:

| 洞 | 答案 | 要的是什么 |
|---|---|---|
| ① 计划必须「构造即正确」 | **HTN + ChatHTN** | 可证明 soundness(排班/合规/航线——LLM 幻觉一步即灾难) |
| ② 要的不是「对的计划」而是「最优解」 | **AlphaEvolve** | 机器可验 fitness(矩阵乘法/调度/编译器) |

> **共同哲学:把硬约束(正确性 / 最优性)锁死在【外部】,把创造力交给【LLM 内部】。LLM 是放大器,不是替代品。**

---

## 核心金句

### #1 · ChatHTN:LLM 负责想,符号层负责审
> **"每个产出的计划都可证明 sound,因为 LLM 的建议只能作为『候选拆解』进入,永远不能直接改计划。符号层拥有正确性,LLM 扩充 method 库。"**

ChatHTN(Gopalakrishnan 2025, arXiv:2505.11814)的循环:① 用现有 method 拆 compound task → ② 拆不动就问 LLM 怎么拆 → ③ 把回答翻成候选子任务 → ④ **用 operator schema 校验,非法直接拒** → ⑤ 递归。

**用尺子劈:这是 CRITIC(L05)的孪生兄弟,方向反过来。** CRITIC 是「LLM 生成答案 + 外部工具验答案」;ChatHTN 是「LLM 提议拆解 + 符号层校验拆解」。**内化的是创造性拆解,外部锁死的是 soundness。**

坑:HTN 没有 operator schema → soundness 主张崩塌(没东西去 reject 非法拆解)。
延伸:online method learning(2025 follow-up)用回归把 LLM 拆解泛化成新 method,LLM 调用频率砍 75%——「把外部循环学到的沉淀下来」,和 STaR 一脉。

### #2 · AlphaEvolve:LLM 是工厂里的临时工,不是产品里的员工
> **AlphaEvolve = 把 LLM 当『会读上下文的智能变异算子』,装进真·进化算法,对【代码】做世代繁衍。淘汰靠真实运行的 evaluator,种群存外部 archive,世代靠 archive 跨上下文传承。**

成果(Novikov 2025, arXiv:2506.13131,DeepMind):4×4 复矩阵乘法 48 次标量乘(破 Strassen 1969 的 49 次,56 年未破)/ Borg 调度 +0.7% / FlashAttention +32%。

**最反直觉的一句:整个发现过程,Gemini 权重一次都没动。**「权重是基因,archive 是文化。这个项目没改基因,改的是文化的传承机制。」→ 这就是它放在 agent-architecture 相而非 fine-tuning 相的原因。

硬约束:fitness 必须机器可验、确定、快。「问 LLM 哪个更好」不是 fitness,进化在 prose 上不收敛。

### #3 · Diff-based mutation:形式选择决定能力上限(同构 L01 formatter)
> **FunSearch 让 LLM 重写整个函数;AlphaEvolve 让 LLM 只输出 diff。**

为什么这个细节是命门:① 支持整个 codebase 级演化(不只一个函数);② **small-step mutation 是进化算法的理论支柱**——保住父代结构、只探索局部邻域,大跨度重写会高概率毁掉已积累的优势;③ token 成本骤降(看父程序但只输出 diff)。

→ 和 L01「observation formatter 决定模型能不能想清楚」同构:**你让 LLM 用什么形式产出,决定了系统的天花板。**

### #4 · MAP-Elites:不排队选第一,给每种长相发一张「本类冠军」
> **MAP-Elites(Mouret & Clune 2015,"Illuminating search spaces by mapping elites")用『行为多样性』对抗『种群塌缩』,让进化永远留着通往别的山峰的种子。**

痛点:top-K 会让种群塌缩到一个局部最优,所有 elite 长一样,失去探索 B 峰的种子(B 峰前要先下谷底,top-K 不许「暂时变差」的个体活)。

一招:**不按分数排队,按『行为特征维度』(behavior descriptor,通常与分数无关)切网格,每个格子各留一个 elite。** 算法灵魂在「竞争上岗只跟同格子的现任比,不跟全局比」。产出不是一个点,是**一整张『解的地图』**——照亮整个空间。

三个本质连接:
- **vs L04 exploration/exploitation** —— 把探索-利用从单次搜索抬到种群层面再现一次。
- **vs L09 Mem0 fusion** —— 都在拒绝「单一标量排序会丢信息」;Mem0 用加权和在多维补偿,MAP-Elites 用网格在多维保多样。
- **LLM 变异 + 多样 archive 是绝配** —— archive 提供风格各异的 elite 当 in-context 灵感,LLM 做「跨风格杂交」,这是随机变异做不到的。这部分回答了「LLM 变异凭什么强过随机变异」。

⚠️ `behavior_fn`(选哪几个行为维度)是**人设计的,不是学出来的**——这正是领域 loop engineering 最吃功夫、最像艺术的一步;选错维度,archive 照亮的是错误空间,搜索白跑。

### #5 · 跨框架顿悟:LLM-in-the-loop 是一个元范式,有三个物种
> **DSPy / AlphaEvolve / Claude Code(loop engineering)/ STaR 全套同一个三拍骨架:生成候选(LLM)→ 评测打分(evaluator)→ 择优回写(archive/state)→ 再采样。骨架相同 ≠ 同一种东西;决定本质差异的是『被优化的产物是什么、回写到哪里』。**

**用『内化 vs 外部』尺子把家族劈成三个物种:**

| 物种 | 代表 | 进化什么产物 | 回写到哪 | 改权重 |
|---|---|---|---|---|
| **A 外部产物优化器(离线)** | DSPy(prompt)、Promptbreeder(prompt)、AlphaEvolve/FunSearch(代码)、ADAS(agent 架构) | prompt / 代码 | 外部产物文件 / archive | ❌ |
| **B 内化优化器** | STaR、ReST、self-rewarding、RLAIF | **模型权重** | **权重(基因)** | ✅ |
| **C 在线执行循环** | **Claude Code**、Devin、Cursor、Aider | 无固化产物,**循环本身就是产品** | working tree / 对话 | ❌ |

关键分野(DSPy vs AlphaEvolve):**DSPy 优化『问法』,LLM 留在产品里(长期员工);AlphaEvolve 优化『答案』,LLM 用完即弃(工厂临时工)。** → 「DSPy 把 LLM 留在产品里,AlphaEvolve 把 LLM 留在工厂里。」

**分类器用法:看到任何号称『自进化』的新系统,先问一句——「它回写到哪?prompt?代码?还是权重?」答案决定它是谁的表亲、能力上限、成本结构。**

### #6 · Loop Engineering = Phase 14 这一相被工业化 + 命名
> **Anthropic 圈子的口号「Stop prompt engineering, start loop engineering」,翻译成本相语言就是:别迷信那一句完美 prompt,去设计那个能自己迭代到答案的循环。**

- 能力公式从 `LLM × Prompt` 升级到 `LLM × Prompt × Scaffold × Verifier × Archive × Iteration`——后面每一项都是 Phase 14 拆过的零件。
- **Claude Code 的内循环 = 微型运行时 AlphaEvolve**:变异=edit,evaluator=pytest/build,archive=working tree(单 elite),选择压力=测试通过/失败。它几乎用上了本相每个零件,少一个都不工作。
- **Loop engineer 的五项核心技能**(全是 Phase 14 教过的):选 ground truth(L05)、选状态持久化(L07/09/10)、选终止条件(L02/03)、选失败模式(L06 error-as-observation)、选搜索压力(L04/10/11)。

**反直觉推论:Claude Code 越普及,loop engineering 越值钱。** 通用 loop 把所有人拉到同一起跑线;**领域 loop(为药物/芯片/SQL/某流程设计的 evaluator + archive 维度)是新的护城河。** → 「通用 loop 把所有人拉到同一起跑线;领域 loop 是新护城河。」

---

## 关键概念地图

**整节一张图:**
```
        ReAct / ReWOO 解不了的两个洞
      ┌──────────────┴──────────────┐
   「要可证明正确」              「要机器可验的最优」
   排班/合规/航线                 矩阵乘法/编译器/调度
      │                              │
   HTN + ChatHTN                 AlphaEvolve
   符号层拥有正确性            evaluator 拥有 ground truth
   LLM 扩充 method 库         LLM 当变异算子 + MAP-Elites 保多样
      └──────── 共同点:LLM 是放大器不是替代品 ────────┘
           正确性/最优性锁外部,创造力交内部
```

**HTN 四零件:** Tasks(compound/primitive)· Methods(带 precondition 的拆解配方)· Operators(带 precondition/effect 的 primitive)· State(事实集)。规划=找一条拆到 primitive、每步 precondition 都满足的路径。HTN 是 L10 Voyager skill 组合的「带形式化校验的近亲」。

**何时用哪个(课文表):** 硬约束排班→HTN;编译器优化→AlphaEvolve;多步任务执行→ReAct/ReWOO;带测试的代码改进→AlphaEvolve(测试即 evaluator);策略约束自动化→HTN(precondition 编码 policy)。**大多数任务两个都不需要,先上 ReAct/ReWOO。**

**AlphaEvolve 五组件 → 内化/外部:**
- `llm.generate(diff)` —— 内化(L01)
- `build_prompt(+inspirations)` —— 混合(L09 retrieval)
- `archive.sample` —— 算法外挂(L04 UCT 风格)
- `archive.add` / `compiles()` gate —— 外部(L07/L10 / L06)
- `evaluator(child)` —— **外部 ground truth ✅✅**(L05b CRITIC)

**MAP-Elites 伪码灵魂:** `if cell not in archive or score > archive[cell].score: archive[cell] = child` —— 只和同格子现任比。

---

## 体检 · 3/3 ✅

| # | 题 | 答 | 点评 |
|---|---|---|---|
| Q1 | diff-mutation 最本质原因 | B(small-step mutation 是进化理论支柱) | 没被「省 token」(A,真但不本质)带走 |
| Q2 | 模型没更新说明什么 | B(能力=模型+scaffolding;思考被分散到几十万次评测) | 抓住主线 |
| Q3 | 套到新领域第一件事 | C(能不能写出自动 evaluator) | 锁定 ground truth 锚点,没去先挑模型/写 prompt |

---

## 手做记录

代码 / notebook 未额外跑(概念已通过 MAP-Elites 手算 trace + 三物种分类 + Claude Code 内循环映射充分覆盖)。

### Exercises
概念已覆盖。代码未额外实现。

### 留给后续追问的点
1. **进化 vs 梯度(RL)**:既然 evaluator 都有了,AlphaEvolve 为何不直接 RL?——「进化 vs 梯度」三种搜索压力(进化/贝叶斯/梯度)的本质区别,留到后续。
2. **DSPy BootstrapFinetune** 横跨 A/B 两物种的「两栖动物」,值得单独拆。
3. **领域 loop 设计实操**:挑一个真问题(SQL 优化等)现场走一遍 evaluator/archive/终止条件——比读 paper 更值,留作 Phase 15+ 入口。
