# OpenSkill Studio — 组织与多租户设计 (ADR-003)

> 对标 Plane.so / Cal.com / Twenty CRM / Formbricks / Supabase
>
> Status: **Proposed** | Author: Lyphixia Wang | Date: 2026-08-13
> Depends on: ADR-001 (Bootstrap), ADR-002 (Auth & Users)

---

## 目录

1. [设计目标](#1-设计目标)
2. [行业对标分析](#2-行业对标分析)
3. [多租户架构决策](#3-多租户架构决策)
4. [数据模型](#4-数据模型)
5. [组织生命周期](#5-组织生命周期)
6. [成员管理](#6-成员管理)
7. [邀请流程](#7-邀请流程)
8. [PostgreSQL RLS 行级安全](#8-postgresql-rls-行级安全)
9. [API 端点设计](#9-api-端点设计)
10. [前端组织上下文](#10-前端组织上下文)
11. [跨组织数据隔离](#11-跨组织数据隔离)
12. [计费与配额预留](#12-计费与配额预留)
13. [测试策略](#13-测试策略)
14. [验收标准](#14-验收标准)
15. [实施计划](#15-实施计划)

---

## 1. 设计目标

### 1.1 核心目标

- **数据隔离** — 组织 A 的学生绝不能看到组织 B 的数据
- **灵活角色** — 同一用户在不同组织可以有不同角色（在 A 是 instructor，在 B 是 student）
- **低摩擦加入** — 支持邀请链接、邮件邀请、批量导入
- **教育场景适配** — 组织 ≈ 培训机构/班级/团队，不是企业 workspace

### 1.2 边界

| 包含 | 不包含 (后续) |
|------|-------------|
| 组织 CRUD | 子组织/部门层级 |
| 成员管理 (邀请/移除/角色变更) | SSO / SAML per org |
| 邀请链接 + 邮件邀请 | 跨组织协作 |
| PostgreSQL RLS 数据隔离 | 自定义域名 per org |
| 组织内角色 (owner/admin/instructor/student) | 付费计划 / 订阅管理 |
| 前端组织切换器 | 审计日志 (Phase 3+) |

---

## 2. 行业对标分析

### 2.1 多租户方案对比

| 维度 | Plane.so | Cal.com | Twenty CRM | Formbricks | Supabase |
|------|----------|---------|------------|------------|----------|
| 租户概念 | Workspace | Organization | Workspace | Organization | Organization |
| 隔离方式 | DB filter (workspace_id) | DB filter (team_id) | Schema-per-tenant | DB filter (org_id) | RLS policies |
| 角色模型 | admin/member/guest | owner/admin/member | admin/member | owner/admin/manager/member | owner/member |
| 邀请方式 | 邮件 + 链接 | 邮件 | 邮件 + 链接 | 邮件 | 邮件 + magic link |
| 用户多租户 | ✅ 多 workspace | ✅ 多 team | ✅ 多 workspace | ✅ 多 org | ✅ 多 org |
| 默认租户 | 注册时自动创建 | 注册时自动创建 | 注册时自动创建 | — | — |

### 2.2 行业共识

| 共识 | 覆盖率 | OpenSkill Studio |
|------|--------|-----------------|
| 共享数据库 + 行级过滤 | 5/5 | ✅ RLS + org_id |
| 用户可属于多个组织 | 5/5 | ✅ |
| 邮件邀请 + 邀请链接 | 4/5 | ✅ |
| 角色 per 组织 (非全局) | 5/5 | ✅ |
| 注册时自动创建个人组织 | 3/5 | ❌ 按需创建 |

### 2.3 OpenSkill Studio 的特殊考量

| 教育场景需求 | 与 SaaS 的区别 |
|------------|---------------|
| 班级 = 组织的一种形态 | 不需要 "个人 workspace" |
| instructor 批量导入学员 | 学生可能没有提前注册账号 |
| 学员可同时在多个培训班 | 角色在不同组织可以不同 |
| 课程/技能绑定到组织 | 资源属于组织而非个人 |
| 结业后仍需访问作品集 | 需要 "归档" 而非删除成员 |

---

## 3. 多租户架构决策

### 3.1 为什么 shared-DB + RLS?

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **Shared DB + RLS** | 简单运维、支持跨租户查询、PostgreSQL 原生 | 需谨慎编写 RLS 策略 | ✅ 选择 |
| Schema per tenant | 强隔离 | migration 复杂 (每个 schema 一次)、连接数爆炸 | ❌ |
| DB per tenant | 最强隔离 | 运维噩梦、成本高 | ❌ |

对标 Supabase 的 RLS 方案 — PostgreSQL 原生功能，零额外依赖。

### 3.2 RLS 策略

```
                         ┌─────────────────┐
                         │   API Request    │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   set_config(           │
                    │     'app.current_org_id',│
                    │     org_id              │
                    │   )                     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   SQL Query             │
                    │   SELECT * FROM skills  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   RLS Policy 自动过滤:   │
                    │   WHERE org_id =        │
                    │   current_setting(      │
                    │     'app.current_org_id' │
                    │   )                     │
                    └─────────────────────────┘
```

---

## 4. 数据模型

### 4.1 ER 图

```
┌─────────────────────────────────────────────────────┐
│                    organizations                     │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ name            VARCHAR(100)   NOT NULL               │
│ slug            VARCHAR(100)   UNIQUE, NOT NULL        │
│ description     TEXT           NULL                   │
│ logo_url        TEXT           NULL                   │
│ status          org_status     DEFAULT 'active'       │
│ settings        JSONB          DEFAULT '{}'           │
│ created_by      ULID           FK → users.id          │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
│ updated_at      TIMESTAMPTZ    DEFAULT now()          │
└───────┬─────────────────────────────────────────────┘
        │ 1
        │
        │ N
┌───────┴─────────────────────────────────────────────┐
│                    org_members                        │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ org_id          ULID           FK → organizations.id  │
│ user_id         ULID           FK → users.id          │
│ role            org_role       DEFAULT 'student'      │
│ status          member_status  DEFAULT 'active'       │
│ joined_at       TIMESTAMPTZ    DEFAULT now()          │
│ invited_by      ULID           FK → users.id NULL     │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
│ updated_at      TIMESTAMPTZ    DEFAULT now()          │
├─────────────────────────────────────────────────────┤
│ UNIQUE (org_id, user_id)                             │
│ INDEX (user_id)            -- 查用户的所有组织         │
│ INDEX (org_id, role)       -- 按角色筛选组织成员       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   org_invitations                     │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ org_id          ULID           FK → organizations.id  │
│ email           VARCHAR(255)   NOT NULL               │
│ role            org_role       DEFAULT 'student'      │
│ token_hash      VARCHAR(255)   UNIQUE, NOT NULL       │
│ invited_by      ULID           FK → users.id          │
│ status          invite_status  DEFAULT 'pending'      │
│ expires_at      TIMESTAMPTZ    NOT NULL               │
│ accepted_at     TIMESTAMPTZ    NULL                   │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
├─────────────────────────────────────────────────────┤
│ INDEX (org_id, status)     -- 查组织的待处理邀请       │
│ INDEX (email, status)      -- 查用户的待处理邀请       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  org_invite_links                     │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ org_id          ULID           FK → organizations.id  │
│ code            VARCHAR(20)    UNIQUE, NOT NULL        │
│ role            org_role       DEFAULT 'student'      │
│ max_uses        INT            NULL (无限)             │
│ use_count       INT            DEFAULT 0              │
│ expires_at      TIMESTAMPTZ    NULL (永不过期)         │
│ created_by      ULID           FK → users.id          │
│ is_active       BOOLEAN        DEFAULT true           │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
└─────────────────────────────────────────────────────┘
```

### 4.2 枚举类型

```sql
CREATE TYPE org_status AS ENUM ('active', 'suspended', 'archived');
CREATE TYPE org_role AS ENUM ('owner', 'admin', 'instructor', 'student');
CREATE TYPE member_status AS ENUM ('active', 'archived');
CREATE TYPE invite_status AS ENUM ('pending', 'accepted', 'expired', 'revoked');
```

### 4.3 角色层级

```
owner (组织所有者)
 ├── 删除组织
 ├── 转移所有权
 ├── 管理账单/配额 (未来)
 └── 拥有 admin 的全部权限

admin (组织管理员)
 ├── 管理成员 (邀请/移除/角色变更)
 ├── 创建邀请链接
 ├── 管理组织设置
 └── 拥有 instructor 的全部权限

instructor (教练/讲师)
 ├── 创建/管理技能和项目
 ├── 审核学员提交
 ├── 查看学员进度
 └── 拥有 student 的浏览权限

student (学员)
 ├── 浏览组织内技能和项目
 ├── 提交作品
 ├── 查看个人进度
 └── 管理个人作品集
```

### 4.4 全局角色 vs 组织角色的关系

```
users.role (全局, ADR-002)          org_members.role (per 组织)
─────────────────────────          ────────────────────────────
admin         → 超级管理员           owner     → 组织创建者/所有者
instructor    → 全局默认角色          admin     → 组织管理员
student       → 全局默认角色          instructor → 组织内讲师
                                    student   → 组织内学员
```

- `users.role = admin` 的用户可以管理全平台（绕过组织限制）
- 普通用户的实际权限 = `org_members.role` in 当前组织上下文
- 没有组织上下文时，只能访问个人资料和公开内容

---

## 5. 组织生命周期

### 5.1 创建组织

```python
@router.post("/organizations", response_model=DataResponse[OrgResponse], status_code=201)
async def create_organization(
    body: CreateOrgRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrgService(db)
    org = await service.create(
        name=body.name,
        slug=body.slug,
        description=body.description,
        created_by=user.id,
    )
    # 创建者自动成为 owner
    await service.add_member(org.id, user.id, role=OrgRole.OWNER)
    return DataResponse(data=OrgResponse.from_orm(org))
```

### 5.2 Slug 生成

```python
import re
from ulid import ULID

def generate_slug(name: str) -> str:
    """从组织名生成 URL-friendly slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if len(slug) < 3:
        slug = f"{slug}-{str(ULID())[:6].lower()}"
    return slug[:100]

# 示例:
# "AI 创作者训练营 2026"  → "ai-2026" + 唯一后缀
# "Phixsura Academy"      → "phixsura-academy"
```

### 5.3 组织设置 (JSONB)

```python
# settings 字段存储组织级配置 (JSONB, 可扩展)
DEFAULT_ORG_SETTINGS = {
    "allow_self_registration": False,    # 是否允许通过邀请链接自注册
    "require_email_verification": True,  # 加入时是否要求邮箱已验证
    "default_member_role": "student",    # 新成员默认角色
    "max_members": None,                 # 成员上限 (null = 无限)
}
```

---

## 6. 成员管理

### 6.1 添加成员

```python
async def add_member(
    self, org_id: str, user_id: str, role: OrgRole,
    invited_by: str | None = None,
) -> OrgMember:
    # 检查是否已是成员
    existing = await self._get_member(org_id, user_id)
    if existing:
        if existing.status == MemberStatus.ARCHIVED:
            # 重新激活归档成员
            existing.status = MemberStatus.ACTIVE
            existing.role = role
            return existing
        raise AlreadyMemberError()

    member = OrgMember(
        org_id=org_id,
        user_id=user_id,
        role=role,
        invited_by=invited_by,
    )
    self.db.add(member)
    await self.db.flush()
    return member
```

### 6.2 移除成员 (归档而非删除)

```python
async def remove_member(self, org_id: str, user_id: str, removed_by: str) -> None:
    member = await self._get_active_member(org_id, user_id)

    # owner 不能被移除
    if member.role == OrgRole.OWNER:
        raise CannotRemoveOwnerError()

    # 不能移除自己 (owner 除外，通过 transfer_ownership)
    if user_id == removed_by and member.role != OrgRole.OWNER:
        member.status = MemberStatus.ARCHIVED  # 允许自行退出
    else:
        # 检查操作者权限
        actor = await self._get_active_member(org_id, removed_by)
        if not self._can_manage_member(actor, member):
            raise InsufficientPermissionError()
        member.status = MemberStatus.ARCHIVED

    await self.db.flush()
```

### 6.3 权限管理矩阵

| 操作 | owner | admin | instructor | student |
|------|-------|-------|-----------|---------|
| 邀请 admin | ✅ | ❌ | ❌ | ❌ |
| 邀请 instructor | ✅ | ✅ | ❌ | ❌ |
| 邀请 student | ✅ | ✅ | ✅ | ❌ |
| 移除 admin | ✅ | ❌ | ❌ | ❌ |
| 移除 instructor | ✅ | ✅ | ❌ | ❌ |
| 移除 student | ✅ | ✅ | ✅ | ❌ |
| 修改角色 | ✅ | ❌ | ❌ | ❌ |
| 删除组织 | ✅ | ❌ | ❌ | ❌ |
| 编辑组织设置 | ✅ | ✅ | ❌ | ❌ |
| 创建邀请链接 | ✅ | ✅ | ✅ | ❌ |

**规则**: 只能管理严格低于自己角色的成员。

---

## 7. 邀请流程

### 7.1 邮件邀请

```
Instructor                 FastAPI               DB              Email
  │                          │                   │                │
  │ POST /orgs/:id/invites   │                   │                │
  │ { emails: [...],         │                   │                │
  │   role: "student" }      │                   │                │
  │ ────────────────────────▶│                   │                │
  │                          │                   │                │
  │                          │ 1. 批量创建邀请    │                │
  │                          │ ──────────────────▶│                │
  │                          │                   │                │
  │                          │ 2. 检查已注册用户   │                │
  │                          │ ──────────────────▶│                │
  │                          │                   │                │
  │                          │ 3. 发送邀请邮件     │                │
  │                          │ ──────────────────────────────────▶│
  │                          │                   │                │
  │  { invited: 5,           │                   │                │
  │    already_member: 1,    │                   │                │
  │    already_invited: 0 }  │                   │                │
  │ ◀────────────────────────│                   │                │
```

### 7.2 邀请链接

```
Instructor 创建链接:
  POST /orgs/:id/invite-links
  { role: "student", max_uses: 30, expires_in_days: 7 }
  → { code: "abc123", url: "https://app.openskill.studio/join/abc123" }

学生使用链接:
  GET /join/abc123 (前端)
    → 未登录 → 重定向 /register?invite=abc123
    → 已登录 → POST /api/v1/invites/accept { code: "abc123" }
      → 加入组织, 角色 = 链接指定的角色
```

### 7.3 批量导入 (CSV)

```
POST /orgs/:id/members/import
Content-Type: multipart/form-data
{ file: students.csv }

# CSV 格式:
email,display_name,role
alice@school.com,Alice Wang,student
bob@school.com,Bob Li,student

# 处理逻辑:
# 1. 已注册 + 未加入 → 直接加入组织
# 2. 已注册 + 已加入 → 跳过
# 3. 未注册 → 创建邀请 + 发送邮件
```

---

## 8. PostgreSQL RLS 行级安全

### 8.1 RLS 策略 SQL

```sql
-- 启用 RLS (对所有含 org_id 的业务表)
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

-- 基本策略: 只能看到当前组织的数据
CREATE POLICY org_isolation ON skills
  USING (org_id = current_setting('app.current_org_id', true)::text);

CREATE POLICY org_isolation ON projects
  USING (org_id = current_setting('app.current_org_id', true)::text);

CREATE POLICY org_isolation ON submissions
  USING (org_id = current_setting('app.current_org_id', true)::text);

-- 超级管理员绕过 RLS
-- FastAPI 不设置 app.current_org_id 时，RLS 返回空结果 (安全默认)
-- admin 用户使用独立的无 RLS session
```

### 8.2 FastAPI RLS 集成

```python
# app/api/deps.py
from sqlalchemy import text

async def get_org_db(
    org_id: str,  # 从路径参数或请求头获取
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """
    注入组织上下文的 DB session.
    1. 验证用户是该组织的活跃成员
    2. 设置 RLS 上下文变量
    """
    # 检查成员资格
    member = await db.execute(
        select(OrgMember)
        .where(OrgMember.org_id == org_id)
        .where(OrgMember.user_id == user.id)
        .where(OrgMember.status == MemberStatus.ACTIVE)
    )
    if member.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    # 设置 RLS 上下文
    await db.execute(text("SET LOCAL app.current_org_id = :org_id"), {"org_id": org_id})

    return db
```

### 8.3 请求头 vs 路径参数

```
方案 A: 路径参数 (选择 ✅)
  GET /api/v1/orgs/{org_id}/skills
  GET /api/v1/orgs/{org_id}/projects

方案 B: 请求头
  GET /api/v1/skills
  X-Organization-Id: 01JKXYZ...

方案 C: 子域名
  GET https://myorg.openskill.studio/api/v1/skills
```

**选择方案 A** — 路径参数：
- 语义最清晰，REST 风格
- 对标 Plane (`/api/v1/workspaces/{slug}/...`)
- URL 可分享、可收藏
- 无需特殊中间件

---

## 9. API 端点设计

### 9.1 完整端点列表

```
Organizations (/api/v1/orgs)
├── POST   /                         创建组织
├── GET    /                         列出我的组织
├── GET    /:org_id                  获取组织详情
├── PUT    /:org_id                  更新组织信息
├── DELETE /:org_id                  删除组织 (owner only)
│
├── Members (/api/v1/orgs/:org_id/members)
│   ├── GET    /                     列出组织成员 (分页, 筛选)
│   ├── POST   /                     直接添加成员 (admin+)
│   ├── PUT    /:user_id             修改成员角色
│   ├── DELETE /:user_id             移除成员 (归档)
│   └── POST   /import               批量导入 (CSV)
│
├── Invitations (/api/v1/orgs/:org_id/invites)
│   ├── GET    /                     列出邀请
│   ├── POST   /                     批量邮件邀请
│   └── DELETE /:invite_id           撤销邀请
│
├── Invite Links (/api/v1/orgs/:org_id/invite-links)
│   ├── GET    /                     列出邀请链接
│   ├── POST   /                     创建邀请链接
│   ├── PUT    /:link_id             启用/禁用链接
│   └── DELETE /:link_id             删除链接
│
└── Settings
    └── PUT    /:org_id/settings      更新组织设置

Invite Actions (/api/v1/invites)
├── POST   /accept                   接受邮件邀请 (token)
└── POST   /join                     通过链接加入 (code)
```

### 9.2 响应示例

```json
// GET /api/v1/orgs — 200
{
  "data": [
    {
      "id": "01JKXYZ...",
      "name": "AI 创作者训练营",
      "slug": "ai-creator-camp",
      "description": "2026 年暑期 AI 创作训练",
      "logo_url": null,
      "role": "instructor",
      "member_count": 32,
      "created_at": "2026-08-13T10:00:00Z"
    }
  ],
  "meta": { "total": 2, "page": 1, "per_page": 20, "has_more": false }
}

// GET /api/v1/orgs/:org_id/members — 200
{
  "data": [
    {
      "id": "01JKXYZ...",
      "user": {
        "id": "01JKABC...",
        "email": "instructor@example.com",
        "display_name": "张老师",
        "avatar_url": null
      },
      "role": "instructor",
      "status": "active",
      "joined_at": "2026-08-13T10:00:00Z"
    }
  ],
  "meta": { "total": 32, "page": 1, "per_page": 20, "has_more": true }
}
```

---

## 10. 前端组织上下文

### 10.1 组织切换器

```typescript
// lib/org.ts — 组织上下文状态
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface OrgState {
  currentOrgId: string | null;
  currentOrg: OrgResponse | null;
  setCurrentOrg: (org: OrgResponse) => void;
  clearOrg: () => void;
}

export const useOrgStore = create<OrgState>()(
  persist(
    (set) => ({
      currentOrgId: null,
      currentOrg: null,
      setCurrentOrg: (org) => set({ currentOrgId: org.id, currentOrg: org }),
      clearOrg: () => set({ currentOrgId: null, currentOrg: null }),
    }),
    { name: "openskill-org" },
  ),
);
```

### 10.2 URL 结构

```
/dashboard                        ← 选择组织
/orgs/:slug/overview              ← 组织首页
/orgs/:slug/skills                ← 组织内技能
/orgs/:slug/projects              ← 组织内项目
/orgs/:slug/members               ← 成员管理
/orgs/:slug/settings              ← 组织设置
```

### 10.3 组织 Layout

```tsx
// app/(dashboard)/orgs/[slug]/layout.tsx
import { OrgProvider } from "@/providers/org";

export default async function OrgLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { slug: string };
}) {
  return (
    <OrgProvider slug={params.slug}>
      <div className="flex h-screen">
        <OrgSidebar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </OrgProvider>
  );
}
```

---

## 11. 跨组织数据隔离

### 11.1 数据归属规则

| 数据类型 | 归属 | 说明 |
|---------|------|------|
| 用户资料 | 全局 (users) | 跨组织共享 |
| 技能定义 | 组织 (org_id) | 每个组织独立技能库 |
| 项目 | 组织 (org_id) | 项目属于组织 |
| 提交物 | 组织 (org_id) + 用户 (user_id) | 双重归属 |
| 作品集 | 用户 (全局) | 跨组织汇聚个人作品 |
| 文件 | 组织 (S3 prefix: `orgs/{org_id}/`) | MinIO 按组织分目录 |

### 11.2 S3 路径规范

```
openskill/                          # S3 bucket
├── orgs/
│   ├── {org_id}/
│   │   ├── logos/                  # 组织 logo
│   │   ├── skills/                 # 技能素材
│   │   ├── projects/               # 项目素材
│   │   └── submissions/            # 学员提交物
│   │       └── {user_id}/
│   │           └── {submission_id}/
│   └── ...
├── users/
│   └── {user_id}/
│       ├── avatars/                # 头像
│       └── portfolio/              # 作品集文件
```

---

## 12. 计费与配额预留

### 12.1 配额模型 (Phase 3+)

```python
# organizations.settings JSONB 中预留的配额字段
QUOTA_FIELDS = {
    "max_members": None,        # 最大成员数 (null = 无限)
    "max_projects": None,       # 最大项目数
    "max_storage_mb": None,     # 最大存储 (MB)
    "max_ai_evaluations": None, # 每月 AI 评估次数
}
```

### 12.2 配额检查中间件 (Phase 3+)

```python
# 未来: 在创建资源前检查配额
async def check_org_quota(org_id: str, resource: str, db: AsyncSession):
    org = await db.get(Organization, org_id)
    limit = org.settings.get(f"max_{resource}")
    if limit is not None:
        current = await count_resources(org_id, resource, db)
        if current >= limit:
            raise QuotaExceededError(resource, limit)
```

---

## 13. 测试策略

### 13.1 测试用例

```python
class TestOrganization:
    async def test_create_org(self, client, auth_headers):
        response = await client.post("/api/v1/orgs", json={
            "name": "Test Org", "slug": "test-org"
        }, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["data"]["slug"] == "test-org"

    async def test_creator_is_owner(self, client, auth_headers, org):
        members = await client.get(f"/api/v1/orgs/{org.id}/members", headers=auth_headers)
        owner = [m for m in members.json()["data"] if m["role"] == "owner"]
        assert len(owner) == 1

    async def test_duplicate_slug_rejected(self, client, auth_headers, org):
        response = await client.post("/api/v1/orgs", json={
            "name": "Another", "slug": org.slug
        }, headers=auth_headers)
        assert response.status_code == 409


class TestMemberManagement:
    async def test_invite_member(self, client, owner_headers, org):
        response = await client.post(f"/api/v1/orgs/{org.id}/invites", json={
            "emails": ["student@example.com"], "role": "student"
        }, headers=owner_headers)
        assert response.status_code == 200
        assert response.json()["invited"] == 1

    async def test_student_cannot_invite(self, client, student_headers, org):
        response = await client.post(f"/api/v1/orgs/{org.id}/invites", json={
            "emails": ["another@example.com"], "role": "student"
        }, headers=student_headers)
        assert response.status_code == 403

    async def test_cannot_remove_owner(self, client, admin_headers, org, owner_id):
        response = await client.delete(
            f"/api/v1/orgs/{org.id}/members/{owner_id}", headers=admin_headers
        )
        assert response.status_code == 403


class TestRLS:
    async def test_org_a_cannot_see_org_b_data(self, client, org_a_member_headers, org_b):
        """关键隔离测试: 组织 A 的成员不能访问组织 B 的数据."""
        response = await client.get(
            f"/api/v1/orgs/{org_b.id}/skills", headers=org_a_member_headers
        )
        assert response.status_code == 403

    async def test_non_member_cannot_access_org(self, client, auth_headers, private_org):
        response = await client.get(
            f"/api/v1/orgs/{private_org.id}/members", headers=auth_headers
        )
        assert response.status_code == 403
```

---

## 14. 验收标准

| # | 验收项 | 方案章节 |
|---|--------|---------|
| 1 | 用户可创建组织 | §5.1 |
| 2 | 组织创建者自动成为 owner | §5.1 |
| 3 | 用户可属于多个组织 | §4 |
| 4 | 同一用户在不同组织可有不同角色 | §4.3 |
| 5 | 组织 owner/admin 可邀请新成员 | §7 |
| 6 | 邀请链接可正常工作 | §7.2 |
| 7 | 成员移除采用归档策略 | §6.2 |
| 8 | RLS 策略正确隔离跨组织数据 | §8 |
| 9 | 非成员无法访问组织资源 | §8 |
| 10 | 前端组织切换器正常工作 | §10 |
| 11 | URL 结构包含组织 slug | §10.2 |
| 12 | 批量导入 CSV 可正常工作 | §7.3 |
| 13 | 权限矩阵中的全部规则通过测试 | §6.3 |

---

## 15. 实施计划

### Phase 1: 数据模型 (~2h)

1. Organization / OrgMember / OrgInvitation 模型 + migration
2. 枚举类型 (org_role, org_status, member_status, invite_status)
3. OrgService 核心逻辑 (create, add_member, remove_member)
4. 组织 CRUD 端点

### Phase 2: 邀请系统 (~2h)

5. 邮件邀请流程
6. 邀请链接 (create, accept, revoke)
7. 批量导入 (CSV 解析 + 处理)
8. 前端邀请 UI

### Phase 3: RLS + 安全 (~1.5h)

9. PostgreSQL RLS 策略 (Alembic migration)
10. FastAPI RLS session 注入
11. 跨组织隔离测试
12. 权限矩阵集成测试

### Phase 4: 前端 (~1.5h)

13. 组织切换器组件
14. 组织 layout + sidebar
15. 成员管理页面
16. 组织设置页面

---

## 新增依赖

### 后端

```toml
# 无新增 — 使用 SQLAlchemy + PostgreSQL 原生 RLS
```

### 前端

```json
{
  "dependencies": {
    // zustand persist 已包含在 zustand 中
  }
}
```

---

## ADR 元数据

- **Status**: Proposed
- **Decision**: Shared-DB multitenancy with PostgreSQL RLS, path-parameter org context, org-scoped RBAC (owner/admin/instructor/student)
- **Context**: Education platform where students belong to classes/orgs managed by instructors. Data isolation is critical but full DB-per-tenant is overkill.
- **Consequences**: RLS policies must be applied to every new table with org_id. Path-parameter approach makes URL structure verbose but explicit. Invitation system adds complexity but is essential for education workflows.

---

*ADR-003 v1 — 组织与多租户完整设计。*
