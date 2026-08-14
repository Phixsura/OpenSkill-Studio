# OpenSkill Studio — 技能与练习模块设计 (ADR-004)

> 对标 Codecademy / freeCodeCamp / Exercism / LeetCode / Brilliant
>
> Status: **Proposed** | Author: Lyphixia Wang | Date: 2026-08-13
> Depends on: ADR-001 (Bootstrap), ADR-002 (Auth), ADR-003 (Organizations)

---

## 目录

1. [设计目标](#1-设计目标)
2. [行业对标分析](#2-行业对标分析)
3. [领域模型](#3-领域模型)
4. [技能树结构](#4-技能树结构)
5. [数据模型](#5-数据模型)
6. [练习系统](#6-练习系统)
7. [进度追踪](#7-进度追踪)
8. [内容管理](#8-内容管理)
9. [API 端点设计](#9-api-端点设计)
10. [前端设计](#10-前端设计)
11. [搜索与发现](#11-搜索与发现)
12. [测试策略](#12-测试策略)
13. [验收标准](#13-验收标准)
14. [实施计划](#14-实施计划)

---

## 1. 设计目标

### 1.1 核心目标

- **结构化学习路径** — 技能分级、有序组织，learner 知道"下一步学什么"
- **练习驱动** — 每个技能点配套练习，learn by doing
- **进度可视** — 清晰的完成度、掌握度追踪
- **instructor 友好** — 教练可自定义技能树，不限于预设内容
- **AI 评估预留** — 练习结果结构化，为 ADR-006 AI 评估提供数据基础

### 1.2 边界

| 包含 | 不包含 (后续) |
|------|-------------|
| 技能定义 + 分级 | 代码执行沙箱 (需独立基础设施) |
| 练习题 CRUD | AI 自动出题 |
| 多种练习类型 | 实时编程环境 |
| 进度追踪 + 完成状态 | 排行榜 / 竞赛 |
| 技能树可视化 | 社区题库 / UGC |
| 前置技能依赖 | 学习推荐引擎 |

---

## 2. 行业对标分析

### 2.1 技能/课程结构对比

| 维度 | Codecademy | freeCodeCamp | Exercism | LeetCode | Brilliant |
|------|-----------|-------------|---------|---------|-----------|
| 内容层级 | Course → Lesson → Exercise | Certification → Section → Challenge | Track → Concept → Exercise | Topic → Problem | Course → Chapter → Lesson |
| 层级深度 | 3 级 | 3 级 | 3 级 | 2 级 | 3 级 |
| 练习类型 | 填空/选择/代码 | 代码/项目 | 代码 (mentor review) | 代码 | 交互/选择/拖拽 |
| 进度模型 | 百分比 + 勋章 | 星星 + 认证 | 完成/未完成 | AC/WA/TLE | 连续天数 |
| 前置依赖 | 线性 | 线性 + 可跳过 | 有向图 | 标签 (无强依赖) | 线性 |
| 内容归属 | 全局 | 全局 | Track 级 | 全局 | 全局 |
| 自定义 | ❌ | ❌ | ✅ (社区 Track) | ❌ | ❌ |

### 2.2 OpenSkill Studio 的差异化

| 需求 | 对标产品 | OpenSkill Studio 的方案 |
|------|---------|----------------------|
| 内容可定制 | Exercism (社区 Track) | instructor 自建技能树 (per org) |
| 不限编程 | Brilliant (数学/科学) | 多练习类型 (代码/文本/文件/选择) |
| 组织隔离 | 无 | 技能归属组织 (org_id) |
| AI 评估 | 无 | 练习结果结构化，对接 AI 管道 |
| 项目制 | freeCodeCamp (认证项目) | 独立项目模块 (ADR-005) |

---

## 3. 领域模型

### 3.1 内容层级

```
Organization
 └── Skill Category (分类)
      └── Skill (技能)
           ├── metadata (描述、标签、难度、预估时长)
           ├── prerequisites (前置技能)
           ├── Learning Content (学习资料)
           │    ├── Markdown 文本
           │    ├── 外部链接
           │    └── 媒体文件
           └── Exercises (练习)
                ├── Exercise 1 (选择题)
                ├── Exercise 2 (文本回答)
                ├── Exercise 3 (代码提交)
                └── Exercise 4 (文件上传)
```

### 3.2 层级设计理由

| 层级 | 概念 | 示例 | 粒度 |
|------|------|------|------|
| **Skill Category** | 技能分类/领域 | "Prompt Engineering", "Python 基础" | 大分类 |
| **Skill** | 单个可学习的技能点 | "Few-Shot Prompting", "列表推导式" | 30-60 分钟可掌握 |
| **Exercise** | 技能下的练习题 | "改写为 Few-Shot 格式", "用列表推导重写循环" | 5-15 分钟可完成 |

为什么**不**加更多层级 (如 Module / Unit)?
- OpenSkill Studio 面向 AI 创作者，不是通用 LMS
- 技能粒度较细，3 层足够
- 更深的层级增加 instructor 维护负担
- 如需更复杂结构，可在 Category 层嵌套（未来扩展）

---

## 4. 技能树结构

### 4.1 前置依赖 (DAG)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Markdown    │────▶│  Prompt      │────▶│  Few-Shot    │
│  基础        │     │  基础        │     │  Prompting   │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                            ┌─────────────────────┤
                            ▼                     ▼
                     ┌──────────────┐     ┌──────────────┐
                     │  Chain-of-   │     │  Prompt      │
                     │  Thought     │     │  Templates   │
                     └──────────────┘     └──────────────┘
```

- **有向无环图 (DAG)**，不是树 — 允许多个前置技能
- 通过 `skill_prerequisites` 关联表实现
- 前端渲染为可交互的技能树地图
- 未解锁的技能显示为灰色 (前置技能未完成)

### 4.2 难度等级

```python
class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"         # 入门
    INTERMEDIATE = "intermediate" # 进阶
    ADVANCED = "advanced"         # 高级
    EXPERT = "expert"             # 专家
```

---

## 5. 数据模型

### 5.1 ER 图

```
┌──────────────────────────────────────────────────────┐
│                   skill_categories                    │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ org_id          ULID           FK → organizations.id   │
│ name            VARCHAR(100)   NOT NULL                │
│ slug            VARCHAR(100)   NOT NULL                │
│ description     TEXT           NULL                    │
│ icon            VARCHAR(50)    NULL (emoji or icon id) │
│ sort_order      INT            DEFAULT 0               │
│ status          content_status DEFAULT 'draft'         │
│ created_by      ULID           FK → users.id           │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ UNIQUE (org_id, slug)                                 │
└───────┬──────────────────────────────────────────────┘
        │ 1:N
        ▼
┌──────────────────────────────────────────────────────┐
│                       skills                          │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ org_id          ULID           FK → organizations.id   │
│ category_id     ULID           FK → skill_categories   │
│ name            VARCHAR(200)   NOT NULL                │
│ slug            VARCHAR(200)   NOT NULL                │
│ description     TEXT           NOT NULL                │
│ learning_content TEXT          NULL (Markdown)         │
│ difficulty      difficulty     DEFAULT 'beginner'      │
│ estimated_minutes INT          NULL                    │
│ tags            TEXT[]         DEFAULT '{}'            │
│ sort_order      INT            DEFAULT 0               │
│ status          content_status DEFAULT 'draft'         │
│ published_at    TIMESTAMPTZ    NULL                    │
│ created_by      ULID           FK → users.id           │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ UNIQUE (org_id, slug)                                 │
│ INDEX (org_id, category_id, sort_order)               │
│ INDEX (org_id, status)                                │
│ GIN INDEX (tags)            -- 标签数组搜索             │
└───────┬──────────────────────────────────────────────┘
        │
        │ M:N (self-referencing)
        ▼
┌──────────────────────────────────────────────────────┐
│                 skill_prerequisites                   │
├──────────────────────────────────────────────────────┤
│ skill_id        ULID           FK → skills.id         │
│ prerequisite_id ULID           FK → skills.id         │
├──────────────────────────────────────────────────────┤
│ PK (skill_id, prerequisite_id)                        │
│ CHECK (skill_id != prerequisite_id)                   │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                      exercises                        │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ org_id          ULID           FK → organizations.id   │
│ skill_id        ULID           FK → skills.id          │
│ title           VARCHAR(200)   NOT NULL                │
│ description     TEXT           NOT NULL (Markdown)     │
│ type            exercise_type  NOT NULL                │
│ config          JSONB          NOT NULL                │
│ sort_order      INT            DEFAULT 0               │
│ max_score       INT            DEFAULT 100             │
│ status          content_status DEFAULT 'draft'         │
│ created_by      ULID           FK → users.id           │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ INDEX (skill_id, sort_order)                          │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                  exercise_attempts                    │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ org_id          ULID           FK → organizations.id   │
│ exercise_id     ULID           FK → exercises.id       │
│ user_id         ULID           FK → users.id           │
│ answer          JSONB          NOT NULL                │
│ score           INT            NULL                    │
│ is_correct      BOOLEAN        NULL                    │
│ feedback        TEXT           NULL                    │
│ graded_by       grading_method NULL                    │
│ graded_at       TIMESTAMPTZ    NULL                    │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ INDEX (exercise_id, user_id, created_at DESC)         │
│ INDEX (user_id, org_id)      -- 用户在组织内的全部尝试  │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                  skill_progress                       │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ org_id          ULID           FK → organizations.id   │
│ skill_id        ULID           FK → skills.id          │
│ user_id         ULID           FK → users.id           │
│ status          progress_status DEFAULT 'not_started'  │
│ exercises_total INT            DEFAULT 0               │
│ exercises_done  INT            DEFAULT 0               │
│ best_score      INT            NULL                    │
│ started_at      TIMESTAMPTZ    NULL                    │
│ completed_at    TIMESTAMPTZ    NULL                    │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ UNIQUE (skill_id, user_id)                            │
│ INDEX (user_id, org_id, status)                       │
└──────────────────────────────────────────────────────┘
```

### 5.2 枚举类型

```sql
CREATE TYPE content_status AS ENUM ('draft', 'published', 'archived');
CREATE TYPE difficulty AS ENUM ('beginner', 'intermediate', 'advanced', 'expert');
CREATE TYPE exercise_type AS ENUM (
    'multiple_choice',     -- 单选/多选
    'text_answer',         -- 自由文本回答
    'code_submission',     -- 代码提交 (AI/手动评分)
    'file_upload'          -- 文件上传 (手动评分)
);
CREATE TYPE progress_status AS ENUM ('not_started', 'in_progress', 'completed');
CREATE TYPE grading_method AS ENUM ('auto', 'manual', 'ai');
```

---

## 6. 练习系统

### 6.1 练习类型与 config 结构

#### 单选/多选题

```json
{
  "type": "multiple_choice",
  "config": {
    "question": "以下哪种 prompting 技术要求在提示中提供示例？",
    "options": [
      { "id": "a", "text": "Zero-Shot Prompting" },
      { "id": "b", "text": "Few-Shot Prompting" },
      { "id": "c", "text": "Chain-of-Thought" },
      { "id": "d", "text": "Role Prompting" }
    ],
    "correct": ["b"],
    "multiple": false,
    "explanation": "Few-Shot Prompting 通过在提示中提供多个示例来引导模型..."
  }
}
```

#### 文本回答 (AI/手动评分)

```json
{
  "type": "text_answer",
  "config": {
    "question": "请解释 Chain-of-Thought prompting 的核心原理，并给出一个实际应用场景。",
    "min_length": 50,
    "max_length": 2000,
    "rubric": [
      { "criterion": "核心原理解释", "max_score": 40, "description": "准确描述 CoT 的逐步推理过程" },
      { "criterion": "实际应用场景", "max_score": 30, "description": "给出具体、合理的应用场景" },
      { "criterion": "表达质量", "max_score": 30, "description": "逻辑清晰、表达准确" }
    ],
    "sample_answer": "Chain-of-Thought prompting 是一种通过引导 LLM 逐步推理来解决复杂问题的技术..."
  }
}
```

#### 代码提交

```json
{
  "type": "code_submission",
  "config": {
    "instruction": "编写一个 Python 函数，使用 OpenAI API 实现 Few-Shot 分类器。",
    "language": "python",
    "starter_code": "def classify(text: str, examples: list[dict]) -> str:\n    \"\"\"使用 Few-Shot 方法分类文本.\"\"\"\n    pass",
    "test_cases": [
      { "input": "classify('I love this!', [...])", "expected": "positive" },
      { "input": "classify('Terrible.', [...])", "expected": "negative" }
    ],
    "rubric": [
      { "criterion": "功能正确", "max_score": 50 },
      { "criterion": "代码质量", "max_score": 30 },
      { "criterion": "错误处理", "max_score": 20 }
    ]
  }
}
```

#### 文件上传

```json
{
  "type": "file_upload",
  "config": {
    "instruction": "使用 Stable Diffusion 生成一张包含以下元素的图片：...",
    "accepted_types": [".png", ".jpg", ".jpeg", ".webp"],
    "max_size_mb": 10,
    "max_files": 3,
    "rubric": [
      { "criterion": "主题符合度", "max_score": 40 },
      { "criterion": "技术执行", "max_score": 30 },
      { "criterion": "创意表达", "max_score": 30 }
    ]
  }
}
```

### 6.2 评分流程

```
提交答案 (exercise_attempts)
    │
    ├── multiple_choice → 自动评分 (graded_by = 'auto')
    │     比对 answer vs config.correct
    │     即时返回结果 + 解释
    │
    ├── text_answer → AI 评分 (graded_by = 'ai', ADR-006)
    │     异步发送到评估管道
    │     按 rubric 逐项评分
    │     返回分数 + 反馈
    │
    ├── code_submission → AI + 自动评分
    │     Phase 1: 手动评分
    │     Phase 2+: 测试用例自动验证 + AI 代码审查
    │
    └── file_upload → 手动评分 (graded_by = 'manual')
          instructor 人工评分
          AI 辅助评分 (ADR-006, Phase 3+)
```

### 6.3 提交答案 API

```python
@router.post(
    "/orgs/{org_id}/exercises/{exercise_id}/attempts",
    response_model=DataResponse[AttemptResponse],
    status_code=201,
)
async def submit_attempt(
    org_id: str,
    exercise_id: str,
    body: SubmitAttemptRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_org_db),
):
    service = ExerciseService(db)
    attempt = await service.submit_attempt(
        exercise_id=exercise_id,
        user_id=user.id,
        answer=body.answer,
    )
    return DataResponse(data=AttemptResponse.from_orm(attempt))
```

---

## 7. 进度追踪

### 7.1 进度计算

```python
async def update_skill_progress(
    self, skill_id: str, user_id: str, org_id: str
) -> SkillProgress:
    """练习完成后更新技能进度."""
    # 统计该技能下的练习总数和已完成数
    exercises = await self._get_skill_exercises(skill_id)
    completed = await self._count_completed_exercises(skill_id, user_id)

    progress = await self._get_or_create_progress(skill_id, user_id, org_id)
    progress.exercises_total = len(exercises)
    progress.exercises_done = completed

    if completed == 0:
        progress.status = ProgressStatus.NOT_STARTED
    elif completed >= len(exercises):
        progress.status = ProgressStatus.COMPLETED
        progress.completed_at = func.now()
    else:
        progress.status = ProgressStatus.IN_PROGRESS
        if progress.started_at is None:
            progress.started_at = func.now()

    return progress
```

### 7.2 技能解锁逻辑

```python
async def is_skill_unlocked(
    self, skill_id: str, user_id: str
) -> bool:
    """检查用户是否已解锁某技能 (前置技能全部完成)."""
    prerequisites = await self._get_prerequisites(skill_id)

    if not prerequisites:
        return True  # 无前置要求，直接解锁

    for prereq_id in prerequisites:
        progress = await self._get_progress(prereq_id, user_id)
        if progress is None or progress.status != ProgressStatus.COMPLETED:
            return False

    return True
```

### 7.3 进度统计 API

```json
// GET /api/v1/orgs/:org_id/progress/me — 200
{
  "data": {
    "skills_total": 12,
    "skills_completed": 5,
    "skills_in_progress": 2,
    "exercises_total": 48,
    "exercises_completed": 22,
    "completion_percentage": 45.8,
    "current_streak_days": 3,
    "categories": [
      {
        "id": "01JK...",
        "name": "Prompt Engineering",
        "skills_total": 6,
        "skills_completed": 3,
        "completion_percentage": 50.0
      }
    ]
  }
}
```

---

## 8. 内容管理

### 8.1 内容状态机

```
draft ──── publish ────▶ published
  ▲                        │
  │         unpublish      │
  └────────────────────────┘
                           │
            archive        │
                           ▼
                        archived
```

- **draft**: 仅 instructor 可见，可编辑
- **published**: 学生可见，可做练习
- **archived**: 学生不可见，历史数据保留

### 8.2 Markdown 内容渲染

```
instructor 编辑:
  使用 Markdown 编写 learning_content
  支持:
    - 标准 Markdown
    - 代码块 (语法高亮)
    - 表格
    - 图片 (上传到 MinIO)
    - 嵌入视频 (YouTube/Bilibili URL)
    - 数学公式 (KaTeX, Phase 2+)
    - Mermaid 图表 (Phase 2+)

前端渲染:
  react-markdown + rehype-highlight + remark-gfm
```

### 8.3 版本控制 (Phase 3+)

```
Phase 1: 直接编辑 (覆盖写)
Phase 3+: 内容版本快照
  - 每次 publish 创建版本快照
  - 学生进度关联到特定版本
  - instructor 可回退到历史版本
```

---

## 9. API 端点设计

### 9.1 完整端点列表

```
Skill Categories (/api/v1/orgs/:org_id/categories)
├── GET    /                      列出分类
├── POST   /                      创建分类 (instructor+)
├── GET    /:category_id          获取分类详情
├── PUT    /:category_id          更新分类
├── DELETE /:category_id          删除分类
└── PUT    /reorder               调整排序

Skills (/api/v1/orgs/:org_id/skills)
├── GET    /                      列出技能 (支持筛选: category, difficulty, status, tag)
├── POST   /                      创建技能 (instructor+)
├── GET    /:skill_id             获取技能详情 (含 learning_content)
├── PUT    /:skill_id             更新技能
├── DELETE /:skill_id             删除技能 (软删除)
├── POST   /:skill_id/publish     发布技能
├── POST   /:skill_id/unpublish   取消发布
├── GET    /:skill_id/tree        获取技能依赖树
└── PUT    /:skill_id/prerequisites  设置前置技能

Exercises (/api/v1/orgs/:org_id/skills/:skill_id/exercises)
├── GET    /                      列出练习
├── POST   /                      创建练习 (instructor+)
├── GET    /:exercise_id          获取练习详情
├── PUT    /:exercise_id          更新练习
├── DELETE /:exercise_id          删除练习
└── PUT    /reorder               调整排序

Attempts (/api/v1/orgs/:org_id/exercises/:exercise_id/attempts)
├── POST   /                      提交答案 (student+)
├── GET    /                      获取我的尝试历史
└── GET    /:attempt_id           获取尝试详情 (含反馈)

Progress (/api/v1/orgs/:org_id/progress)
├── GET    /me                    获取我的整体进度
├── GET    /me/skills             获取每个技能的进度
├── GET    /me/skills/:skill_id   获取特定技能的详细进度
└── GET    /students/:user_id     获取学员进度 (instructor+)

Grading (/api/v1/orgs/:org_id/grading)
├── GET    /pending               获取待评分提交 (instructor+)
└── POST   /attempts/:attempt_id  评分 (instructor+)
```

---

## 10. 前端设计

### 10.1 页面结构

```
/orgs/:slug/skills
  ├── 技能树概览 (技能地图 / 列表视图切换)
  ├── 进度摘要卡片
  └── 分类筛选 + 难度筛选

/orgs/:slug/skills/:skill_slug
  ├── 技能详情
  │   ├── 学习内容 (Markdown 渲染)
  │   ├── 练习列表 (带完成状态)
  │   └── 前置技能链接
  └── 侧边栏
      ├── 难度 / 预估时长
      ├── 完成进度
      └── 前置/后续技能

/orgs/:slug/skills/:skill_slug/exercises/:exercise_id
  ├── 练习详情 + 题目
  ├── 答题区域 (按类型渲染不同 UI)
  ├── 提交按钮
  └── 历史提交 + 反馈
```

### 10.2 技能树可视化

```typescript
// 使用 React Flow 渲染 DAG 技能树
// 每个节点:
// - 锁定 (灰色, 前置未完成)
// - 未开始 (白色)
// - 进行中 (蓝色, 带进度环)
// - 已完成 (绿色, 带 ✓)

interface SkillNode {
  id: string;
  name: string;
  difficulty: DifficultyLevel;
  status: "locked" | "not_started" | "in_progress" | "completed";
  progress: number; // 0-100
  prerequisites: string[];
}
```

### 10.3 练习组件

```tsx
// 按 exercise.type 渲染不同组件
function ExerciseRenderer({ exercise }: { exercise: Exercise }) {
  switch (exercise.type) {
    case "multiple_choice":
      return <MultipleChoiceExercise config={exercise.config} />;
    case "text_answer":
      return <TextAnswerExercise config={exercise.config} />;
    case "code_submission":
      return <CodeSubmissionExercise config={exercise.config} />;
    case "file_upload":
      return <FileUploadExercise config={exercise.config} />;
  }
}
```

---

## 11. 搜索与发现

### 11.1 搜索策略

```
Phase 1: PostgreSQL ILIKE + GIN 索引
  - 按名称/描述搜索技能
  - 按标签筛选
  - 按难度/状态筛选

Phase 2+: PostgreSQL Full-Text Search (tsvector)
  - 中文分词 (zhparser 扩展)
  - 搜索学习内容全文
  - 搜索练习题目

Phase 3+: 独立搜索引擎 (Meilisearch)
  - 模糊搜索
  - 搜索建议
  - 多面搜索 (faceted)
```

### 11.2 筛选参数

```
GET /api/v1/orgs/:org_id/skills?
  category=01JK...           # 按分类
  difficulty=beginner         # 按难度
  status=published            # 按状态
  tag=prompt-engineering      # 按标签
  q=few-shot                  # 搜索关键词
  sort=sort_order             # 排序: sort_order, name, difficulty, created_at
  page=1&per_page=20          # 分页
```

---

## 12. 测试策略

### 12.1 关键测试用例

```python
class TestSkillTree:
    async def test_create_skill_with_prerequisites(self, client, instructor_headers, org):
        # 创建前置技能
        prereq = await create_skill(client, org.id, "Basics")
        # 创建依赖技能
        skill = await create_skill(client, org.id, "Advanced",
                                   prerequisites=[prereq["id"]])
        assert len(skill["prerequisites"]) == 1

    async def test_circular_dependency_rejected(self, client, instructor_headers, org):
        a = await create_skill(client, org.id, "A")
        b = await create_skill(client, org.id, "B", prerequisites=[a["id"]])
        # A → B → A 应该被拒绝
        response = await set_prerequisites(client, a["id"], [b["id"]])
        assert response.status_code == 422

    async def test_locked_skill_cannot_be_practiced(self, client, student_headers, org):
        prereq = await create_skill(client, org.id, "Prereq", status="published")
        skill = await create_skill(client, org.id, "Advanced",
                                   prerequisites=[prereq["id"]], status="published")
        exercise = await create_exercise(client, skill["id"])
        # 前置未完成 → 不能提交
        response = await submit_attempt(client, exercise["id"], ...)
        assert response.status_code == 403


class TestExerciseAttempts:
    async def test_multiple_choice_auto_graded(self, client, student_headers, org):
        exercise = await create_mc_exercise(client, org.id, correct=["b"])
        attempt = await submit_attempt(client, exercise["id"], answer=["b"])
        assert attempt["is_correct"] is True
        assert attempt["graded_by"] == "auto"

    async def test_multiple_attempts_allowed(self, client, student_headers, org):
        exercise = await create_mc_exercise(client, org.id)
        await submit_attempt(client, exercise["id"], answer=["a"])
        await submit_attempt(client, exercise["id"], answer=["b"])
        history = await get_attempts(client, exercise["id"])
        assert len(history) == 2

    async def test_progress_updates_after_completion(self, client, student_headers, org):
        skill = await create_skill_with_exercises(client, org.id, n_exercises=3)
        # 完成全部练习
        for ex in skill["exercises"]:
            await submit_correct_attempt(client, ex["id"])
        progress = await get_skill_progress(client, skill["id"])
        assert progress["status"] == "completed"
```

---

## 13. 验收标准

| # | 验收项 | 方案章节 |
|---|--------|---------|
| 1 | instructor 可创建技能分类 | §4 |
| 2 | instructor 可创建技能并设置前置依赖 | §4.1, §5 |
| 3 | 技能依赖形成 DAG (拒绝循环依赖) | §4.1 |
| 4 | 支持 4 种练习类型 | §6.1 |
| 5 | 选择题自动评分 | §6.2 |
| 6 | 学生可提交练习答案 | §6.3 |
| 7 | 进度自动追踪并更新 | §7.1 |
| 8 | 未解锁技能不可练习 | §7.2 |
| 9 | 技能内容支持 Markdown 渲染 | §8.2 |
| 10 | 技能有 draft/published/archived 状态 | §8.1 |
| 11 | 技能树可视化展示 | §10.2 |
| 12 | instructor 可手动评分 | §6.2 |
| 13 | 全部端点有组织级 RLS 隔离 | §5 (org_id) |

---

## 14. 实施计划

### Phase 1: 数据模型 + 技能 CRUD (~3h)

1. SkillCategory / Skill / Exercise 模型 + migration
2. skill_prerequisites 关联表 + DAG 环检测
3. 技能 CRUD 端点 (含分类)
4. 练习 CRUD 端点

### Phase 2: 练习系统 (~2.5h)

5. 选择题自动评分引擎
6. 提交答案 API + exercise_attempts
7. 手动评分 API (instructor)
8. 进度追踪 (skill_progress 自动计算)

### Phase 3: 前端 (~3h)

9. 技能列表页 + 筛选/搜索
10. 技能详情页 (Markdown 渲染 + 练习列表)
11. 练习页面 (4 种类型组件)
12. 技能树可视化 (React Flow)
13. 进度仪表板

### Phase 4: 内容管理 (~1.5h)

14. 状态机 (draft → published → archived)
15. Markdown 编辑器 (instructor)
16. 图片上传 (MinIO 集成)
17. 技能排序/重排序

---

## 新增依赖

### 前端

```json
{
  "dependencies": {
    "@xyflow/react": "^12",           // 技能树 DAG 可视化
    "react-markdown": "^9",           // Markdown 渲染
    "rehype-highlight": "^7",         // 代码高亮
    "remark-gfm": "^4"               // GitHub Flavored Markdown
  }
}
```

---

## ADR 元数据

- **Status**: Proposed
- **Decision**: 3-level skill hierarchy (Category → Skill → Exercise), DAG prerequisites, 4 exercise types, auto-grading for MCQ, per-org skill trees
- **Context**: AI creator training platform needs structured learning paths. Must balance flexibility (instructor-customizable) with structure (enforced prerequisites, progress tracking).
- **Consequences**: DAG cycle detection needed for prerequisites. JSONB `config` for exercise types provides flexibility but requires careful validation. AI grading deferred to ADR-006.

---

*ADR-004 v1 — 技能与练习模块完整设计。*
