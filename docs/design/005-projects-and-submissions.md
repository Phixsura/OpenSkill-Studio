# OpenSkill Studio — 项目与提交模块设计 (ADR-005)

> 对标 freeCodeCamp (Certification Projects) / GitHub Classroom / Gradescope / Google Classroom
>
> Status: **Proposed** | Author: Lyphixia Wang | Date: 2026-08-13
> Depends on: ADR-001 (Bootstrap), ADR-002 (Auth), ADR-003 (Organizations), ADR-004 (Skills)

---

## 目录

1. [设计目标](#1-设计目标)
2. [行业对标分析](#2-行业对标分析)
3. [领域模型](#3-领域模型)
4. [数据模型](#4-数据模型)
5. [项目生命周期](#5-项目生命周期)
6. [提交流程](#6-提交流程)
7. [文件上传与存储](#7-文件上传与存储)
8. [评审流程](#8-评审流程)
9. [截止日期与延期](#9-截止日期与延期)
10. [API 端点设计](#10-api-端点设计)
11. [前端设计](#11-前端设计)
12. [通知系统预留](#12-通知系统预留)
13. [测试策略](#13-测试策略)
14. [验收标准](#14-验收标准)
15. [实施计划](#15-实施计划)

---

## 1. 设计目标

### 1.1 核心目标

- **项目制交付** — 学员通过完成真实项目来证明技能掌握度
- **结构化提交** — 明确的提交要求、格式、截止日期
- **多轮评审** — 支持 instructor 反馈 → 学员修改 → 再评审的迭代循环
- **文件管理** — 安全的文件上传/下载，支持多种文件类型
- **AI 评估衔接** — 提交物结构化存储，为 ADR-006 AI 管道提供数据

### 1.2 边界

| 包含 | 不包含 (后续) |
|------|-------------|
| 项目 CRUD + 发布 | 项目模板市场 |
| 提交物上传 (多文件) | Git 仓库集成 |
| 评审流程 (评分 + 反馈) | 同学互评 (Peer Review) |
| 截止日期 + 延期管理 | 自动截止提醒通知 |
| 文件存储 (MinIO/S3) | 在线预览 (PDF/Video) |
| 关联技能要求 | 项目协作/团队项目 |
| 提交版本历史 | 实时协作编辑 |

---

## 2. 行业对标分析

### 2.1 项目/作业系统对比

| 维度 | freeCodeCamp | GitHub Classroom | Gradescope | Google Classroom |
|------|-------------|-----------------|-----------|-----------------|
| 项目概念 | Certification Project | Assignment | Assignment | Assignment |
| 提交方式 | URL (Codepen/Replit) | Git push | PDF/代码上传 | 文件/链接/文档 |
| 评分方式 | 通过/不通过 (测试) | 自动测试 + 手动 | AI + 手动 | 手动 |
| 多轮修改 | ✅ (重新提交) | ✅ (re-push) | ✅ (重新提交) | ✅ (退回修改) |
| 截止日期 | ❌ | ✅ | ✅ (迟交标记) | ✅ |
| 文件类型 | URL only | 代码仓库 | PDF/图片/代码 | 任意文件 |
| 评审反馈 | 自动 | 代码 review | 批注 + 分数 | 评论 + 分数 |
| 与技能关联 | ✅ (认证要求) | ❌ | ❌ | ❌ |

### 2.2 OpenSkill Studio 的差异化

- **技能关联** — 项目明确对应需要的技能 (ADR-004)，完成项目 = 证明技能
- **多类型提交** — 不只是代码，支持文档/设计/视频等 AI 创作者的多样产出
- **AI 评估** — Gradescope 式的 AI 辅助评分，但面向 AI 创作物而非传统作业
- **作品集整合** — 优秀提交直接进入作品集 (ADR-007)

---

## 3. 领域模型

### 3.1 核心概念

```
Organization
 └── Project (项目/作业)
      ├── metadata (描述、要求、截止日期、分值)
      ├── required_skills (关联技能)
      ├── deliverables (交付物定义)
      │    ├── Deliverable 1: "项目 README" (markdown)
      │    ├── Deliverable 2: "源代码" (file, .py/.ts)
      │    └── Deliverable 3: "演示视频" (file, .mp4)
      │
      └── Submissions (学员提交)
           └── Submission
                ├── files (上传的文件)
                ├── text_content (文本内容)
                ├── links (外部链接)
                ├── reviews (评审记录)
                │    ├── Review 1: "需要修改..." (revision_requested)
                │    └── Review 2: "很好！" (approved, score=92)
                └── version (提交版本)
```

### 3.2 项目 vs 练习的区别

| 维度 | 练习 (ADR-004) | 项目 (ADR-005) |
|------|---------------|---------------|
| 粒度 | 5-15 分钟 | 数小时到数天 |
| 评分 | 自动 (选择题) / 简单评分 | 多维度 rubric 评审 |
| 提交物 | 单一答案 | 多个交付物 (文件/文本/链接) |
| 迭代 | 通常一次提交 | 多轮修改 |
| 技能关联 | 属于某个技能 | 综合多个技能 |
| 目的 | 学习巩固 | 能力证明 |

---

## 4. 数据模型

### 4.1 ER 图

```
┌──────────────────────────────────────────────────────┐
│                      projects                         │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ org_id          ULID           FK → organizations.id   │
│ title           VARCHAR(200)   NOT NULL                │
│ slug            VARCHAR(200)   NOT NULL                │
│ description     TEXT           NOT NULL (Markdown)     │
│ instructions    TEXT           NOT NULL (Markdown)     │
│ difficulty      difficulty     DEFAULT 'intermediate'  │
│ max_score       INT            DEFAULT 100             │
│ rubric          JSONB          NOT NULL                │
│ deadline        TIMESTAMPTZ    NULL                    │
│ late_deadline   TIMESTAMPTZ    NULL (迟交截止)          │
│ late_penalty_pct INT           DEFAULT 0 (迟交扣分%)   │
│ max_submissions INT            DEFAULT 0 (0=无限)      │
│ status          content_status DEFAULT 'draft'         │
│ published_at    TIMESTAMPTZ    NULL                    │
│ created_by      ULID           FK → users.id           │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ UNIQUE (org_id, slug)                                 │
│ INDEX (org_id, status, deadline)                      │
└───────┬──────────────────────────────────────────────┘
        │
        │ M:N
        ▼
┌──────────────────────────────────────────────────────┐
│                  project_skills                       │
├──────────────────────────────────────────────────────┤
│ project_id      ULID           FK → projects.id       │
│ skill_id        ULID           FK → skills.id          │
│ PK (project_id, skill_id)                             │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                  project_deliverables                 │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ project_id      ULID           FK → projects.id       │
│ name            VARCHAR(200)   NOT NULL                │
│ description     TEXT           NULL                    │
│ type            deliverable_type NOT NULL              │
│ required        BOOLEAN        DEFAULT true            │
│ config          JSONB          DEFAULT '{}'            │
│ sort_order      INT            DEFAULT 0               │
├──────────────────────────────────────────────────────┤
│ INDEX (project_id, sort_order)                        │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                    submissions                        │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ org_id          ULID           FK → organizations.id   │
│ project_id      ULID           FK → projects.id       │
│ user_id         ULID           FK → users.id           │
│ version         INT            NOT NULL DEFAULT 1      │
│ status          submission_status DEFAULT 'draft'      │
│ submitted_at    TIMESTAMPTZ    NULL                    │
│ is_late         BOOLEAN        DEFAULT false           │
│ final_score     INT            NULL                    │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ INDEX (project_id, user_id, version DESC)             │
│ INDEX (org_id, status)                                │
└───────┬──────────────────────────────────────────────┘
        │ 1:N
        ▼
┌──────────────────────────────────────────────────────┐
│                  submission_items                     │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ submission_id   ULID           FK → submissions.id    │
│ deliverable_id  ULID           FK → project_deliverables │
│ type            item_type      NOT NULL                │
│ content         TEXT           NULL (文本内容/链接)     │
│ file_key        VARCHAR(500)   NULL (S3 key)          │
│ file_name       VARCHAR(255)   NULL                    │
│ file_size       BIGINT         NULL (bytes)            │
│ mime_type       VARCHAR(100)   NULL                    │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ INDEX (submission_id)                                 │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                  submission_reviews                   │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ submission_id   ULID           FK → submissions.id    │
│ reviewer_id     ULID           FK → users.id          │
│ reviewer_type   reviewer_type  NOT NULL                │
│ status          review_status  NOT NULL                │
│ score           INT            NULL                    │
│ score_breakdown JSONB          NULL (按 rubric 项评分)  │
│ feedback        TEXT           NULL (Markdown)         │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ INDEX (submission_id, created_at DESC)                │
└──────────────────────────────────────────────────────┘
```

### 4.2 枚举类型

```sql
CREATE TYPE deliverable_type AS ENUM ('file', 'text', 'link', 'markdown');
CREATE TYPE item_type AS ENUM ('file', 'text', 'link');
CREATE TYPE submission_status AS ENUM (
    'draft',              -- 草稿 (可编辑)
    'submitted',          -- 已提交 (等待评审)
    'revision_requested', -- 需要修改
    'approved',           -- 通过
    'rejected'            -- 不通过
);
CREATE TYPE review_status AS ENUM (
    'approved',           -- 通过
    'revision_requested', -- 需要修改
    'rejected'            -- 不通过
);
CREATE TYPE reviewer_type AS ENUM ('instructor', 'ai');
```

### 4.3 Rubric (评分标准) 结构

```json
{
  "rubric": [
    {
      "criterion": "功能完整性",
      "max_score": 30,
      "description": "全部功能需求是否完整实现",
      "levels": [
        { "score": 30, "label": "优秀", "description": "全部功能完整实现，无遗漏" },
        { "score": 20, "label": "良好", "description": "核心功能实现，少量遗漏" },
        { "score": 10, "label": "及格", "description": "部分功能实现" },
        { "score": 0,  "label": "不及格", "description": "功能严重缺失" }
      ]
    },
    {
      "criterion": "代码质量",
      "max_score": 25,
      "description": "代码结构、命名、可读性",
      "levels": [...]
    },
    {
      "criterion": "创新性",
      "max_score": 25,
      "description": "解决方案的创意和独特性",
      "levels": [...]
    },
    {
      "criterion": "文档质量",
      "max_score": 20,
      "description": "README、注释、说明文档",
      "levels": [...]
    }
  ]
}
```

---

## 5. 项目生命周期

### 5.1 状态机

```
draft ──── publish ────▶ published ──── archive ────▶ archived
  ▲                        │                            │
  │         unpublish      │                            │
  └────────────────────────┘        unarchive           │
                                 ◀──────────────────────┘
```

### 5.2 截止日期逻辑

```
                     deadline          late_deadline
──────────────────────│─────────────────│──────────────
  正常提交区间          │   迟交区间       │   不可提交
                      │ (-N% 扣分)      │
```

```python
def get_submission_timing(project: Project) -> str:
    now = datetime.now(timezone.utc)
    if project.deadline is None:
        return "on_time"  # 无截止日期
    if now <= project.deadline:
        return "on_time"
    if project.late_deadline and now <= project.late_deadline:
        return "late"
    return "closed"
```

---

## 6. 提交流程

### 6.1 提交状态机

```
                    ┌──────────────────────────────────────────┐
                    │                                          │
                    ▼                                          │
draft ──── submit ────▶ submitted ──── review ────▶ approved   │
                           │                                   │
                           │         ┌───── revision_requested │
                           │         │            │            │
                           │         │            ▼            │
                           │         │     draft (new version) │
                           │         │            │            │
                           │         └────────────┘            │
                           │                                   │
                           └──── review ────▶ rejected         │
```

### 6.2 多版本提交

```python
async def create_submission(
    self, project_id: str, user_id: str, org_id: str,
) -> Submission:
    """创建新提交 (草稿)."""
    # 检查提交次数限制
    project = await self._get_project(project_id)
    existing_count = await self._count_user_submissions(project_id, user_id)

    if project.max_submissions > 0 and existing_count >= project.max_submissions:
        raise MaxSubmissionsReachedError(project.max_submissions)

    # 版本号递增
    version = existing_count + 1

    submission = Submission(
        org_id=org_id,
        project_id=project_id,
        user_id=user_id,
        version=version,
        status=SubmissionStatus.DRAFT,
    )
    self.db.add(submission)
    await self.db.flush()
    return submission


async def submit(self, submission_id: str, user_id: str) -> Submission:
    """将草稿提交为正式提交."""
    submission = await self._get_submission(submission_id)

    if submission.user_id != user_id:
        raise PermissionDeniedError()
    if submission.status != SubmissionStatus.DRAFT:
        raise InvalidStateError("Only drafts can be submitted")

    # 检查必填交付物
    await self._validate_required_deliverables(submission)

    # 检查截止日期
    project = await self._get_project(submission.project_id)
    timing = get_submission_timing(project)
    if timing == "closed":
        raise DeadlinePassedError()

    submission.status = SubmissionStatus.SUBMITTED
    submission.submitted_at = func.now()
    submission.is_late = (timing == "late")

    await self.db.flush()
    return submission
```

---

## 7. 文件上传与存储

### 7.1 上传流程

```
Client                  FastAPI                  MinIO (S3)
  │                       │                        │
  │ POST /upload          │                        │
  │ (multipart/form-data) │                        │
  │ ─────────────────────▶│                        │
  │                       │                        │
  │                       │  1. 验证文件类型/大小    │
  │                       │  2. 生成 S3 key         │
  │                       │  3. 上传到 MinIO        │
  │                       │  ───────────────────── ▶│
  │                       │                        │
  │                       │  4. 返回 file metadata  │
  │  { file_key,          │                        │
  │    file_name,         │                        │
  │    file_size,         │                        │
  │    mime_type }        │                        │
  │ ◀─────────────────────│                        │
```

### 7.2 Presigned URL (大文件)

```
Phase 1: 直接上传 (< 50MB) — FastAPI 代理上传到 MinIO
Phase 2+: Presigned URL (> 50MB) — 客户端直传 MinIO

GET /api/v1/uploads/presign
  → { upload_url: "https://minio:9000/openskill/...", fields: {...} }

PUT upload_url (客户端直传)
  → 完成后 POST /api/v1/uploads/confirm { file_key }
```

### 7.3 S3 Key 规范

```
orgs/{org_id}/submissions/{submission_id}/{deliverable_id}/{ulid}_{filename}
```

示例:
```
orgs/01JK.../submissions/01JK.../01JK.../01JKXYZ_README.md
orgs/01JK.../submissions/01JK.../01JK.../01JKXYZ_demo.mp4
```

### 7.4 文件安全

| 措施 | 实现 |
|------|------|
| 文件类型白名单 | 按 deliverable config 中的 accepted_types |
| 文件大小限制 | 全局 50MB，按 deliverable 可配置 |
| 恶意文件扫描 | Phase 2+: ClamAV 异步扫描 |
| 访问控制 | Presigned URL (时效 1h) 下载，不直接暴露 S3 |
| 文件名清理 | 去除路径分隔符、控制字符 |

### 7.5 文件上传 API

```python
@router.post(
    "/orgs/{org_id}/submissions/{submission_id}/files",
    response_model=DataResponse[FileResponse],
    status_code=201,
)
async def upload_file(
    org_id: str,
    submission_id: str,
    deliverable_id: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_org_db),
):
    service = SubmissionService(db)
    result = await service.upload_file(
        submission_id=submission_id,
        deliverable_id=deliverable_id,
        file=file,
        user_id=user.id,
    )
    return DataResponse(data=FileResponse.from_orm(result))


@router.get("/orgs/{org_id}/submissions/{submission_id}/files/{file_id}/download")
async def download_file(
    org_id: str,
    submission_id: str,
    file_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_org_db),
):
    """生成 presigned download URL (1h 有效)."""
    service = SubmissionService(db)
    url = await service.get_download_url(file_id, user.id)
    return {"download_url": url}
```

---

## 8. 评审流程

### 8.1 评审操作

```python
@router.post(
    "/orgs/{org_id}/submissions/{submission_id}/reviews",
    response_model=DataResponse[ReviewResponse],
    status_code=201,
)
async def create_review(
    org_id: str,
    submission_id: str,
    body: CreateReviewRequest,
    user: User = Depends(require_org_role(OrgRole.INSTRUCTOR)),
    db: AsyncSession = Depends(get_org_db),
):
    service = ReviewService(db)
    review = await service.create_review(
        submission_id=submission_id,
        reviewer_id=user.id,
        status=body.status,
        score=body.score,
        score_breakdown=body.score_breakdown,
        feedback=body.feedback,
    )
    return DataResponse(data=ReviewResponse.from_orm(review))
```

### 8.2 评审结果处理

```python
async def create_review(self, ...) -> SubmissionReview:
    review = SubmissionReview(...)
    self.db.add(review)

    # 更新提交状态
    submission = await self._get_submission(submission_id)

    if status == ReviewStatus.APPROVED:
        submission.status = SubmissionStatus.APPROVED
        submission.final_score = self._calculate_final_score(score, submission.is_late, project)
        # 触发技能进度更新 (关联技能标记为完成)
        await self._update_skill_progress(submission)
    elif status == ReviewStatus.REVISION_REQUESTED:
        submission.status = SubmissionStatus.REVISION_REQUESTED
    elif status == ReviewStatus.REJECTED:
        submission.status = SubmissionStatus.REJECTED
        submission.final_score = score

    await self.db.flush()
    return review


def _calculate_final_score(self, score: int, is_late: bool, project: Project) -> int:
    """计算最终分数 (含迟交扣分)."""
    if is_late and project.late_penalty_pct > 0:
        penalty = score * project.late_penalty_pct / 100
        return max(0, round(score - penalty))
    return score
```

### 8.3 instructor 评审仪表板

```json
// GET /api/v1/orgs/:org_id/reviews/pending — 200
{
  "data": [
    {
      "submission_id": "01JK...",
      "project_title": "AI Chatbot 项目",
      "student_name": "Alice Wang",
      "submitted_at": "2026-08-12T15:30:00Z",
      "version": 2,
      "is_late": false,
      "file_count": 3,
      "previous_reviews": 1
    }
  ],
  "meta": { "total": 8, "page": 1, "per_page": 20, "has_more": false }
}
```

---

## 9. 截止日期与延期

### 9.1 延期机制

```python
# instructor 可以为特定学生延期
@router.post("/orgs/{org_id}/projects/{project_id}/extensions")
async def grant_extension(
    org_id: str,
    project_id: str,
    body: ExtensionRequest,  # { user_id, new_deadline, reason }
    user: User = Depends(require_org_role(OrgRole.INSTRUCTOR)),
    db: AsyncSession = Depends(get_org_db),
):
    ...
```

```
┌──────────────────────────────────────────────────────┐
│                 submission_extensions                  │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ project_id      ULID           FK → projects.id       │
│ user_id         ULID           FK → users.id           │
│ original_deadline TIMESTAMPTZ  NOT NULL                │
│ extended_deadline TIMESTAMPTZ  NOT NULL                │
│ reason          TEXT           NULL                    │
│ granted_by      ULID           FK → users.id           │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ UNIQUE (project_id, user_id)                          │
└──────────────────────────────────────────────────────┘
```

### 9.2 截止日期检查优先级

```python
async def get_effective_deadline(project_id: str, user_id: str) -> datetime | None:
    """获取对特定用户生效的截止日期 (个人延期 > 迟交截止 > 常规截止)."""
    extension = await get_extension(project_id, user_id)
    if extension:
        return extension.extended_deadline

    project = await get_project(project_id)
    return project.late_deadline or project.deadline
```

---

## 10. API 端点设计

### 10.1 完整端点列表

```
Projects (/api/v1/orgs/:org_id/projects)
├── GET    /                         列出项目 (含筛选/排序)
├── POST   /                         创建项目 (instructor+)
├── GET    /:project_id              获取项目详情
├── PUT    /:project_id              更新项目
├── DELETE /:project_id              删除项目 (软删除)
├── POST   /:project_id/publish      发布项目
├── POST   /:project_id/unpublish    取消发布
├── PUT    /:project_id/skills       设置关联技能
└── POST   /:project_id/extensions   授予截止日期延期

Deliverables (/api/v1/orgs/:org_id/projects/:project_id/deliverables)
├── GET    /                         列出交付物定义
├── POST   /                         创建交付物
├── PUT    /:deliverable_id          更新交付物
└── DELETE /:deliverable_id          删除交付物

Submissions (/api/v1/orgs/:org_id/projects/:project_id/submissions)
├── GET    /                         列出提交 (instructor: 全部, student: 自己)
├── POST   /                         创建提交 (草稿)
├── GET    /:submission_id           获取提交详情
├── PUT    /:submission_id           更新提交 (仅草稿状态)
├── POST   /:submission_id/submit    正式提交
└── DELETE /:submission_id           删除草稿

Files (/api/v1/orgs/:org_id/submissions/:submission_id/files)
├── POST   /                         上传文件
├── GET    /:file_id/download        获取下载链接
└── DELETE /:file_id                 删除文件 (仅草稿状态)

Reviews (/api/v1/orgs/:org_id/submissions/:submission_id/reviews)
├── GET    /                         获取评审历史
└── POST   /                         创建评审 (instructor+)

Review Dashboard (/api/v1/orgs/:org_id/reviews)
└── GET    /pending                  待评审列表 (instructor+)
```

---

## 11. 前端设计

### 11.1 页面结构

```
/orgs/:slug/projects
  ├── 项目列表 (卡片/列表视图)
  ├── 截止日期排序 (即将截止 → 已截止)
  └── 状态筛选 (全部/进行中/已截止)

/orgs/:slug/projects/:project_slug
  ├── 项目说明 (Markdown 渲染)
  ├── 交付物清单 (带完成标记)
  ├── 截止日期倒计时
  ├── 我的提交历史
  └── 评审反馈 (时间线)

/orgs/:slug/projects/:project_slug/submit
  ├── 交付物上传区域 (按 deliverable 分区)
  ├── 文件上传 (拖拽 + 选择)
  ├── 文本/链接输入
  └── 提交按钮

/orgs/:slug/reviews (instructor)
  ├── 待评审队列
  ├── 评审详情 (文件预览 + rubric 评分)
  └── 反馈编辑器
```

### 11.2 提交页面组件

```tsx
function SubmissionForm({ project, deliverables }: Props) {
  return (
    <form>
      {deliverables.map((d) => (
        <DeliverableInput key={d.id} deliverable={d} />
      ))}
      <SubmitButton />
    </form>
  );
}

function DeliverableInput({ deliverable }: { deliverable: Deliverable }) {
  switch (deliverable.type) {
    case "file":
      return <FileUploader config={deliverable.config} />;
    case "text":
      return <TextInput />;
    case "link":
      return <LinkInput />;
    case "markdown":
      return <MarkdownEditor />;
  }
}
```

---

## 12. 通知系统预留

### 12.1 事件列表 (Phase 3+)

| 事件 | 接收者 | 渠道 |
|------|--------|------|
| 新提交 | instructor | 站内 + 邮件 |
| 评审完成 | student | 站内 + 邮件 |
| 需要修改 | student | 站内 + 邮件 |
| 截止日期临近 (24h) | student (未提交) | 站内 + 邮件 |
| 迟交提交 | instructor | 站内 |

### 12.2 事件模型预留

```python
# 提交时发送事件 (Phase 3+: Redis PubSub / 专用事件表)
async def _emit_event(self, event_type: str, payload: dict):
    """Phase 1: 仅日志. Phase 3+: 推送到事件系统."""
    import structlog
    log = structlog.get_logger()
    log.info("event", type=event_type, **payload)
```

---

## 13. 测试策略

### 13.1 关键测试用例

```python
class TestSubmissionFlow:
    async def test_full_submission_lifecycle(self):
        # 创建项目 → 创建草稿 → 上传文件 → 提交 → 评审通过
        ...

    async def test_cannot_submit_after_deadline(self):
        project = await create_project(deadline=past_time)
        submission = await create_draft(project.id)
        response = await submit(submission.id)
        assert response.status_code == 422
        assert "DEADLINE_PASSED" in response.json()["error"]["code"]

    async def test_late_submission_marked(self):
        project = await create_project(
            deadline=past_time,
            late_deadline=future_time,
            late_penalty_pct=20
        )
        submission = await submit_draft(project.id)
        assert submission["is_late"] is True

    async def test_revision_allows_resubmit(self):
        sub = await submit_and_review(status="revision_requested")
        new_sub = await create_draft(sub["project_id"])
        assert new_sub["version"] == 2

    async def test_max_submissions_enforced(self):
        project = await create_project(max_submissions=2)
        await submit_draft(project.id)  # v1
        await submit_draft(project.id)  # v2
        response = await create_draft(project.id)  # v3 → rejected
        assert response.status_code == 422


class TestFileUpload:
    async def test_upload_file(self):
        response = await upload(submission_id, file=b"content", filename="test.py")
        assert response.status_code == 201
        assert response.json()["data"]["mime_type"] == "text/x-python"

    async def test_reject_oversized_file(self):
        large_file = b"x" * (51 * 1024 * 1024)  # 51 MB
        response = await upload(submission_id, file=large_file)
        assert response.status_code == 413

    async def test_reject_disallowed_type(self):
        response = await upload(submission_id, file=b"content", filename="test.exe")
        assert response.status_code == 422


class TestReview:
    async def test_approve_updates_score(self):
        review = await create_review(submission_id, status="approved", score=85)
        submission = await get_submission(submission_id)
        assert submission["status"] == "approved"
        assert submission["final_score"] == 85

    async def test_late_penalty_applied(self):
        # 项目 late_penalty_pct = 20, 评分 100
        review = await create_review(late_submission_id, status="approved", score=100)
        submission = await get_submission(late_submission_id)
        assert submission["final_score"] == 80  # 100 - 20%

    async def test_student_cannot_review(self):
        response = await create_review_as(student_token, submission_id, ...)
        assert response.status_code == 403
```

---

## 14. 验收标准

| # | 验收项 | 方案章节 |
|---|--------|---------|
| 1 | instructor 可创建项目并定义交付物 | §4, §5 |
| 2 | 项目可关联技能要求 | §4.1 |
| 3 | 项目有评分标准 (rubric) | §4.3 |
| 4 | 学员可创建草稿并上传文件 | §6, §7 |
| 5 | 文件安全上传到 MinIO/S3 | §7 |
| 6 | 学员可正式提交 | §6.2 |
| 7 | 截止日期后不可提交 | §9 |
| 8 | 迟交标记并扣分 | §9 |
| 9 | instructor 可评审 (评分+反馈) | §8 |
| 10 | 评审通过后更新技能进度 | §8.2 |
| 11 | 需要修改时学员可重新提交 | §6.1 |
| 12 | 提交版本历史可追溯 | §6.2 |
| 13 | instructor 可授予个人延期 | §9.1 |
| 14 | 全部端点有组织级隔离 | §4 (org_id) |

---

## 15. 实施计划

### Phase 1: 数据模型 + 项目 CRUD (~2.5h)

1. Project / Deliverable / Submission / SubmissionItem / Review 模型 + migration
2. 项目 CRUD 端点
3. 交付物管理端点
4. Rubric 验证

### Phase 2: 提交流程 (~3h)

5. 提交创建 + 状态机
6. 文件上传 (MinIO aioboto3)
7. 文件下载 (presigned URL)
8. 截止日期检查 + 迟交逻辑
9. 多版本提交

### Phase 3: 评审 (~2h)

10. 评审 CRUD
11. 评分计算 (含迟交扣分)
12. 技能进度联动
13. 评审仪表板 API

### Phase 4: 前端 (~3h)

14. 项目列表 + 详情页
15. 提交表单 (文件上传组件)
16. 评审页面 (rubric 评分 + 反馈)
17. 提交历史时间线

---

## 新增依赖

### 后端

```toml
[project]
dependencies = [
    # aioboto3 已在 ADR-001 中引入
    "python-multipart>=0.0.18",  # FastAPI 文件上传
]
```

### 前端

```json
{
  "dependencies": {
    "react-dropzone": "^14"      // 文件拖拽上传
  }
}
```

---

## ADR 元数据

- **Status**: Proposed
- **Decision**: Multi-deliverable projects with rubric-based review, multi-version submissions, MinIO file storage with presigned URLs, late penalty system
- **Context**: Education platform needs structured project assignments. Must support diverse file types (code, design, video) for AI creators. Review workflow must support iteration (revision → resubmit).
- **Consequences**: File upload adds MinIO dependency (already in ADR-001). Multi-version submissions increase storage. Review workflow adds complexity but essential for education. AI evaluation (ADR-006) will hook into the same submission_reviews table.

---

*ADR-005 v1 — 项目与提交模块完整设计。*
