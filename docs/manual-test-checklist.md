# 手动测试清单 — Issue #16 Cohort + Brief + Multimodal Eval

> 前置条件：`make infra-up && make dev-api && make dev-web`
> API: http://localhost:8000 · FE: http://localhost:3000

---

## 第一步：注册 + 创建组织

1. 打开 http://localhost:3000/register
2. 注册管理员账号（如 admin@test.com / TestPass123!）
3. 登录后点左侧 "Organizations" → "New Organization"
4. 创建组织（如 "AI 视觉培训中心"）
5. ✅ 预期：进入组织概览，看到 Overview 标签页高亮
6. ✅ 预期：顶部标签栏有 **Cohorts** 和 **Briefs** 两个新标签

---

## 第二步：注册讲师 + 学员

7. 另开隐身窗口，注册讲师账号（instructor@test.com）
8. 再注册学员 A（alice@test.com）和学员 B（bob@test.com）
9. 回管理员窗口 → Members 标签 → 添加讲师（role: instructor）和两个学员（role: student）
10. ✅ 预期：Members 页面显示 4 人（含管理员自己）

---

## 第三步：创建 Cohort

11. 点 **Cohorts** 标签
12. ✅ 预期：显示 "No cohorts yet" 空状态
13. 点 "+ New Cohort"
14. 输入名称 "AI 视觉商务 — 2026 秋季"，描述随意
15. 点 "Create Cohort"
16. ✅ 预期：出现卡片，状态 "draft"，0 members
17. 点击卡片进入详情
18. ✅ 预期：看到统计卡片（Learners: 0, Skills: 0, Projects: 0, Overdue: 0）
19. ✅ 预期：子标签栏有 Overview / Members / Skills / Projects / Progress / My Dashboard

---

## 第四步：激活 Cohort + 注册成员

20. （通过 API 或修改状态）将 cohort 状态改为 active
    - 可在详情页 URL 末尾加 `/members` 直接跳转
21. 点 **Members** 子标签
22. 在 User ID 输入框粘贴讲师的用户 ID，选 Instructor，点 Add
23. ✅ 预期：讲师出现在列表中，角色显示 "instructor"
24. 同样添加 Alice（role: learner）
25. ✅ 预期：2 行，一个 instructor 一个 learner，各有 Remove 按钮
26. **不要**添加 Bob（测试可见性隔离需要）

---

## 第五步：分配技能到 Cohort

27. 先在 Skills 标签创建一个技能（如 "Prompt 工程"），添加一道 MCQ 习题，发布
28. 回 Cohort → Skills 子标签
29. ✅ 预期：看到 "Assigned Skills" 区（空）和 "Available Skills" 区（Prompt 工程）
30. 点 "Assign"
31. ✅ 预期：技能移到已分配区，显示 Remove 按钮

---

## 第六步：分配项目到 Cohort

32. 先在 Projects 标签创建一个项目，添加 rubric，发布
33. 回 Cohort → Projects 子标签
34. 从下拉选择项目
35. 可选填 deadline override 和 max submissions
36. 点 "Assign to Cohort"
37. ✅ 预期：项目出现在已分配列表，显示 override 信息

---

## 第七步：讲师进度仪表板

38. 回 Cohort Overview 页
39. ✅ 预期：Learners: 1, Skills: 1, Projects: 1
40. ✅ 预期：Project Progress 表格显示项目名，Not Started: 1
41. 点 **Progress** 子标签
42. ✅ 预期：看到 Alice 的名字，可点击
43. 点击 Alice
44. ✅ 预期：看到 Skills 区（Prompt 工程, not started）和 Projects 区（项目名, not started）

---

## 第八步：创建客户简报

45. 点顶部 **Briefs** 标签
46. ✅ 预期："No client briefs" 空状态
47. 点 "+ New Brief"
48. 填入：标题 "Acme Q4 产品推广"，客户 "Acme Corp"，目标 "为 Q4 新品上市创建主视觉"
49. 点 "Create Brief"
50. ✅ 预期：列表显示简报卡片，Acme Corp，draft 状态

---

## 第九步：简报详情 + 转换为项目

51. 点击简报卡片进入详情
52. ✅ 预期：看到标题、客户名、目标文本、Draft 标签、"Convert to Project →" 按钮
53. 点 "Convert to Project →"
54. ✅ 预期：展开表单，有 Rubric criterion 输入框、Max score、Deadline
55. 输入 criterion "Visual Quality"，点 "Create Project"
56. ✅ 预期：跳转到新建的项目详情页，项目类型 ai_visual

---

## 第十步：可见性隔离测试

57. 用 Alice 账号登录（她在 cohort 里）
58. 进组织 → Projects
59. ✅ 预期：能看到分配给 cohort 的项目
60. ✅ 预期：如果有 cohort 过滤下拉，能看到 cohort 名

61. 用 Bob 账号登录（他不在 cohort 里）
62. 进组织 → Projects
63. ✅ 预期：**看不到** cohort 专属项目（只能看到 org-wide 项目）

---

## 第十一步：学员 My Dashboard

64. 用 Alice 登录 → Cohorts → 点击 cohort → My Dashboard 子标签
65. ✅ 预期：看到 cohort 名称、分配的技能列表、分配的项目列表
66. ✅ 预期：技能和项目显示状态（not started / in progress 等）

---

## 第十二步：学员提交作业

67. 用 Alice 登录 → Projects → 点项目 → Submit
68. 填入文本 deliverable，提交
69. ✅ 预期：提交状态变为 "submitted"

70. 回讲师账号 → Cohort Overview
71. ✅ 预期：Project Progress 表格的 Submitted 列变为 1

---

## 第十三步：评估页面

72. 讲师 → AI Evaluation 标签
73. ✅ 预期：页面正常加载
74. ✅ 预期：如果有评估记录，类型列显示 emoji 图标（📝/🖼️/🎬/✏️/💼）

---

## 第十四步：RBAC 检查

75. 用 Alice（学生）访问 Briefs 标签
76. ✅ 预期：看不到简报内容（403 或空页面，不是崩溃）

77. 用 Bob（不在 cohort）访问 cohort 的 members 页
78. ✅ 预期：看不到成员数据

---

## 发现问题？

在每一步记下：
- 步骤编号
- 实际看到的结果（截图更好）
- 与预期的差异

告诉我编号，我立刻修。
