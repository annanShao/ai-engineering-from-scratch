# Lesson 33 · Instructions as Executable Constraints

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/33-instructions-as-executable-constraints/` |
| 类型 | Build(实战)· 设计+评审模式 |
| 前置 | L32(最小 workbench)、L27(结构硬/模型软)、L26(不信自述)、L30(每 guardrail 配 eval) |
| lab | `learning-notes/workbench-lab/docs/agent-rules.md` + `rule_checker.py` |
| 状态 | ✅ 完成(规则声明+检测器搭出并跑通 + "软约束 vs 硬强制"分层追问 + 归类/check/severity 评审) |

---

## 这节课的真定位:把祈使句变成可执行约束

指令 operational(可执行)才有力,aspirational(祈使)就是废话。"要仔细""充分测试"三天后 agent 照样违反,因为它不知道线在哪。修法:规则搬进 `docs/agent-rules.md`,每条 name+category+`check`(指向 `rule_checker.py` 函数)。**规则=可执行检查=L31 的 function 原语。**

---

## 核心金句

### #1 · ⭐ 软约束 vs 硬强制的分层(用户自己撞出的题眼)
> **用户问:"agent-rules 不也是软约束吗?该不该在 write tool 里约束?"—— 说对了一半:agent-rules.md 单独看就是软的(跟 L27"结构能保证边界不被伪造,但不能保证模型尊重边界"同一件事)。但规则文件和 write-tool 约束不是二选一,是两层。**

| 层 | 是什么 | 软/硬 |
|---|---|---|
| agent-rules.md | 规则**声明**(人可读/可 diff/可 review 的契约) | 软 |
| write tool 拒写禁止路径 | **预防性强制**(preventive,L36) | 硬 |
| rule_checker.py / verification gate | **检测性强制**(detective,事后抓,L38) | 硬 |
| reviewer | 复审(L39) | 中 |

**为什么还要软的规则文件(3 理由)**:
1. **单一真相源**——一条规则多个强制点实现,别把策略散落三处代码(会漂移,L14)。
2. **不是所有规则能预防性强制**——光谱:可预防(Forbidden→tool authz 拦得住)↔ 只能检测(DoD→跑完才知道,只能事后判)。规则文件要同时承载两种。
3. **可读可 review**——审计员读一个 markdown 就知道 agent 被什么策略约束。

**"agent-rules.md 是策略声明(软),write-tool authz + verification gate 是策略强制(硬)。不是二选一,是声明一次、预防+检测各强制一次——跟 L27 defense-in-depth 一样:声明+预防+检测+复审四层。用户直觉'文件软'对,解法'挪进 write tool'也对,只是它是规则文件的硬化落地点之一,不是替代。"** 课程编排:L33 搭声明+检测,L36 scope contract 搭 write-tool 预防(用户提前一节想到了 L36)。

### #2 · 五个类别(不符合的通常想拆成两条)
Startup(干活前必须为真,查一次)/ Forbidden(绝不能发生,查每次)/ Definition of done(什么证明完成)/ Uncertainty(不确定怎么办)/ Approval(什么需人批)。

### #3 · check 读 git 真相,不读 agent 自述(L26 落地)
> **check 的"改动文件"从 `git diff` 来,不从 `agent_state.touched_files` 来——捣乱的 agent 可能改了测试但不记进 state。check 必须读外部真相(git),不信 agent 自述。这是 L26"成功由外部状态验证,不由 agent 宣布"在这里落地。**

### #4 · 生产 pattern
- **Severity 写时标注**(block/warn/info):runtime 只在 block 拒。大多数团队早期高估、deadline 下偷偷调弱——写时校准强制提前。block 的 override 签进 `overrides.jsonl`(L38)。
- **Rule expiry 当 forcing function**:每条带 `expires_at`(默认 90 天),60 天零违规就告警,季度 review 决定留/弱化/删。Cloudflare 数据(13 万次 review):有 expiry 的规则集 <30 条/repo,没有的涨到 80+ 且大多不触发。
- **Progressive disclosure**:router<50 行只放指针;可达性测试(任何规则从 router 2 跳可达);新鲜度测试(router 短到 reviewer 每 PR 重读)。broken link 本身是 startup-check 违规。

---

## 设计评审(模式①)

### 决策 1 · 归类:2 对 1 错
| 规则 | 用户归 | 评审 |
|---|---|---|
| T1 完成定义 | DoD | ✅ |
| 不许改测试 | Forbidden | ✅ |
| scope | **Startup** | ❌ 应是 **Forbidden**——scope=贯穿全程的"不许写 allowed 之外",不是干活前一次性前提。**Startup 查一次,Forbidden 查每次。** |

### 决策 2 · check 逻辑:方向对,两个升级
用户"check 改写文件是否 test_xxx"——对,但:① 别硬编码 `test_`,对照规则声明的 globs(通用 `check_forbidden_paths` 服务所有路径规则,加规则不加 check)② **改动文件从 git diff 来,不从 state.touched_files(L26 不信自述)**。

### 决策 3 · severity(reviewer 定)
不许改测试→**block**(改测试=作弊,硬拒);scope→**block**(越界=L26 scope creep);DoD→**block on 标记完成**(没过验收不许 done)。

---

## 绑 TPP
你司 middleware(`SkillsSyncMiddleware`/`AUIRuntimeMiddleware`)= runtime 级 guardrail = 这套规则的**强制层**;而 human-readable rule set 是它们实现的**声明层**。两者关系正是本节 #1:声明 vs 强制。你司缺不缺一份可 review 的规则声明(而不是把策略散在 middleware 代码里)?值得回去看。

---

## 手做记录(真 artifact,已 push)

新增 lab 文件:
- `docs/agent-rules.md`——3 条规则声明(no-edit-tests / stay-in-scope / t1-tests-green)
- `rule_checker.py`——parser + 3 个 check + git 真相源 + 2 场景 demo
- `AGENTS.md`——router 加 Enforcement 段(detective 现在/preventive L36)

**跑通**:Scenario A(只改 user_service.py)全 PASS;Scenario B(偷改测试)→ 2 条 block 违规从 git 真相抓到 → runtime 拒绝。**软规则被硬化成"从外部真相抓违规的检测器"。**

### 钩子
- L36 scope contract → write-tool 预防性拦截(用户已预见)
- L38 verification gate → block override 审计 + fails-closed
- L39 reviewer → 消费 rule_report.json
