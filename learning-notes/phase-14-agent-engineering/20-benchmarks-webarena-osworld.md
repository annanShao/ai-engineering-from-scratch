# Lesson 20 · Benchmarks:WebArena 与 OSWorld

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/20-benchmarks-webarena-osworld/` |
| 类型 | Concept · ~60 分钟 |
| 前置 | L19 (SWE-bench/GAIA)、L01 (observation formatter)、L11 (MAP-Elites 按维度拆) |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/20-benchmarks-webarena-osworld/docs/en.md |
| 状态 | ✅ 完成(评测另一半:界面操作 + GUI grounding 新失败维度 + 轨迹效率 + 3/3 体检 + 4 金句) |

---

## 这节课的真定位:评测这对的另一半

L19 测"有明确输出"的任务(patch/答案),L20 测"要跨 20-50 步操作界面"的任务。**人机差距是 Phase 14 目前最大的:人 72-78% vs 最强 agent 发布时 12-14%。** 而且暴露了 SWE-bench 测不到的新失败维度:GUI grounding。

---

## 核心金句

### #1 · 可复现是 benchmark 的隐形要害
> **WebArena 不 flaky,是因为目标 app 自托管、版本钉死。你测的环境必须可复现,否则今天 14% 明天 18% 你不知道是 agent 变强了还是网站改版了。和 L13 "deterministic node 才能 resume" 是同一个工程直觉。**

| | WebArena | OSWorld |
|---|---|---|
| 测什么 | 浏览器长程任务(购物/论坛/GitLab类/CMS) | 整个 OS 键鼠控制(Ubuntu/Win/macOS) |
| observation | web 页面(结构化) | **1920×1080 截图(纯像素)** |
| 评测 | execution-based(订单下了吗/issue 关了吗) | execution-based(状态检查) |
| 发布时最佳 vs 人 | 14.41% vs 78.24% | 12.24% vs 72.36% |

两个都是 execution-based——又是 L05/L19 那条"外部确定性 verifier"主线。

### #2 · GUI Grounding:把失败拆成"知道做什么" vs "能不能指对地方"(全节最重要)
> **一个 agent 可以完美规划出『点保存 → 填表 → 提交』,却因为在截图里把保存按钮坐标指偏 20 像素而全盘失败。这是纯文本 agent 永远测不到的维度——文本 agent 的 action 是 `edit_file(path)`(精确);GUI agent 的 action 是 `click(x,y)`(要先把像素看对)。**

OSWorld 两个新失败模式:
1. **GUI grounding** —— 像素→元素映射,视觉定位问题(不是推理问题)
2. **Operational knowledge** —— "设置藏哪个菜单/哪个快捷键",人类多年攒的操作长尾

**OSWorld-G** 把 grounding 和 planning **拆开测**——这样知道 agent 是"不会想"还是"想对了手抖"。**方法学进步 = 把混在一起的失败拆成可独立测量的维度(呼应 L11 MAP-Elites 按维度拆开)。**

### #3 · 轨迹效率:笨拙藏在步数里不藏在成功率里
> **OSWorld-Human 人工标黄金轨迹,发现顶级 agent 用 1.4-2.7 倍人类步数。成功率告诉你能不能做到,轨迹效率告诉你做得多蠢。90% 成功但 2.7 倍步数 = 生产里 2.7 倍 token/延迟/出错机会。只看成功率和 L19 只看单数字不看分布,是同一个盲区。**

### #4 · 好 benchmark 的最高标准:刷它 = 真的变强(Goodhart 良性版)
> **L19 警告 Goodhart(指标变目标就失效),但 computer-use 是良性例子:因为评测是 execution-based(真把订单下了),刷分 ≈ 真变得更会用电脑。当 evaluator 足够接近真实目标时,Goodhart 诅咒减轻。**

产业闭环:WebArena/OSWorld 定义"什么叫会用电脑" → 成为训练目标 → Claude Computer Use / OpenAI CUA / Gemini Computer Use(L21 产品) → 回来刷分。**benchmark 是靶子,production 模型是射出的答案。**

---

## 关键概念地图

**三个翻车(评测方法学的坑)**:

| 翻车 | 为什么错 |
|---|---|
| Screenshot-only evals 误用(拿 DOM/accessibility API 的 agent 去 OSWorld 测) | 绕过 grounding 真难题,**分数虚高**,没测到核心挑战 |
| 忽略轨迹长度(只报成功率) | 漏掉 1.4-2.7x 步数低效 |
| 自托管 app 过期(更新没重新 curate) | 版本一变和历史分数没法比 |

第一条呼应 L01 observation formatter:**agent 看世界的方式(截图 vs DOM),决定了它在哪个 benchmark 上的分数有意义。**

**扩展**:VisualWebArena(视觉 grounding)、TheAgentCompany(加终端+编码,更像真远程工作)。

**用尺子收口**:execution-based = L05/L19 外部 verifier;GUI grounding = L01 formatter 极端形态(observation 是像素时"看对"成瓶颈);grounding/planning 拆测 = L11 按维度拆;轨迹效率 = L19 分布 > 均值;benchmark→训练→产品 = Goodhart 良性版。

**"L19+L20 教你评测两把标尺:evaluator 可不可信(execution-based > LLM 自评)+ 你测的是不是完整能力(成功率 + 分布 + 轨迹效率 + grounding/planning 拆分)。会造 agent 的人报成功率,会审 agent 的人问『evaluator 跑真环境还是问 LLM?算了轨迹效率吗?grounding 和 planning 分开测了吗?』"**

---

## 体检 · 3/3 ✅

| # | 答 | 点评 |
|---|---|---|
| Q1 | b(视觉定位问题,知道该点什么但指不准) | grounding ≠ 推理,锁死 |
| Q2 | b(补成本/低效盲区) | 没选安全/泛化 |
| Q3 | c(用 DOM 绕过 grounding → 分数虚高) | 抓住"虚高"反直觉方向,同 L19 污染思维:分数不可信常因走捷径而非弱 |

---

## 手做记录

`code/main.py` toy web-agent harness(购物 app 状态机 + 黄金轨迹 + execution-based evaluator + 轨迹效率指标)。未额外跑——概念已通过 grounding 拆分 + 轨迹效率讨论完全消化。

### 钩子
- **L21 Computer Use** 是这些 benchmark 训练出来的**产品**(评测→产品闭环)
- grounding 作为独立能力,可能在多模态/CV 相有更深展开
