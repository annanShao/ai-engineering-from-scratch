# Lesson 10 · Skill Library 与 Lifelong Learning(Voyager)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/10-skill-libraries-voyager/` |
| 类型 | Build · ~75 分钟 |
| 前置 | Lesson 07 (MemGPT)、Lesson 08 (Letta Blocks) |
| 关键文件 | `docs/zh.md`、`code/main.py`(Skill + SkillLibrary 全套) |
| zh.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/10-skill-libraries-voyager/docs/zh.md |
| 状态 | ✅ 完成(阅读 + 概念深挖 + 5 金句;代码未跑) |

---

## 核心金句

### #1 · Action space 的层级升级:primitive → tool → skill
> **action 抽象层级越往上,行为越能"在时间上延伸"。primitive command 是最低层(`bot.moveTo(x,y)`,单步原子);tool(Lesson 06)是中层(`add(a,b)`,带 schema 的原子操作);skill 是高层(`craftIronPickaxe(bot)`,封装多步行为,内部调一堆 tool)。**

为什么 Voyager 要再往上抽一层?**因为复杂任务需要"一次调用 = 一段过程"**——agent 不在 prompt 里手写 50 步,而是 `await craftDiamondPickaxe(bot)`,函数内部自然把 50 步走完。primitive command 写不出复合任务,只有"代码作为动作"才能让行为时间上延伸、可组合、可复用。

### #2 · Skill library = Lesson 09 archival 的"how-to 升级版"
> **形态完全一样:store + 按 description 相似度检索。区别只在存储的对象:Lesson 09 存的是事实文本("ava lives in Lisbon"),Voyager 存的是可执行函数(`craftIronPickaxe`)。**

一句话:**memory 从存"知识 (what)"升级到存"how-to (how)"。** archival 是"我知道什么",skill library 是"我会做什么"。两者用同一套基建(向量索引 + 相似度检索 + 版本化 + 失效),只是内容形态不同。

### #3 · Iterative refinement = Self-Refine 用环境当 verifier
> **形态完全一样:generate → 跑 → feedback → 改 → 再跑。三种反馈信号:success / error(带 stack trace)/ self-verification failure。前两种本质是 Lesson 05 CRITIC 的 grounded verifier —— 环境(Minecraft runtime)直接告诉你跑没跑通、跑出什么错。代码生成场景天然有最强的独立 verifier(代码跑得通跑不通是确定性的)。**

闭环:Lesson 05 我们说"独立性强度:外部工具 > 异模型 > 异 prompt",**环境本身就是终极独立 verifier** —— Voyager 是把这条原则用到 code synthesis 上的标杆案例。

### #4 · Curriculum = 自动出题飞轮 + 最近发展区算法化(全节最值钱)
> **前面 9 节所有 agent 都假设任务由外部(用户/上游)给定 —— Voyager 是 agent 自己给自己出题。curriculum 综合"你会什么(skill inventory)+ 你周围是什么(环境状态)"提议下一个"刚好踮脚能做到"的新任务。这是质变,不是渐变。**

**为什么"刚高于当前能力"是甜蜜点:**
- 太简单 → 没学到新东西,原地踏步
- 太难 → 失败到放弃,信号丢失
- **刚高于能力(踮脚)→ 能完成且学到新 skill ✅**

这是心理学的 **Zone of Proximal Development(最近发展区,Vygotsky 1978)** 概念被算法化。**每完成一个甜蜜点任务,skill library 净增一个 skill,能力边界往外推一圈,curriculum 下次能提议的任务集就更大** —— 这是个**正向飞轮,agent 把自己往上推**。

### #5 · Voyager = 前 9 节关键模式的合流
> **Voyager 没发明新东西,它把前面几个模式缝成一个 lifelong learning 飞轮:**

```
curriculum(全新:自动出题)
    ↓ 提出"刚高于能力"的任务
library(Lesson 09 archival 升级版)
    ↓ 检索 + 组合相关 skill
refinement(Lesson 05 Self-Refine 用环境当 verifier)
    ↓ 失败 → 用 stack trace 重写
新 skill 入库 → 库变大 → curriculum 能提议更高任务 → 飞轮转下一圈
```

这就是 Voyager 论文 Minecraft 数据(3.3× 物品 / 8.5× 石器速度 / 6.4× 铁器速度)的解释:**任由它跑,能力指数级扩张**。

---

## 关键概念地图

**Voyager(Wang TMLR 2024)三组件:**
1. Automatic curriculum —— 好奇驱动的自动出题
2. Skill library —— 可执行代码 + description,按相似度检索
3. Iterative prompting —— 环境反馈驱动的精修 loop

**Action-space-as-code 的关键性质:**
- 时间上延伸(一次调用 = 一段过程)
- 可组合(skill 调 skill,拓扑排序执行)
- 可存储复用(入 library,跨 session 携带)
- 可版本化(refinement 触发 v2)

**Skill 结构:** name + description + code(string)+ version + tags + dependencies。`SkillLibrary` 表面:`register / search / compose / refine`。

**生态映射(2026):**
- **Claude Agent SDK skill(Anthropic)** —— Voyager 的 2026 产品化参考实现。**Claude Code 里的 `/skill`、`SKILLS.md` 就是这一脉**
- **skillkit**(npm)—— 跨 32+ AI coding agent 的 skill 管理
- **OpenAI Agents SDK tools** —— 低端;每个 tool 是个轻量 skill
- **领域自建** —— SQL skill 给数据 agent、Terraform skill 给基建 agent

**三个坑:**
- Library rot —— 同 skill 用稍异描述加 10 次 → 写入去重
- Composed-skill drift —— 子 skill 升 v2,父 skill 悄悄被升级 → 显式 pin 版本
- 检索质量退化(库 > 几百)→ vector 检索 + tag filter + 硬约束

**Phase 14 主线位置:** memory 三部曲(L07/08/09)之后的合流点。前面把"记住什么"做到位,这节回答"记住的怎么变成能用的能力"——把存储升级成可执行。

---

## 手做记录

代码未额外跑(toy `code/main.py` 实现 register / search / compose / refine 端到端,概念在追问里已通过手算 trace 把飞轮逻辑过了一遍)。

### Exercises
概念已覆盖。代码未额外实现。

---

## 本节最值钱的追问(我自己留的)

1. **Q1 ✅:tool vs skill 的层级关系** —— tool 原子化、skill 封装多步行为;两者都是"代码作为动作",只是抽象层不同。
2. **Q2 关键澄清:curriculum 不是编排器,是自动出题人** —— 它在比 library/composition 更上游的位置工作。引出"最近发展区"和"刚高于能力是甜蜜点"——这是 lifelong learning 飞轮的核心起点。
3. **Q3 三组件溯源** —— Library = archival 的 how-to 升级版,Refinement = Self-Refine 用环境当 verifier,Curriculum = 前所未见的"自动出题"。前两个是已学模式的应用,第三个是质变。

### 一个未深挖但值得后续追问的点

**curriculum 在生产里到底怎么实现?** Voyager 用好奇驱动的 LLM proposer。但课文也说"团队通常手动实现成 curriculum review"——这说明 production 里 curriculum 的算法化还不成熟,大多是手工列"还缺什么 skill"清单。**这个 gap 是不是 2026 production agent 还没解决的一块**?(可能在 Lesson 19/20 alignment / RL 那边有进一步答案。)
