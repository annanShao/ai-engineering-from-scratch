# Lesson 41 · Workbench for Real Repos(before/after 实证)

## 课程坐标

| 项 | 值 |
|---|---|
| 路径 | `phases/14-agent-engineering/41-workbench-for-real-repos/` |
| 类型 | Build(实战)· 端到端跑一遍 |
| 前置 | L32-L40(七个 surface 全部搭齐) |
| lab | `learning-notes/workbench-lab/before-after-report.md` + 真实完成的 toy-repo |
| 状态 | ✅ 完成(任务 T1 通过工作台端到端做完,before/after 五指标实测)|

---

## 这节课的真定位:把说服力从"demo"变成"before/after 报告"

toy demo 说服不了人。工作台的价值是"真实感的任务在真实感的 repo 上,以更少失败/回退落地,还留下下个 session 能用的包"。同一任务过两条流水线,产出能递给怀疑者的 before/after。

---

## 实测(真的跑了,不是模拟)

任务:给 `create_user` 加输入验证(拒空 username/负 age/坏 email),测试证明,不碰测试文件。

| 五指标 | prompt-only | workbench-guided(实测) |
|---|---|---|
| tests_actually_run | 声称,不可验证 | **yes**——feedback runner 捕获 exit 0(L37) |
| acceptance_met | 也许 | **yes**——5 passed exit 0(之前 3 failed) |
| files_outside_scope | 大概率 creep | **0**——gate 只见 user_service.py(L36/L38) |
| handoff_quality | "有进展" | **完整包**含 next_action(L40) |
| reviewer_total | 无 | **10/10 pass**(L39) |

**流水线 trace**:init READY(L35)→ 只改 scope 允许的 user_service.py → feedback runner 验收 exit 0 succeeded=True(L37)→ gate passed 0 findings(L38)→ reviewer 10/10(L39)→ 反事实:prompt-only 若也改了 forbidden 测试文件 → gate passed=False 3 block findings(工作台拒绝,prompt-only 会 ship)。

**核心**:同模型同任务,差别不是智能,是模型周围的 surface——scope 拒 creep,feedback runner 让"tests passed"可验证,gate 按 git 真相拒,reviewer 抓质量,handoff 留起点。**Harness, not model。** 印证 L31 的收据(Vercel 删 80% tool 反涨到 100%)。

---

## 手做记录

- 把 toy-repo 测试从 xfail 占位改成真 FAIL_TO_PASS(before=3 failed,after=5 passed)
- 通过工作台实现 `user_service.py` 验证(只碰允许文件)
- 端到端跑完整流水线,产出 `before-after-report.md`

### 绑 TPP
这就是你可以对你司 skeptic 做的实验:同一个任务,一条裸 prompt-only,一条挂上你搭的 surface,量五指标。数字自己说话。
