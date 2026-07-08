# Lesson 31 · Agent Workbench:为什么强模型仍然会失败(实战相开篇)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/31-agent-workbench-why-models-fail/` |
| 类型 | Concept(实战相宣言)· ~60 分钟 |
| 前置 | Phase 14 前 30 节全部 |
| en.md | https://github.com/annanShao/ai-engineering-from-scratch/blob/claude/wonderful-hawking-1247L/phases/14-agent-engineering/31-agent-workbench-why-models-fail/docs/en.md |
| 状态 | ✅ 完成(七面/八原语框架 + workbench vs harness 追问 + subagent=worker 解码器追问 + 免体检直接过) |

---

## 这节课的真定位:实战相(L31-L42)的宣言 + Phase 14 前 30 节的归位点

核心论点让前 30 节全部咔哒归位:**大多数 agent 失败不是 model bug,是 workbench bug——模型周围缺了把"一次性生成"变成"可靠可续工程"的部件。**

---

## 核心金句

### #1 · 模型没搞错 Python,它搞错了"工作"
> **Most agent failure stories are workbench failures wearing prompt-engineering clothes. 你前 30 节踩的每个坑(假成功/scope creep/context loss/handoff drift)没有一个是"模型不够聪明",全是"模型周围的工作台缺了一块"。答案不是等 GPT-6,是把工作台搭对。**

### #2 · 七个 Surface(实战相目录,一节搭一个面)
| Surface | 承载 | 缺了会 | 对应节 |
|---|---|---|---|
| Instructions | 启动规则/禁止动作/完成定义 | agent 猜什么叫交付 | L33 |
| State | 当前任务/动过文件/blocker/下一步 | 每 session 从零重启 | L34 |
| Scope | 允许/禁止文件/验收标准 | 编辑漏进无关代码 | L36 |
| Feedback | 真实命令输出进循环 | 400 上宣布成功 | L37 |
| Verification | 测试/lint/smoke/scope 检查 | "看着挺好"进 main | L38 |
| Review | 换角色第二遍 | builder 给自己批作业 | L39 |
| Handoff | 改了什么/为什么/还剩什么 | 下 session 重新发现一切 | L40 |

**核心机制**:The loop closes on the state file, not on chat history. Chat is volatile. The repo is the system of record.**agent 记忆不该活在对话窗口(会丢),该活在 repo(持久)——L07/L13/L17 收敛成:把状态写进文件,让 repo 当不会失忆的大脑。**

**workbench 独立于模型**:换模型保留这些面,但换掉这些面保不住可靠性。(框架给 runtime,workbench 给 agent 在 runtime 里干活的地方,两个都要。)

### #3 · ⭐ 七面底下是八个分布式系统原语(Phase 14 顶点)
> **每个流行 harness pattern 都是 agent 社区重新发现了一个分布式系统早有名字的原语,给它起了新名字。术语在变,工程不变。你学的不是 agent 新知识,是分布式系统老原语穿了 agent 新衣。**

| 原语 | 对 agent | 你之前学的 |
|---|---|---|
| Function | tool 调用/规则检查/验证/模型调用 | L06 |
| Worker | builder/reviewer/verifier/MCP/subagent | L14 actor/L17 subagent |
| Trigger | 循环 tick/HTTP/队列/cron/文件变化/hook | L17 hook/L22 barge-in |
| Runtime | 决定什么在哪跑+超时+资源 | L13 LangGraph runtime |
| HTTP/RPC | tool-call 协议/MCP/模型 API | L16 handoff/MCP |
| Queue | trigger-worker 间持久缓冲(背压/重试/幂等) | L14 DLQ/L29 queue |
| Session persistence | 扛崩溃/重启/换模型的状态 | L07/L13/L17 + repo 本身 |
| Authorization policy | 谁能用什么 scope 调什么 | L27 PVE/scope |

**翻译表**:Ralph Loop=requeue+persistence;PEV=三 worker 用 queue 通信;harness-compute separation=control/data plane(早几十年);subagent=worker;sandbox=compute plane;hook=trigger;memory=session persistence;MCP=worker over RPC。

### #4 · 收据:harness > model 有硬数字(专治"等更强模型")
> **Terminal Bench 2.0:同模型只改 harness,从榜外冲到第 5。Vercel:删 80% tool,成功率 80%→100%。Harvey:光 harness 优化准确率翻倍多。88% 企业 agent 项目到不了生产,失败聚在 runtime 不是 reasoning。**

**Vercel 删 80% tool 反涨到 100% = 实战相广告牌:瓶颈不在能力不够,在工作台太乱。减法比加法更能提升 agent(呼应 L12 复杂度是债务)。大家都在等更强模型,而钱在工作台里。**

### #5 · vendor 都在写 UX 描述,没人写系统本身
> **所有 harness 博客写的是已存在系统的 UX 描述,这个实战相写系统本身。搭对 harness,七个 surface 从八原语自动长出来;搭错了,再多 AGENTS.md 润色也补不上缺的 queue。别人教你配置工作台,这里教你从分布式原语建出来。**

---

## 两个追问(用户提问)

### 追问 A · workbench = harness 吗?
**不完全等同,是同一系统的两个视角:**
- **Workbench** = agent-facing UX 层 = 七个面(从 agent 往下看"我在什么环境干活")
- **Harness** = 工程实质 = 八原语正确接线(扒开工程看"用什么搭的")
- 类比:workbench=汽车仪表盘/驾驶舱;harness=发动机/传动/线路。**搭对 harness,workbench 自动长出来。**

三层:**Framework(runtime 边界,L13-L18)< Harness(八原语接对)< Workbench(agent 感受到的七面)**。同 L24 "trace(录像)vs checkpoint(存档)"一样,是一件事的两副面孔。日常口语里两词常混用,这节故意拆开是为了骂"人人写 UX(workbench)、没人建系统(harness)"。

### 追问 B · subagent 本质 = 开新 worker?(用户在用解码器)
**对。** subagent=worker 原语(=L14 actor=L17 subagent isolation,三者归一)。

**磨精确**:worker 本质不是"进程 or 线程",是三个属性——① 拥有自己 state(不共享内存;subagent=自己的 context window)② 有生命周期(spawn→跑→销毁)③ 只靠消息/RPC 通信(主 agent 只拿最终返回)。**进程/线程/容器/新 context window 都只是同一 worker 原语的实现变体。** Claude Code subagent 常连新进程都不是,就是新 context window + 独立调用,照样是 worker。→ 解释了 L17"subagent 省 context":worker 的"拥有自己 state"=独立 context=主 agent budget 不被烧。

**可复用解码器(L31 核心技能)**:① 撕掉 agent 标签→跨时间/进程/机器的计算里哪一块?② 落到 8 原语之一 ③ 实现细节(进程/线程/文件/DB)只是变体不是本质。

**worker vs function 别混**:function=无状态一次调用(用完即走);worker=长活+拥有 function+生命周期+自己 state。一个 worker 里调很多 function(subagent 是 worker,内部每个 tool 是 function)。

---

## 关键概念地图

```
七个面(agent-facing UX)  ←落在→  八个原语(工程实质)
"术语在变,工程不变。harness 博客写 UX 描述,这个实战相写系统本身。"
```

agent loop 本身 = 一个 worker:消费事件(user 消息/tool 结果/timer)→ 调 function(模型+tool)→ 写记录(state/feedback)→ 发 trigger(verify/review/handoff)。和 job processor 同形。

---

## 手做记录

概念宣言课,未跑代码。核心通过 workbench-vs-harness + subagent=worker 两个解码追问完全消化,已能独立运用"撕标签→落原语"解码器。

### 钩子
- **L32 Minimal Agent Workbench**:开始真正动手把八原语接成最小 workbench
- L33-L40:一节搭一个 surface
- L41 真 repo / L42 capstone
