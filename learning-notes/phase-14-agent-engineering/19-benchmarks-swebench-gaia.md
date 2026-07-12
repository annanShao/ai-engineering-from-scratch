# Lesson 19 · Benchmarks:SWE-bench、GAIA、AgentBench

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/19-benchmarks-swebench-gaia/` |
| 类型 | Concept · ~60 分钟 |
| 前置 | L05 (CRITIC)、L11 (evaluator)、L01 (observation formatter) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/19-benchmarks-swebench-gaia/docs/en.md |
| 状态 | ✅ 完成(运营篇第一课 + 三锚定 benchmark + 污染 + 分布 > 均值 + 3/3 体检 + 4 金句) |

---

## 这节课的真定位:从"造 agent"到"审 agent"的第一步

前 18 节教"怎么造 agent",L19 开始教"怎么知道造的 agent 到底行不行"。**审 agent 的第一课不是信数字,是不信数字、先查数字怎么来的。**

---

## 核心金句

### #1 · Benchmark 选错 = 测错东西
> **拿 GAIA 分数说『我代码 agent 强』,或拿 SWE-bench 说『我 agent 通用』,都是范畴错误。第一个 taste:先确认这个 benchmark 测的是不是你关心的那个能力。**

| Benchmark | 测什么 | 评测方式 |
|---|---|---|
| SWE-bench | 代码修 bug(2294 GitHub issue) | 应用 patch → 跑测试套件,FAIL_TO_PASS 翻绿 + 不破坏 PASS_TO_PASS |
| GAIA | 通才(466 题,人 92% / GPT-4+插件 15%) | 对人简单对 AI 难 |
| AgentBench | 多环境(8 个:代码/游戏/web/开放) | 多轮 4k-13k turns |

### #2 · SWE-bench 可信的根源:确定性 verifier 不是 LLM 自评
> **SWE-bench 是金标准不是因为题难,是因为它的评测器是确定性的真实测试套件。这正是 L05 那条主线:独立性强度 外部工具 > 异模型 > 异 prompt——代码天然有最强的确定性 verifier。一个 benchmark 可不可信,先看它的 evaluator 是『跑代码』还是『问 LLM 哪个更好』。**

SWE-agent(Yang 2024)发布 12.5%,靠强调 **agent-computer interface**(给模型好懂的文件编辑命令/搜索语法)提分——**又是 L01 "observation formatter 决定 agent 能不能想清楚" 的实证**:同模型,接口设计好,分数翻倍。

### #3 · 污染:报 benchmark 不提污染 = 撒谎
> **一个模型 SWE-bench 报 50%,在 SWE-bench+ 上可能只有 35%。声称 SWE-bench 成绩却不提 Verified 或 SWE-bench+,等于撒谎。**

| 污染事实 | 数字 |
|---|---|
| SWE-bench issue 早于多数模型 cutoff | >94% |
| SWE-bench+ 发现成功 patch 里解法泄漏在 issue 描述里 | 32.67%(直接抄到答案) |
| 因测试覆盖太弱而"可疑"的成功 | 31.08% |

**SWE-bench Verified**(OpenAI 2024-08):人工 curate 500 题子集,去歧义/去不可靠测试;是"能不能 ship 真 patch"主基准,但**也不是零污染**。数据污染本质 = 评测答案出现在模型能看到的输入/训练数据里,模型不是"解决"是"抄到"。

### #4 · 分布 > 单数字(运营篇新尺子)
> **SWE-bench 50% 这个单数字,信息量远不如 P50/P75/P95 的成本 + 步数分布。benchmark 给平均,生产事故永远发生在尾部——那个跑 400 步烧 $40 token 的 worst 1%。看 agent 不看分布只看均值,是运营新手最常见盲区。**

benchmark 测不到:真实运营成本(token/wall-clock)/ 对抗安全(L27)/ 你的领域(L30 custom eval)/ 尾部失败。

**Goodhart's Law**:指标一旦成为目标就不再是好指标。拿 SWE-bench 当 KPI 刷,agent 会越来越擅长 benchmark(学测试覆盖弱的捷径)、越来越不擅长真任务。

---

## 关键概念地图

**三个翻车**:Single-number fixation(只报 50%)/ Contaminated claims(不提 Verified/plus)/ Benchmark-as-development-target(Goodhart)。

**用尺子收口**:SWE-bench 测试套件 = L05b/L11 外部 ground truth;SWE-agent 靠 ACI 提分 = L01 formatter;污染 = 评测的"内化 vs 外部"(答案不该在模型见过的数据里);尾部 vs 均值 = 运营的新视角。

**"造 agent 的人问『平均能做多好』,审 agent 的人问『最差能坏成什么样、数字怎么测的、测的是不是我关心的事』。审的核心能力是怀疑数字。"**

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | C(确定性测试套件是可信根源) | 没停在"题多/够真实" |
| Q2 | B(数据污染——答案出现在模型能看到的输入) | 本质拿捏准 |
| Q3 | B(内行三连:污染?分布?测的是不是我关心的能力) | 没被"问参数/问价格"外行问题带走 |

---

## 手做记录

`code/main.py` toy SWE-bench harness(合成 bug-fix + FAIL_TO_PASS/PASS_TO_PASS 检查 + GAIA 式难度分类)。未额外跑——概念已通过污染 + 分布讨论完全消化。

### 钩子
- L20 WebArena/OSWorld 是评测另一半(界面操作)
- L30 custom evals 是"你自己领域"那块
- **元主线**:整个 Phase 14 皇冠宝石 = 外部 ground truth 能不能验证对错
