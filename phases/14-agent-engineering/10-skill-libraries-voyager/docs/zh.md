# Skill Library 与 Lifelong Learning(Voyager)

> Voyager(Wang 等人,TMLR 2024)把**可执行代码当作 skill**。skill 是命名的、可检索的、可组合的,并被环境反馈精修。这是 Claude Agent SDK skill、skillkit、以及 2026 skill-library 模式的参考架构。

**Type:** Build
**Languages:** Python (stdlib)
**Prerequisites:** Phase 14 · 07 (MemGPT)、Phase 14 · 08 (Letta Blocks)
**Time:** ~75 分钟

## 学习目标 (Learning Objectives)

- 说出 Voyager 的三个组件 —— automatic curriculum、skill library、iterative prompting —— 各自的角色。
- 解释为什么 Voyager 把 **action space 定为 code**,而不是 primitive command。
- 用 stdlib 实现一个 skill library:注册、检索、组合、失败驱动的精修。
- 把 Voyager 的模式对应到 2026 Claude Agent SDK skill 和 skillkit 生态。

## 问题所在 (The Problem)

每个 session 都从零重建所有能力的 agent,犯三个错:

1. **浪费 token。** 每个任务都重新激发同样的推理。
2. **进度丢失。** session A 里学到的一个纠正,**没法迁移到 session B**。
3. **长程组合失败。** 复杂任务需要能力层级;one-shot prompt 表达不出来。

Voyager 的回答:把每个可复用能力**当作一个命名的代码块**,存进 library,**按相似度检索**,**和其他 skill 组合**,**靠执行反馈精修**。

## 核心概念 (The Concept)

### 三个组件 (Three components)

Voyager(arXiv:2305.16291)把 agent 结构化成:

1. **Automatic curriculum(自动课程)。** 一个**好奇驱动**的 proposer 根据 agent 当前 skill set 和环境状态挑下一个任务。**探索是自底向上的。**
2. **Skill library。** 每个 skill 都是**可执行代码**。任务成功时新 skill 入库。**按 query → description 相似度**检索。
3. **Iterative prompting mechanism(迭代式 prompting)。** 失败时,agent 拿到 execution error、环境反馈、self-verification 输出,然后精修 skill。

Minecraft 评估(Wang 2024):3.3× 更多独特物品、8.5× 更快造石器、6.4× 更快造铁器、2.3× 更长地图穿越——对比 baseline。**数字是 Minecraft 特有的,但模式可迁移。**

### Action space = code(动作空间 = 代码)

大多数 agent 发出 **primitive command**(原始命令)。**Voyager 发出 JavaScript 函数。** 一个 skill 长这样:

```javascript
async function craftIronPickaxe(bot) {
  await mineIron(bot, 3);
  await mineStick(bot, 2);
  await placeCraftingTable(bot);
  await craft(bot, 'iron_pickaxe');
}
```

由子 skill 组合。按 description 和 embedding 入库。**作为程序检索,不是 prompt。**

**这就是 2026 Claude Agent SDK 的 skill**:一个命名的、可检索的代码块 + 指令,agent 按需加载。

### Skill 检索

新任务 "造一把钻石镐"。agent:

1. embed 任务描述。
2. 在 skill library 查 top-k 相似 skill。
3. 取回 `craftIronPickaxe`、`mineDiamond`、`placeCraftingTable` 等。
4. 用取回的 primitive + 新逻辑**组合**出新 skill。

**这就是 MCP resource(Phase 13)和 Agent SDK skill 实现的模式**:在 knowledge/code 表面上做检索,scope 到当前任务。

### 迭代精修

Voyager 的反馈 loop:

1. agent 写一个 skill。
2. skill 跑在环境里。
3. 三种信号之一返回:`success` / `error`(带 stack trace)/ `self-verification failure`。
4. agent 用这个信号作为 context 重写 skill。
5. 循环到成功或 max round。

**这就是 Self-Refine(Lesson 05)应用到代码生成 + 环境锚定的验证。CRITIC(Lesson 05)是同一模式,只是把外部工具当 verifier。**

### Curriculum 与探索

Voyager 的 curriculum 模块根据 agent **有什么 / 还没做什么**,提"在湖边盖个庇护所"这类任务。proposer 用环境状态 + skill inventory 挑一个**刚高于当前能力**的任务——**探索的甜蜜点**。

对生产 agent,这翻译成一个 **"还缺什么(what's missing)" 算子**:给定当前 skill library 和领域,我们还没覆盖哪些 skill?团队通常手动实现成 curriculum review。

### 这个模式哪里会出问题

- **Skill library rot(库腐烂)。** 同一个 skill 用稍不同的描述加 10 次。**写入时去重**,检索只返回一个 canonical。
- **Composed-skill drift(组合 skill 漂移)。** 父 skill 依赖一个被精修过的子 skill。**给 skill 加版本**;pin 到 v1 的父 skill 不会神奇地升级到 v3。
- **检索质量。** vector retrieval 在描述上跑,库一过几百就退化。**用 tag filter 和硬约束补充**("只挑 `category=tooling` 的")。

## 动手做 (Build It)

`code/main.py` 用 stdlib 实现 skill library:

- `Skill` —— name、description、code(作为 string)、version、tags、dependencies。
- `SkillLibrary` —— register、search(token overlap)、compose(依赖拓扑排序)、refine(更新时版本号 +1)。
- 一个脚本化 agent:注册三个 primitive skill、组合第四个、撞上一个失败、精修。

运行它:

```
python3 code/main.py
```

trace 显示库写入、检索、组合、一次失败执行、v2 精修——Voyager loop 端到端。

## 用起来 (Use It)

- **Claude Agent SDK skill**(Anthropic)—— 2026 的参考实现:每个 skill 有 description、code、instructions;在 agent session 中按需加载。
- **skillkit**(npm:skillkit)—— 跨 32+ AI coding agent 的 skill 管理。
- **自定义 skill library** —— 领域特定(数据 agent 的 SQL skill、基建 agent 的 Terraform skill)。**Voyager 模式能 scale down(向下缩放)。**
- **OpenAI Agents SDK 的 `tools`** —— 在低端;每个 tool 是个轻量 skill。

## 交付出去 (Ship It)

`outputs/skill-skill-library.md` 为任意 runtime 生成一个 Voyager 形状的 skill library,带注册、检索、版本、精修接线。

## 练习 (Exercises)

1. 给 `compose()` 加一个**依赖循环检测**。skill A 依赖 B,B 依赖 A 时会发生什么?error 还是 warning?
2. 实现 **per-skill 版本固定(pin)**。父 skill 组合 `crafting@1` 时,`crafting` 升到 `@2` 不应该悄悄升级父 skill。
3. 把 token-overlap 检索换成 sentence-transformers embedding(或一个 stdlib BM25)。在 50-skill toy library 上测 retrieval@5。
4. 加一个 "curriculum" agent:给定当前 library 和领域描述,提 5 个缺失 skill。每周跑一次。
5. 读 Anthropic 的 Claude Agent SDK skill 文档。把 toy library 移到 SDK 的 skill schema。可发现性(discoverability)有什么变化?

## 关键术语 (Key Terms)

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| Skill | "可复用能力" | 命名的代码块 + description,按相似度可检索 |
| Skill library | "agent 的'怎么做'记忆" | skill 的持久 store,可搜索可组合 |
| Curriculum | "任务 proposer" | 自底向上的目标生成器,由当前能力 gap 驱动 |
| Composition | "skill DAG" | skill 调 skill;执行时拓扑排序 |
| Iterative refinement | "自纠 loop" | 环境反馈 + error + self-verification 回流进下一版 |
| Action-space-as-code | "程序化动作" | 发函数而非 primitive command,实现时间上延伸的行为 |
| Dedup on write | "skill 合并" | 近似 description 折叠到一个 canonical skill |

## 延伸阅读 (Further Reading)

- [Wang et al., Voyager (arXiv:2305.16291)](https://arxiv.org/abs/2305.16291) —— 最初的 skill-library 论文
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview) —— skill 作为 2026 产品化
- [Anthropic, Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) —— 实践中的 skill 和 subagent
- [Madaan et al., Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) —— Voyager 下面的精修 loop
