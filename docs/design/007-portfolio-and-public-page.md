# OpenSkill Studio — 作品集与公开页设计 (ADR-007)

> 对标 Behance / Dribbble / Read.cv / Polywork / freeCodeCamp Certifications / GitHub Profile
>
> Status: **Proposed** | Author: Lyphixia Wang | Date: 2026-08-13
> Depends on: ADR-002 (Auth), ADR-005 (Projects & Submissions)

---

## 目录

1. [设计目标](#1-设计目标)
2. [行业对标分析](#2-行业对标分析)
3. [领域模型](#3-领域模型)
4. [数据模型](#4-数据模型)
5. [作品发布流程](#5-作品发布流程)
6. [公开个人页](#6-公开个人页)
7. [SEO 与社交分享](#7-seo-与社交分享)
8. [访问控制与隐私](#8-访问控制与隐私)
9. [API 端点设计](#9-api-端点设计)
10. [前端设计](#10-前端设计)
11. [搜索与发现](#11-搜索与发现)
12. [测试策略](#12-测试策略)
13. [验收标准](#13-验收标准)
14. [实施计划](#14-实施计划)

---

## 1. 设计目标

### 1.1 核心目标

- **成果展示** — 学员将优秀项目提交转化为公开作品，构建个人品牌
- **个人主页** — 每个用户有一个公开的个人页面 (username.openskill.studio 或 /u/username)
- **可分享** — 作品和个人页可分享到社交媒体，有 OG 卡片
- **SEO 友好** — SSR 渲染、结构化数据、sitemap
- **跨组织汇聚** — 作品集汇聚用户在所有组织中的优秀作品

### 1.2 边界

| 包含 | 不包含 (后续) |
|------|-------------|
| 个人公开页 | 自定义域名 (username.com) |
| 作品发布 (从提交转化) | 博客/文章系统 |
| 技能徽章展示 | NFT / 区块链认证 |
| OG 卡片 + SEO | 作品评论 / 点赞 |
| 作品集编辑 (排序/描述) | 推荐算法 / 发现页 |
| 隐私控制 (公开/私密) | 多语言页面 |

---

## 2. 行业对标分析

### 2.1 作品集/个人页对比

| 维度 | Behance | Read.cv | Polywork | freeCodeCamp | GitHub Profile |
|------|---------|---------|---------|-------------|---------------|
| 公开页 URL | behance.net/username | read.cv/username | polywork.com/username | freecodecamp.org/username | github.com/username |
| 作品来源 | 手动上传 | 手动编辑 | 关联外部 | 课程认证 | 代码仓库 |
| 技能展示 | 标签 | 技能列表 | 标签 | 认证徽章 | 语言统计 |
| SEO | ✅ | ✅ | ✅ | ✅ | ✅ |
| OG 卡片 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 自定义 | 布局/封面 | 简洁固定 | 时间线 | 固定 | README 自定义 |
| 隐私 | 公开/私密 | 公开 | 公开/私密 | 公开 | 公开/私密 |

### 2.2 OpenSkill Studio 的差异化

| 特点 | 说明 |
|------|------|
| 作品 = 训练成果 | 不是空白上传，而是从课程项目提交中"毕业" |
| 技能认证可验证 | 展示的技能有完成度数据支撑 |
| AI 评分可展示 | 可选展示 AI 评估分数 |
| 组织关联 | 可展示"在 XX 训练营完成" |

---

## 3. 领域模型

### 3.1 核心概念

```
User
 ├── Profile (公开资料)
 │    ├── username (唯一, URL-friendly)
 │    ├── display_name
 │    ├── bio
 │    ├── avatar
 │    ├── social_links
 │    └── visibility (public/private)
 │
 ├── Portfolio Items (作品集条目)
 │    ├── Item 1 (从 Submission 发布)
 │    │    ├── 标题、描述 (可编辑)
 │    │    ├── 封面图
 │    │    ├── 标签
 │    │    ├── 关联技能
 │    │    └── 来源: "AI 训练营 / Chatbot 项目"
 │    ├── Item 2 (独立作品 — 无关联提交)
 │    └── ...
 │
 └── Skill Badges (技能徽章)
      ├── "Prompt Engineering" ✓ (完成度 100%)
      ├── "Python 基础" ✓ (完成度 100%)
      └── "Few-Shot Prompting" (进行中, 60%)
```

### 3.2 作品来源

```
来源 1: 从项目提交发布 (主要路径)
  Submission (approved, score >= threshold)
    → 用户点击 "发布到作品集"
      → 创建 PortfolioItem (关联 submission_id)

来源 2: 独立作品 (补充路径)
  用户手动创建 PortfolioItem
    → 上传封面 + 描述 + 链接
    → 无关联提交 (submission_id = null)
```

---

## 4. 数据模型

### 4.1 ER 图

```
┌──────────────────────────────────────────────────────┐
│                    user_profiles                      │
├──────────────────────────────────────────────────────┤
│ user_id         ULID           PK, FK → users.id      │
│ username        VARCHAR(40)    UNIQUE, NOT NULL         │
│ headline        VARCHAR(200)   NULL ("AI Developer")   │
│ bio             TEXT           NULL (Markdown)          │
│ location        VARCHAR(100)   NULL                    │
│ website_url     VARCHAR(500)   NULL                    │
│ social_links    JSONB          DEFAULT '{}'            │
│ visibility      profile_vis    DEFAULT 'public'        │
│ theme           VARCHAR(20)    DEFAULT 'default'       │
│ custom_og_image VARCHAR(500)   NULL                    │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ INDEX (username)               -- 公开页路由解析        │
│ INDEX (visibility)             -- 公开用户搜索          │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                   portfolio_items                     │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ user_id         ULID           FK → users.id           │
│ submission_id   ULID           FK → submissions.id NULL│
│ title           VARCHAR(200)   NOT NULL                │
│ slug            VARCHAR(200)   NOT NULL                │
│ description     TEXT           NULL (Markdown)          │
│ cover_image_url VARCHAR(500)   NULL                    │
│ tags            TEXT[]         DEFAULT '{}'            │
│ skills          ULID[]         DEFAULT '{}'            │
│ external_url    VARCHAR(500)   NULL                    │
│ source_org_name VARCHAR(100)   NULL                    │
│ source_project  VARCHAR(200)   NULL                    │
│ score           INT            NULL (可选展示)          │
│ show_score      BOOLEAN        DEFAULT false           │
│ visibility      item_vis       DEFAULT 'public'        │
│ featured        BOOLEAN        DEFAULT false           │
│ sort_order      INT            DEFAULT 0               │
│ published_at    TIMESTAMPTZ    NULL                    │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ UNIQUE (user_id, slug)                                │
│ INDEX (user_id, visibility, sort_order)               │
│ INDEX (user_id, featured)                             │
│ GIN INDEX (tags)                                      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                   skill_badges                        │
├──────────────────────────────────────────────────────┤
│ id              ULID           PK                     │
│ user_id         ULID           FK → users.id           │
│ skill_id        ULID           FK → skills.id          │
│ org_id          ULID           FK → organizations.id   │
│ skill_name      VARCHAR(200)   NOT NULL (冗余, 展示用)  │
│ category_name   VARCHAR(100)   NOT NULL                │
│ completion_pct  INT            NOT NULL (0-100)         │
│ completed_at    TIMESTAMPTZ    NULL                    │
│ show_on_profile BOOLEAN        DEFAULT true            │
│ created_at      TIMESTAMPTZ    DEFAULT now()           │
│ updated_at      TIMESTAMPTZ    DEFAULT now()           │
├──────────────────────────────────────────────────────┤
│ UNIQUE (user_id, skill_id, org_id)                    │
│ INDEX (user_id, show_on_profile)                      │
└──────────────────────────────────────────────────────┘
```

### 4.2 枚举类型

```sql
CREATE TYPE profile_vis AS ENUM ('public', 'private');
CREATE TYPE item_vis AS ENUM ('public', 'unlisted', 'private');
-- unlisted: 有链接可访问，不在公开列表中出现
```

### 4.3 social_links 结构

```json
{
  "github": "https://github.com/alice",
  "twitter": "https://twitter.com/alice",
  "linkedin": "https://linkedin.com/in/alice",
  "bilibili": "https://space.bilibili.com/12345"
}
```

---

## 5. 作品发布流程

### 5.1 从提交发布

```
学员提交项目
    │
    ▼
Instructor/AI 评审通过
    │
    ▼
提交状态 = approved
    │
    ▼
前端显示 "🎉 发布到作品集" 按钮
    │
    ▼
用户点击 → 编辑作品信息
    ├── 标题 (默认 = 项目标题)
    ├── 描述 (默认 = 项目描述, 可编辑)
    ├── 封面图 (上传或从提交文件选择)
    ├── 标签
    ├── 是否展示评分 (show_score)
    └── 可见性 (公开/仅链接/私密)
    │
    ▼
创建 PortfolioItem
    ├── submission_id = 提交 ID
    ├── source_org_name = 组织名 (冗余)
    ├── source_project = 项目名 (冗余)
    └── score = 提交最终分数
```

### 5.2 为什么冗余存储组织名/项目名?

- 用户可能离开组织，但作品集应保留
- 组织可能改名/删除，公开页不应受影响
- 公开页渲染不需要跨表 JOIN (性能)

### 5.3 发布 API

```python
@router.post("/portfolio/items", response_model=DataResponse[PortfolioItemResponse], status_code=201)
async def publish_to_portfolio(
    body: CreatePortfolioItemRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PortfolioService(db)

    if body.submission_id:
        # 从提交发布 — 验证所有权 + 状态
        submission = await db.get(Submission, body.submission_id)
        if submission is None or submission.user_id != user.id:
            raise HTTPException(status_code=404)
        if submission.status != SubmissionStatus.APPROVED:
            raise HTTPException(status_code=422, detail="Submission must be approved")

    item = await service.create_item(
        user_id=user.id,
        title=body.title,
        description=body.description,
        submission_id=body.submission_id,
        tags=body.tags,
        visibility=body.visibility,
    )
    return DataResponse(data=PortfolioItemResponse.from_orm(item))
```

---

## 6. 公开个人页

### 6.1 URL 结构

```
方案: 路径前缀
  https://openskill.studio/u/alice
  https://openskill.studio/u/alice/projects/chatbot-v2

预留 (Phase 3+): 子域名
  https://alice.openskill.studio
```

**选择路径前缀** `/u/username` — 无需 DNS 通配符、开发环境友好、CDN 简单。

### 6.2 Username 规则

```python
import re

USERNAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9])){2,38}[a-z0-9]$")

# 保留名列表 (不可注册)
RESERVED_USERNAMES = {
    "admin", "api", "app", "auth", "blog", "dashboard",
    "docs", "help", "login", "logout", "register", "settings",
    "status", "support", "www", "health", "about", "pricing",
    "terms", "privacy", "u", "orgs", "join", "invite",
}

def validate_username(username: str) -> bool:
    if username in RESERVED_USERNAMES:
        return False
    if not USERNAME_PATTERN.match(username):
        return False
    return True
```

### 6.3 页面布局

```
┌─────────────────────────────────────────────────────────┐
│  ┌──────┐                                               │
│  │Avatar│  Alice Wang                                   │
│  └──────┘  AI Developer & Prompt Engineer               │
│            Beijing, China                                │
│            🔗 alice.dev  🐙 GitHub  🐦 Twitter           │
│                                                         │
│  ── Skills ──────────────────────────────────────────── │
│  [Prompt Engineering ✓] [Python ✓] [LLM Apps ●60%]     │
│                                                         │
│  ── Featured Projects ───────────────────────────────── │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 🖼 Cover    │  │ 🖼 Cover    │  │ 🖼 Cover    │     │
│  │ AI Chatbot  │  │ Prompt Lib  │  │ Data Viz    │     │
│  │ ⭐ 92/100   │  │ ⭐ 88/100   │  │             │     │
│  │ #ai #llm    │  │ #prompt     │  │ #dataviz    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
│  ── All Projects ────────────────────────────────────── │
│  ...                                                    │
│                                                         │
│  ── About ───────────────────────────────────────────── │
│  (Bio — Markdown 渲染)                                   │
│                                                         │
│  ⚡ Powered by OpenSkill Studio                         │
└─────────────────────────────────────────────────────────┘
```

---

## 7. SEO 与社交分享

### 7.1 Meta Tags (SSR)

```tsx
// app/u/[username]/page.tsx
import type { Metadata } from "next";

export async function generateMetadata({ params }): Promise<Metadata> {
  const profile = await getPublicProfile(params.username);

  return {
    title: `${profile.display_name} | OpenSkill Studio`,
    description: profile.headline || profile.bio?.slice(0, 160),
    openGraph: {
      title: `${profile.display_name} — ${profile.headline}`,
      description: profile.bio?.slice(0, 300),
      url: `https://openskill.studio/u/${profile.username}`,
      type: "profile",
      images: [profile.custom_og_image || profile.avatar_url || "/og-default.png"],
    },
    twitter: {
      card: "summary_large_image",
      title: `${profile.display_name} | OpenSkill Studio`,
      description: profile.headline,
    },
  };
}
```

### 7.2 结构化数据 (JSON-LD)

```tsx
<script type="application/ld+json">
{JSON.stringify({
  "@context": "https://schema.org",
  "@type": "Person",
  "name": profile.display_name,
  "url": `https://openskill.studio/u/${profile.username}`,
  "image": profile.avatar_url,
  "jobTitle": profile.headline,
  "sameAs": Object.values(profile.social_links || {}),
})}
</script>
```

### 7.3 动态 OG 图片 (Phase 2+)

```
Phase 1: 静态 OG 图片 (用户上传或默认)
Phase 2+: 动态生成 OG 图片
  → Next.js OG Image Generation (Satori + Resvg)
  → 自动包含: 头像 + 姓名 + 标题 + 技能徽章
  → 路由: /api/og/u/[username]
```

### 7.4 Sitemap

```xml
<!-- public/sitemap.xml (动态生成) -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://openskill.studio/u/alice</loc>
    <lastmod>2026-08-13</lastmod>
    <changefreq>weekly</changefreq>
  </url>
  <!-- ... all public profiles ... -->
</urlset>
```

```typescript
// app/sitemap.ts
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const profiles = await getPublicProfiles();

  return profiles.map((p) => ({
    url: `https://openskill.studio/u/${p.username}`,
    lastModified: p.updated_at,
    changeFrequency: "weekly",
    priority: 0.7,
  }));
}
```

---

## 8. 访问控制与隐私

### 8.1 可见性规则

| 级别 | 个人页 | 作品列表 | 单个作品 |
|------|--------|---------|---------|
| **public** | 任何人可见 | 出现在搜索和列表中 | 任何人可见 |
| **unlisted** | — | 不出现在列表中 | 有链接可见 |
| **private** | 仅自己可见 | 不可见 | 仅自己可见 |

### 8.2 数据脱敏

公开页**不暴露**:
- 用户邮箱
- 组织内部 ID
- 未发布的提交物
- 具体评审反馈 (仅展示分数，如果 show_score=true)
- 其他学员信息

### 8.3 API 权限

```python
# 公开 API — 无需认证
@router.get("/u/{username}", response_model=PublicProfileResponse)
async def get_public_profile(username: str, db: AsyncSession = Depends(get_db)):
    profile = await get_profile_by_username(db, username)
    if profile is None or profile.visibility != ProfileVisibility.PUBLIC:
        raise HTTPException(status_code=404)
    return PublicProfileResponse.from_profile(profile)

# 私有 API — 需要认证 (编辑自己的)
@router.put("/portfolio/profile", response_model=DataResponse[ProfileResponse])
async def update_profile(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ...
```

---

## 9. API 端点设计

### 9.1 完整端点列表

```
Public (无需认证)
├── GET    /u/:username               公开个人页数据
├── GET    /u/:username/items         公开作品列表
└── GET    /u/:username/items/:slug   公开作品详情

Portfolio Management (需认证 — 管理自己的)
├── Profile
│   ├── GET    /portfolio/profile      获取我的资料
│   ├── PUT    /portfolio/profile      更新资料
│   └── PUT    /portfolio/username     修改 username
│
├── Items
│   ├── GET    /portfolio/items        列出我的作品
│   ├── POST   /portfolio/items        创建作品 (发布/独立)
│   ├── GET    /portfolio/items/:id    获取作品详情
│   ├── PUT    /portfolio/items/:id    编辑作品
│   ├── DELETE /portfolio/items/:id    删除作品
│   └── PUT    /portfolio/items/reorder  调整排序
│
├── Badges
│   ├── GET    /portfolio/badges       列出我的技能徽章
│   └── PUT    /portfolio/badges/:id   切换展示/隐藏
│
└── Cover Images
    └── POST   /portfolio/upload-cover  上传封面图
```

### 9.2 公开页响应示例

```json
// GET /u/alice — 200
{
  "username": "alice",
  "display_name": "Alice Wang",
  "headline": "AI Developer & Prompt Engineer",
  "bio": "Passionate about building AI-powered applications...",
  "avatar_url": "https://cdn.openskill.studio/users/01JK.../avatar.jpg",
  "location": "Beijing, China",
  "website_url": "https://alice.dev",
  "social_links": {
    "github": "https://github.com/alice",
    "twitter": "https://twitter.com/alice"
  },
  "skills": [
    { "name": "Prompt Engineering", "category": "AI", "completed": true },
    { "name": "Python", "category": "Programming", "completed": true },
    { "name": "LLM Applications", "category": "AI", "completion_pct": 60, "completed": false }
  ],
  "featured_items": [
    {
      "slug": "ai-chatbot-v2",
      "title": "AI Chatbot v2",
      "description": "A multi-turn chatbot with RAG...",
      "cover_image_url": "https://cdn...",
      "tags": ["ai", "llm", "chatbot"],
      "score": 92,
      "show_score": true,
      "source_org_name": "AI 创作者训练营",
      "published_at": "2026-08-10T00:00:00Z"
    }
  ],
  "item_count": 5,
  "joined_at": "2026-06-01T00:00:00Z"
}
```

---

## 10. 前端设计

### 10.1 页面结构

```
/u/:username                        公开个人页 (SSR)
/u/:username/:item_slug              公开作品详情 (SSR)

/dashboard/portfolio                 我的作品集管理
/dashboard/portfolio/profile         编辑个人资料
/dashboard/portfolio/items           管理作品列表
/dashboard/portfolio/items/new       创建新作品
/dashboard/portfolio/items/:id/edit  编辑作品
```

### 10.2 个人页组件

```tsx
// app/u/[username]/page.tsx — Server Component (SSR for SEO)
export default async function PublicProfilePage({ params }: { params: { username: string } }) {
  const profile = await fetchPublicProfile(params.username);

  if (!profile) {
    notFound();
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-12">
      <ProfileHeader profile={profile} />
      <SkillBadges skills={profile.skills} />
      <FeaturedItems items={profile.featured_items} />
      <AllItems username={profile.username} />
      <Bio content={profile.bio} />
      <Footer />
    </main>
  );
}
```

### 10.3 作品卡片

```tsx
function PortfolioCard({ item }: { item: PortfolioItem }) {
  return (
    <a href={`/u/${item.username}/${item.slug}`} className="group block">
      <div className="overflow-hidden rounded-lg border transition-shadow hover:shadow-md">
        {item.cover_image_url ? (
          <img src={item.cover_image_url} alt={item.title}
               className="aspect-video w-full object-cover" />
        ) : (
          <div className="aspect-video w-full bg-muted flex items-center justify-center">
            <span className="text-4xl">🎨</span>
          </div>
        )}
        <div className="p-4">
          <h3 className="font-semibold group-hover:text-primary">{item.title}</h3>
          {item.show_score && item.score && (
            <span className="text-sm text-muted-foreground">⭐ {item.score}/100</span>
          )}
          <div className="mt-2 flex flex-wrap gap-1">
            {item.tags.map((tag) => (
              <span key={tag} className="rounded-full bg-secondary px-2 py-0.5 text-xs">
                {tag}
              </span>
            ))}
          </div>
          {item.source_org_name && (
            <p className="mt-2 text-xs text-muted-foreground">
              📍 {item.source_org_name}
            </p>
          )}
        </div>
      </div>
    </a>
  );
}
```

### 10.4 技能徽章展示

```tsx
function SkillBadges({ skills }: { skills: SkillBadge[] }) {
  return (
    <section className="mt-6">
      <h2 className="text-lg font-semibold mb-3">Skills</h2>
      <div className="flex flex-wrap gap-2">
        {skills.map((skill) => (
          <div
            key={skill.name}
            className={`rounded-full px-3 py-1 text-sm font-medium ${
              skill.completed
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                : "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
            }`}
          >
            {skill.completed ? "✓" : `${skill.completion_pct}%`} {skill.name}
          </div>
        ))}
      </div>
    </section>
  );
}
```

---

## 11. 搜索与发现

### 11.1 Phase 1: 基础搜索

```
GET /api/v1/discover/profiles?q=alice&skill=prompt-engineering
  → PostgreSQL ILIKE + GIN (tags)
```

### 11.2 Phase 3+: 发现页

```
/discover
  ├── 热门作品 (按浏览/分享量排序)
  ├── 最新发布
  ├── 按技能/标签筛选
  └── 搜索框
```

### 11.3 robots.txt

```txt
User-agent: *
Allow: /u/
Disallow: /dashboard/
Disallow: /api/
Sitemap: https://openskill.studio/sitemap.xml
```

---

## 12. 测试策略

### 12.1 关键测试用例

```python
class TestPublicProfile:
    async def test_public_profile_accessible(self, client, user_with_profile):
        response = await client.get("/u/alice")
        assert response.status_code == 200
        assert response.json()["display_name"] == "Alice Wang"

    async def test_private_profile_returns_404(self, client, private_user):
        response = await client.get("/u/private-user")
        assert response.status_code == 404

    async def test_profile_hides_email(self, client, user_with_profile):
        response = await client.get("/u/alice")
        assert "email" not in response.json()

    async def test_reserved_username_rejected(self, client, auth_headers):
        response = await client.put("/portfolio/username",
            json={"username": "admin"}, headers=auth_headers)
        assert response.status_code == 422


class TestPortfolioItems:
    async def test_publish_approved_submission(self, client, auth_headers, approved_submission):
        response = await client.post("/portfolio/items", json={
            "submission_id": approved_submission.id,
            "title": "My Chatbot",
            "tags": ["ai", "chatbot"],
        }, headers=auth_headers)
        assert response.status_code == 201

    async def test_cannot_publish_unapproved_submission(self, client, auth_headers, draft_sub):
        response = await client.post("/portfolio/items", json={
            "submission_id": draft_sub.id,
            "title": "Draft Work",
        }, headers=auth_headers)
        assert response.status_code == 422

    async def test_unlisted_item_accessible_by_link(self, client, unlisted_item):
        response = await client.get(f"/u/alice/{unlisted_item.slug}")
        assert response.status_code == 200

    async def test_unlisted_item_not_in_list(self, client, unlisted_item):
        response = await client.get("/u/alice/items")
        slugs = [i["slug"] for i in response.json()["data"]]
        assert unlisted_item.slug not in slugs


class TestSkillBadges:
    async def test_badges_sync_from_progress(self, client, auth_headers):
        # 完成技能后，徽章自动出现
        await complete_skill(skill_id)
        badges = await client.get("/portfolio/badges", headers=auth_headers)
        assert any(b["skill_name"] == "Prompt Engineering" for b in badges.json()["data"])

    async def test_hidden_badge_not_on_public_page(self, client, auth_headers):
        await hide_badge(badge_id)
        response = await client.get("/u/alice")
        skills = response.json()["skills"]
        assert not any(s["name"] == "Hidden Skill" for s in skills)
```

---

## 13. 验收标准

| # | 验收项 | 方案章节 |
|---|--------|---------|
| 1 | 用户可设置 username | §6.2 |
| 2 | 公开个人页可访问 (/u/username) | §6 |
| 3 | 用户可将通过的提交发布为作品 | §5 |
| 4 | 用户可创建独立作品 | §5 |
| 5 | 作品支持封面图上传 | §4.1 |
| 6 | 技能徽章自动同步 | §4.1 |
| 7 | 公开页有 OG 卡片 (SSR) | §7 |
| 8 | 公开页有 JSON-LD 结构化数据 | §7.2 |
| 9 | 隐私控制 (公开/仅链接/私密) | §8 |
| 10 | 公开页不暴露用户邮箱 | §8.2 |
| 11 | 作品可排序/置顶 | §4.1 (featured, sort_order) |
| 12 | 保留 username 列表生效 | §6.2 |
| 13 | Sitemap 包含公开用户 | §7.4 |

---

## 14. 实施计划

### Phase 1: 数据模型 + 个人资料 (~2h)

1. UserProfile / PortfolioItem / SkillBadge 模型 + migration
2. Username 注册 + 保留名校验
3. 个人资料 CRUD API
4. 公开个人页 API (无需认证)

### Phase 2: 作品管理 (~2.5h)

5. 从提交发布作品流程
6. 独立作品创建
7. 封面图上传 (MinIO)
8. 作品排序/置顶
9. 可见性控制

### Phase 3: 公开页前端 (~3h)

10. 公开个人页 (SSR)
11. 作品卡片组件
12. 技能徽章展示
13. SEO meta tags + JSON-LD
14. Sitemap 生成

### Phase 4: 管理界面 (~2h)

15. 作品集管理仪表板
16. 个人资料编辑页
17. 技能徽章管理
18. 作品编辑/删除

---

## 新增依赖

```
无新增依赖 — 使用 Next.js 内置的 Metadata API + SSR
```

---

## ADR 元数据

- **Status**: Proposed
- **Decision**: Path-based public profiles (/u/username), SSR for SEO, submission-to-portfolio publish flow, denormalized org/project names for resilience
- **Context**: Education platform needs verifiable portfolio — not just self-reported skills, but training outcomes with scores. Must work after students leave organizations.
- **Consequences**: Denormalized fields (source_org_name, source_project) need sync strategy for name changes (or accept snapshot-at-publish). SSR public pages increase server load vs static generation. Username changes need redirect handling.

---

*ADR-007 v1 — 作品集与公开页完整设计。*
