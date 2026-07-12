# Lesson 05 · Self-Refine and CRITIC(迭代式输出改进)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/05-self-refine-and-critic/` |
| 类型 | Build · ~60 分钟 |
| 前置 | Lesson 01 (Agent Loop)、Lesson 03 (Reflexion) |
| 关键文件 | `docs/zh.md`、`code/main.py`(Self-Refine vs CRITIC 对比) |
| 状态 | ✅ 完成(阅读 + 3 钩子 + 代码对比 + 3 金句) |

---

## 核心金句

### #1 · CRITIC 只改一步(feedback→verify),靠的是"独立性"
> **Self-Refine = 单模型扮 generate→feedback→refine 三角色的自我精修 loop;CRITIC 只把其中 feedback(模型自评)那一步换成 verify(调外部工具拿 ground truth)。** 强弱的本质是 judge 的独立性:同模型异 prompt < 异模型 < 外部工具。外部工具的错误分布和生成器完全无关,独立性拉满 → critique 最可信。

机制:同模型+同 prompt 自评会橡皮图章,因为 critique 抽样自和输出同一个分布——模型觉得自己的输出"很可信"(hallucination 在产生它的模型眼里很有说服力)。破法 = 制造独立性。

### #2 · refine/critique 的 history 必须是"累积",不是"上一条"
> **refine 看的是全部历史 output+critique 的累积,不是只看最近一条。** 只看上一条会犯早先已改过的错、来回震荡;全量 history 让模型记得"哪些路已经走死"。和 Lesson 03 Reflexion 的 episodic memory 同一个洞察:把过去累积喂回去。论文消融:去掉 history 质量急剧下降。

### #3 · 没有外部 verifier,CRITIC 退化成 Self-Refine
> **CRITIC 的全部增量就在那个外部 verifier。** 任务若没有可调的 ground truth tool(创意写作、纯格式偏好),verify 无工具可用,只能退回自评,此时 CRITIC ≡ Self-Refine。推论:别在没 verifier 的任务上硬上 CRITIC,白付延迟。判断该不该上 CRITIC = 问"这任务有没有便宜可靠的外部 verifier"。

---

## 关键概念地图

**Self-Refine(Madaan 2023):** 一个 LLM 三角色 `generate → feedback → refine`,refine 带 history,loop 到"no issues"或预算耗尽。7 任务平均 +20,无训练无工具。

**CRITIC(Gou 2023):** 把 `feedback(task,output)` 换成 `verify(task,output,tools)`,tools = search / code interpreter / calculator / 领域 verifier(测试、type checker、linter)。critique 锚定在 tool 结果上。事实任务优于 Self-Refine。

**stop condition(绝不用单一条件):** verifier passes OR(模型说没问题 AND 迭代≥2)OR 迭代≥max。

**Evaluator-Optimizer(Anthropic 五 workflow pattern 之一):** evaluator 打分 + optimizer 修订,循环到通过。关键工程细节:两者 prompt 要显著不同,否则橡皮图章。

**OpenAI Agents SDK output guardrail:** 跑在最终输出上的 validator,触发则拒绝+重试。可调工具(CRITIC 式)或纯函数(Self-Refine 式)。

**三个坑:** rubber-stamp loop(同 prompt 自评→"看着挺好",用异 prompt/异模型破)/ over-refinement(每轮加延迟,预算 1-3 轮)/ 在无 verifier 任务上用 CRITIC(退化还白付延迟)。

**这节在 Phase 14 主线的位置:** 是前两节"验证 > 思考""grounded verification 必须外部建"反复挖出的洞察的**正式落地模式**。CRITIC = 把 Lesson 04 金句 #1 做成产品形态。

---

## 手做记录

### 跑 demo(对比 Self-Refine vs CRITIC)
任务:给主题产 3 条 bullet。

```
Self-Refine(只自评): 4 轮全卡死,输出一字没变
  critique: "first bullet reads wrong"(含糊)→ refine 没动
  且完全漏掉 "Mt Everest is in Europe" 这条错(抓不住自信的 hallucination)
  → did not converge

CRITIC(外部 verifier): 3 轮收敛
  iter1: verifier "'paris is capital of germany' contradicts reference data"(具体)
  iter2: 修好 Paris→France,verifier 又抓 Everest
  iter3: 修好 Everest→Asia → verifier ok → passed
```

**实证:** 同模型自评抓不住自己自信的错(裁判=运动员偏差);换外部 ground truth,critique 立刻具体且独立,真能驱动修正。印证"验证是承重步骤"+"独立性:外部工具 > 自评"。

### Exercises
概念已覆盖。代码未额外实现(scripted demo 的对比已充分说明 CRITIC vs Self-Refine 的核心差异)。
