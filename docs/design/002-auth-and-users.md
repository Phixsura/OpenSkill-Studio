# OpenSkill Studio — 认证与用户系统设计 (ADR-002)

> 对标 Cal.com / Plane.so / Documenso / Twenty CRM / Formbricks / Supabase
>
> Status: **Proposed** | Author: Lyphixia Wang | Date: 2026-08-13
> Depends on: ADR-001 (Bootstrap)

---

## 目录

1. [设计目标](#1-设计目标)
2. [行业对标分析](#2-行业对标分析)
3. [认证架构决策](#3-认证架构决策)
4. [数据模型](#4-数据模型)
5. [注册与登录流程](#5-注册与登录流程)
6. [JWT 令牌设计](#6-jwt-令牌设计)
7. [密码安全](#7-密码安全)
8. [OAuth 社交登录](#8-oauth-社交登录)
9. [邮箱验证与密码重置](#9-邮箱验证与密码重置)
10. [RBAC 权限体系](#10-rbac-权限体系)
11. [API 端点设计](#11-api-端点设计)
12. [中间件与依赖注入](#12-中间件与依赖注入)
13. [前端认证流程](#13-前端认证流程)
14. [会话管理与安全](#14-会话管理与安全)
15. [限流与防暴力破解](#15-限流与防暴力破解)
16. [测试策略](#16-测试策略)
17. [验收标准](#17-验收标准)
18. [实施计划](#18-实施计划)

---

## 1. 设计目标

### 1.1 核心目标

- **安全优先** — 遵循 OWASP 认证最佳实践，密码 bcrypt 哈希，JWT 短期有效
- **角色分层** — 支持 admin / instructor / student 三级角色，为多租户预留
- **社交登录预留** — Day 1 实现邮箱/密码，架构预留 OAuth (GitHub / Google)
- **开发者友好** — 清晰的 API 设计，前端 hooks 封装，统一的错误码

### 1.2 边界

| 包含 | 不包含 (后续 ADR) |
|------|-----------------|
| 邮箱/密码注册登录 | 组织/多租户 (ADR-003) |
| JWT access + refresh token | 第三方 API key 管理 |
| RBAC 角色 (admin/instructor/student) | 细粒度权限 (resource-level) |
| 邮箱验证 | MFA / Passkeys |
| 密码重置 | SSO / SAML |
| GitHub/Google OAuth 预留 | 支付/订阅 |
| 用户资料管理 | 头像上传 (依赖 ADR-005 文件上传) |

---

## 2. 行业对标分析

### 2.1 认证方案对比

| 维度 | Cal.com | Plane.so | Documenso | Twenty CRM | Formbricks | Supabase |
|------|---------|----------|-----------|------------|------------|----------|
| 认证方案 | 自研 | 自研 (Django) | Arctic + Passkeys | 自研 (JWT) | NextAuth.js | GoTrue (Go) |
| Token 类型 | JWT | Session | JWT + cookie | JWT (access+refresh) | Session (NextAuth) | JWT (access+refresh) |
| 密码哈希 | bcrypt | Django PBKDF2 | bcrypt | bcrypt | NextAuth | bcrypt |
| OAuth 支持 | Google, SAML | Google, GitHub | Google, GitHub, OIDC | Google, Microsoft | Google, GitHub, Azure | 30+ providers |
| MFA | TOTP | — | Passkeys | — | — | TOTP, SMS |
| 角色模型 | Team-based RBAC | Workspace roles | Document-level | Workspace roles | Environment RBAC | RLS policies |
| Session 存储 | DB | DB (Django) | DB | Redis | DB (NextAuth) | JWT stateless |
| Refresh 机制 | — | — | Cookie rotation | Redis + rotation | NextAuth built-in | Refresh token |

### 2.2 行业共识

| 共识 | 覆盖率 | OpenSkill Studio |
|------|--------|-----------------|
| bcrypt / PBKDF2 密码哈希 | 6/6 | ✅ bcrypt |
| JWT 或 Session-based 认证 | 6/6 | ✅ JWT (access + refresh) |
| OAuth 社交登录 | 6/6 | ✅ GitHub + Google |
| 基于角色的访问控制 | 6/6 | ✅ RBAC (admin/instructor/student) |
| 邮箱验证 | 5/6 | ✅ 可选 (开发环境跳过) |
| HTTPS only cookies | 5/6 | ✅ Refresh token in httpOnly cookie |

### 2.3 OpenSkill Studio 的特殊考量

与 SaaS/CRM 不同，教育平台有独特需求：

- **批量创建学员** — instructor 需要批量邀请学生，不能只靠自注册
- **角色不可自选** — 学生不能自行升级为 instructor
- **组织上下文** — 用户可属于多个组织（班级），但角色 per-org（ADR-003 处理）
- **低摩擦注册** — 学生可能技术背景弱，注册流程要简单
- **日后 AI 评估身份** — 需要可靠的用户身份关联提交物

---

## 3. 认证架构决策

### 3.1 为什么自研而不是 NextAuth / GoTrue?

| 选项 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **自研 (FastAPI)** | 完全控制、Python 生态一致、无外部依赖 | 需自行实现安全细节 | ✅ 选择 |
| NextAuth.js | 开箱即用 | 绑定 Next.js、与 FastAPI 割裂、Session 模型与 JWT 不匹配 | ❌ |
| Supabase GoTrue | 功能丰富 | Go 服务，运维复杂度增加、与自有 FastAPI 栈不一致 | ❌ |
| Keycloak | 企业级 SSO | 太重 (Java)、启动慢、开发体验差 | ❌ |

**理由**：Cal.com、Plane、Twenty 均选择自研，证明中等规模项目自研认证完全可行。OpenSkill Studio 后端是 Python/FastAPI，在同一栈内实现认证最简洁。

### 3.2 Token 策略: JWT (Access + Refresh)

```
┌──────────┐     POST /auth/login      ┌──────────┐
│  Client  │ ─────────────────────────▶ │  FastAPI │
│ (Next.js)│                            │          │
│          │ ◀───────────────────────── │          │
│          │  { access_token }          │          │
│          │  + Set-Cookie: refresh     │          │
│          │    (httpOnly, secure)      │          │
└──────┬───┘                            └────┬─────┘
       │                                     │
       │  Authorization: Bearer <access>     │
       │ ──────────────────────────────────▶  │
       │                                     │
       │  401 Expired                        │
       │ ◀──────────────────────────────────  │
       │                                     │
       │  POST /auth/refresh                 │
       │  Cookie: refresh=<token>            │
       │ ──────────────────────────────────▶  │
       │                                     │
       │  { new_access_token }               │
       │  + Set-Cookie: new_refresh          │
       │ ◀──────────────────────────────────  │
```

| 令牌 | 存储位置 | 有效期 | 用途 |
|------|---------|--------|------|
| Access Token | 前端内存 (JS 变量) | 15 分钟 | API 请求认证 |
| Refresh Token | httpOnly + Secure + SameSite cookie | 7 天 | 静默续期 access token |

**为什么 access token 不放 cookie?**
- 避免 CSRF 攻击面 — Bearer token 不会被浏览器自动附加
- 前端可以精确控制哪些请求带 token

**为什么 refresh token 放 httpOnly cookie?**
- 防止 XSS 窃取 — JavaScript 无法读取 httpOnly cookie
- 自动随请求发送到 `/auth/refresh` 端点

---

## 4. 数据模型

### 4.1 ER 图

```
┌─────────────────────────────────────────────────────┐
│                       users                          │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ email           VARCHAR(255)   UNIQUE, NOT NULL       │
│ email_verified  BOOLEAN        DEFAULT false          │
│ password_hash   VARCHAR(255)   NULL (OAuth 用户无密码) │
│ display_name    VARCHAR(100)   NOT NULL               │
│ avatar_url      TEXT           NULL                   │
│ role            user_role      DEFAULT 'student'      │
│ status          user_status    DEFAULT 'active'       │
│ last_login_at   TIMESTAMPTZ    NULL                   │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
│ updated_at      TIMESTAMPTZ    DEFAULT now()          │
└───────┬─────────────────────────────────────────────┘
        │ 1
        │
        │ N
┌───────┴─────────────────────────────────────────────┐
│                  oauth_accounts                      │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ user_id         ULID           FK → users.id         │
│ provider        VARCHAR(50)    NOT NULL (github/google)│
│ provider_id     VARCHAR(255)   NOT NULL               │
│ provider_email  VARCHAR(255)   NULL                   │
│ access_token    TEXT           NULL (加密存储)         │
│ refresh_token   TEXT           NULL (加密存储)         │
│ token_expires_at TIMESTAMPTZ   NULL                   │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
│ updated_at      TIMESTAMPTZ    DEFAULT now()          │
├─────────────────────────────────────────────────────┤
│ UNIQUE (provider, provider_id)                       │
└─────────────────────────────────────────────────────┘

        │ 1
        │
        │ N
┌───────┴─────────────────────────────────────────────┐
│                 refresh_tokens                       │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ user_id         ULID           FK → users.id         │
│ token_hash      VARCHAR(255)   UNIQUE, NOT NULL       │
│ device_info     VARCHAR(255)   NULL                   │
│ ip_address      VARCHAR(45)    NULL                   │
│ expires_at      TIMESTAMPTZ    NOT NULL               │
│ revoked_at      TIMESTAMPTZ    NULL                   │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
├─────────────────────────────────────────────────────┤
│ INDEX (user_id, revoked_at)  -- 查询未撤销的 tokens   │
│ INDEX (expires_at)           -- 定期清理过期 tokens    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              email_verification_tokens                │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ user_id         ULID           FK → users.id         │
│ token_hash      VARCHAR(255)   UNIQUE, NOT NULL       │
│ expires_at      TIMESTAMPTZ    NOT NULL               │
│ used_at         TIMESTAMPTZ    NULL                   │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              password_reset_tokens                    │
├─────────────────────────────────────────────────────┤
│ id              ULID           PK                    │
│ user_id         ULID           FK → users.id         │
│ token_hash      VARCHAR(255)   UNIQUE, NOT NULL       │
│ expires_at      TIMESTAMPTZ    NOT NULL               │
│ used_at         TIMESTAMPTZ    NULL                   │
│ created_at      TIMESTAMPTZ    DEFAULT now()          │
└─────────────────────────────────────────────────────┘
```

### 4.2 枚举类型

```sql
CREATE TYPE user_role AS ENUM ('admin', 'instructor', 'student');
CREATE TYPE user_status AS ENUM ('active', 'suspended', 'deleted');
```

### 4.3 SQLAlchemy 模型

```python
# app/models/user.py
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, ulid_pk


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = ulid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.STUDENT
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"), default=UserStatus.ACTIVE
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    @property
    def has_password(self) -> bool:
        return self.password_hash is not None
```

### 4.4 Base 模型 + ULID 主键

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ulid import ULID


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类."""
    pass


def ulid_pk() -> Mapped[str]:
    """ULID 主键 — 有序、URL 友好、无中心生成器."""
    return mapped_column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
```

**为什么 ULID 而不是 UUID?**
- **有序** — 按时间排序，B-tree 索引友好，避免页分裂
- **可读** — 26 字符 Crockford Base32，比 UUID 短
- **无中心** — 无需数据库 sequence，应用层生成
- 对标: Twenty CRM 使用 ULID

---

## 5. 注册与登录流程

### 5.1 注册流程

```
Client                           FastAPI                         PostgreSQL
  │                                │                                │
  │  POST /auth/register           │                                │
  │  { email, password,            │                                │
  │    display_name }              │                                │
  │ ──────────────────────────────▶│                                │
  │                                │                                │
  │                                │  1. 验证输入 (Pydantic)         │
  │                                │  2. 检查 email 唯一性           │
  │                                │  ────────────────────────────▶ │
  │                                │  ◀──────────────────────────── │
  │                                │  3. bcrypt hash password       │
  │                                │  4. 生成 ULID                  │
  │                                │  5. INSERT user                │
  │                                │  ────────────────────────────▶ │
  │                                │  6. 生成邮箱验证 token          │
  │                                │  7. 发送验证邮件 (异步)         │
  │                                │  8. 生成 JWT pair              │
  │                                │                                │
  │  201 Created                   │                                │
  │  { access_token, user }        │                                │
  │  Set-Cookie: refresh_token     │                                │
  │ ◀──────────────────────────────│                                │
```

```python
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, AuthResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.register(
        email=body.email,
        password=body.password,
        display_name=body.display_name,
    )

    # Refresh token → httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,          # 生产 HTTPS only
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/api/v1/auth",  # 仅认证端点可访问
    )

    return AuthResponse(
        access_token=result.access_token,
        token_type="bearer",
        expires_in=900,  # 15 min
        user=result.user,
    )
```

### 5.2 登录流程

```python
@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.login(email=body.email, password=body.password)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/api/v1/auth",
    )

    return AuthResponse(
        access_token=result.access_token,
        token_type="bearer",
        expires_in=900,
        user=result.user,
    )
```

### 5.3 请求/响应 Schema

```python
# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Display name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Display name must not exceed 100 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    email_verified: bool
    display_name: str
    avatar_url: str | None
    role: str
    created_at: str

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
```

---

## 6. JWT 令牌设计

### 6.1 令牌结构

```python
# Access Token payload
{
    "sub": "01JKXYZ...",        # user.id (ULID)
    "email": "user@example.com",
    "role": "student",
    "type": "access",
    "iat": 1723529400,
    "exp": 1723530300,          # iat + 15 min
    "jti": "01JKXYZ..."        # 唯一 token ID (用于撤销)
}

# Refresh Token payload
{
    "sub": "01JKXYZ...",
    "type": "refresh",
    "iat": 1723529400,
    "exp": 1724134200,          # iat + 7 days
    "jti": "01JKXYZ..."
}
```

### 6.2 令牌服务

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from ulid import ULID

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Password ─────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ──────────────────────────────────────────────

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: str, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": str(ULID()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """返回 (raw_token, token_jti) — jti 用于存储到 DB."""
    now = datetime.now(timezone.utc)
    jti = str(ULID())
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "jti": jti,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM), jti


def decode_token(token: str) -> dict:
    """解码并验证 JWT. 过期/无效抛出异常."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
```

### 6.3 Refresh Token 轮转 (Rotation)

```
Client                FastAPI              DB (refresh_tokens)
  │                     │                       │
  │ POST /auth/refresh  │                       │
  │ Cookie: old_refresh │                       │
  │ ───────────────────▶│                       │
  │                     │  1. decode old token  │
  │                     │  2. lookup by jti     │
  │                     │  ────────────────────▶│
  │                     │                       │
  │                     │  3. check: not revoked│
  │                     │     + not expired     │
  │                     │                       │
  │                     │  4. REVOKE old token  │
  │                     │  ────────────────────▶│
  │                     │                       │
  │                     │  5. create NEW pair   │
  │                     │  6. INSERT new refresh│
  │                     │  ────────────────────▶│
  │                     │                       │
  │ { new_access }      │                       │
  │ Set-Cookie: new_ref │                       │
  │ ◀───────────────────│                       │
```

**安全要点**:
- 每次 refresh 都发新的 refresh token（轮转），旧的立即撤销
- 如果检测到已撤销的 refresh token 被再次使用 → **令牌泄露**，立即撤销该用户的所有 refresh tokens
- 对标 Supabase GoTrue 的 rotation 策略

```python
# app/services/auth.py (refresh 部分)
async def refresh_tokens(self, old_refresh_token: str) -> TokenPair:
    payload = decode_token(old_refresh_token)
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Not a refresh token")

    jti = payload["jti"]
    user_id = payload["sub"]

    # 查找 token 记录
    token_record = await self._get_refresh_token(jti)

    if token_record is None:
        # Token 不存在 — 可能已被清理
        raise InvalidTokenError("Token not found")

    if token_record.revoked_at is not None:
        # ⚠️ 已撤销的 token 被重用 → 可能泄露
        # 撤销该用户所有 refresh tokens (安全措施)
        await self._revoke_all_user_tokens(user_id)
        raise TokenReuseError("Possible token theft detected")

    # 撤销旧 token
    await self._revoke_refresh_token(jti)

    # 生成新 token pair
    user = await self._get_user(user_id)
    return await self._create_token_pair(user)
```

---

## 7. 密码安全

### 7.1 策略

| 维度 | 策略 | 理由 |
|------|------|------|
| 哈希算法 | bcrypt (cost=12) | OWASP 推荐，GPU 抗性好 |
| 最小长度 | 8 字符 | NIST SP 800-63B 建议 |
| 最大长度 | 128 字符 | 防 bcrypt DoS (超长输入) |
| 复杂度 | ≥1 大写 + ≥1 数字 | 平衡安全性与用户体验 |
| 常见密码检查 | 前 10,000 常见密码黑名单 | OWASP 建议 |
| 存储 | 仅存 hash，原文不落盘不日志 | 标准实践 |

### 7.2 密码变更

```python
@router.post("/change-password", status_code=204)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.change_password(
        user=current_user,
        old_password=body.old_password,
        new_password=body.new_password,
    )
    # 变更密码后撤销所有 refresh tokens (强制重新登录)
    await service.revoke_all_user_tokens(current_user.id)
```

---

## 8. OAuth 社交登录

### 8.1 架构 (Phase 2 实现)

```
┌──────────┐    /auth/oauth/github     ┌──────────┐     ┌──────────┐
│  Client  │ ─────────────────────────▶│ FastAPI  │────▶│ GitHub   │
│          │                           │          │     │ OAuth    │
│          │ ◀─── 302 redirect ────────│          │     │          │
│          │                           │          │     │          │
│          │ ─── callback with code ──▶│          │◀────│          │
│          │                           │          │     │          │
│          │ ◀─── { access_token }  ───│          │     │          │
│          │      + Set-Cookie: ref    │          │     │          │
└──────────┘                           └──────────┘     └──────────┘
```

### 8.2 OAuth 账户关联规则

| 场景 | 行为 |
|------|------|
| 新 provider_id，邮箱匹配已有用户 | 关联到已有用户 (email_verified 为 true 时) |
| 新 provider_id，无匹配邮箱 | 创建新用户 + 关联 OAuth |
| 已关联的 provider_id | 直接登录 |
| 用户手动解绑 OAuth | 必须有密码或至少一个其他 OAuth 才能解绑 |

### 8.3 依赖选型

```toml
# Phase 2 新增依赖
[project.optional-dependencies]
oauth = [
    "httpx>=0.28",       # OAuth 回调请求 (已在 dev 依赖中)
    "authlib>=1.4",      # OAuth 2.0 / OIDC 客户端
]
```

**为什么 authlib?**
- Python OAuth 事实标准（2.1k+ stars）
- 支持 OAuth 2.0 + OIDC
- 异步支持 (httpx backend)
- 对标: Documenso 使用 Arctic (JS 等价库)

### 8.4 OAuth 配置

```python
# app/config.py (新增)
class Settings(BaseSettings):
    # ... existing fields ...

    # OAuth (Phase 2)
    github_client_id: str = ""
    github_client_secret: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    oauth_redirect_base: str = "http://localhost:3000"
```

---

## 9. 邮箱验证与密码重置

### 9.1 邮箱验证流程

```
注册 ──▶ 发送验证邮件 ──▶ 用户点击链接 ──▶ GET /auth/verify-email?token=xxx
                                              │
                                              ▼
                                         验证 token
                                         设置 email_verified = true
                                         重定向到前端 /login?verified=true
```

**开发环境**:
- `APP_ENV=development` 时跳过邮箱验证
- 验证 token 直接打印到控制台日志

**生产环境**:
- 集成邮件服务 (Resend / AWS SES) — Phase 2+
- Token 有效期: 24 小时
- 一次性使用

### 9.2 密码重置流程

```
POST /auth/forgot-password { email }
  │
  ├── 用户存在 → 生成 token，发送重置邮件
  └── 用户不存在 → 返回相同的 200 (防枚举)

GET /auth/reset-password?token=xxx
  → 前端展示新密码表单

POST /auth/reset-password { token, new_password }
  → 验证 token，更新密码，撤销所有 refresh tokens
```

**安全要点**:
- 忘记密码接口**始终返回 200**，不暴露用户是否存在
- Token 使用 `secrets.token_urlsafe(32)` 生成，存储 SHA-256 hash
- Token 有效期: 1 小时
- 一次性使用

### 9.3 邮件服务抽象

```python
# app/core/email.py
import structlog
from abc import ABC, abstractmethod

log = structlog.get_logger()


class EmailSender(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, html: str) -> None: ...


class ConsoleEmailSender(EmailSender):
    """开发环境: 打印到控制台."""
    async def send(self, to: str, subject: str, html: str) -> None:
        log.info("email_sent", to=to, subject=subject, body_preview=html[:200])


class ResendEmailSender(EmailSender):
    """生产环境: Resend API (Phase 2+)."""
    async def send(self, to: str, subject: str, html: str) -> None:
        raise NotImplementedError("Resend integration not yet implemented")


def get_email_sender() -> EmailSender:
    from app.config import settings
    if settings.app_env == "development":
        return ConsoleEmailSender()
    return ResendEmailSender()
```

---

## 10. RBAC 权限体系

### 10.1 角色定义

```
admin
 ├── 管理所有用户
 ├── 创建/管理组织
 ├── 全局配置
 └── 查看全平台数据

instructor
 ├── 创建/管理技能和项目
 ├── 批量邀请学生
 ├── 审核提交物
 ├── 查看学员进度
 └── 管理自己的组织内资源

student
 ├── 浏览技能和项目
 ├── 提交作品
 ├── 查看个人进度
 └── 管理个人作品集
```

### 10.2 权限装饰器

```python
# app/api/deps.py
from functools import wraps
from fastapi import Depends, HTTPException
from app.models.user import User, UserRole


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 JWT 解析当前用户. 验证用户存在且状态为 active."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = await db.get(User, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


def require_role(*roles: UserRole):
    """角色检查依赖. 用法: Depends(require_role(UserRole.ADMIN))"""
    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.role.value}' does not have access"
            )
        return user
    return checker
```

### 10.3 使用示例

```python
# 仅 admin 可访问
@router.get("/admin/users", response_model=ListResponse[UserResponse])
async def list_all_users(
    user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    ...

# admin 或 instructor 可访问
@router.post("/skills", response_model=DataResponse[SkillResponse])
async def create_skill(
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTRUCTOR)),
    db: AsyncSession = Depends(get_db),
):
    ...

# 任何已认证用户可访问
@router.get("/me", response_model=DataResponse[UserResponse])
async def get_profile(
    user: User = Depends(get_current_user),
):
    ...
```

### 10.4 权限矩阵 (Phase 1 范围)

| 端点 | admin | instructor | student | 未认证 |
|------|-------|-----------|---------|--------|
| POST /auth/register | ✅ | ✅ | ✅ | ✅ |
| POST /auth/login | ✅ | ✅ | ✅ | ✅ |
| POST /auth/refresh | ✅ | ✅ | ✅ | ❌ |
| GET /auth/me | ✅ | ✅ | ✅ | ❌ |
| PUT /auth/me | ✅ | ✅ | ✅ | ❌ |
| POST /auth/change-password | ✅ | ✅ | ✅ | ❌ |
| GET /admin/users | ✅ | ❌ | ❌ | ❌ |
| PUT /admin/users/:id/role | ✅ | ❌ | ❌ | ❌ |
| DELETE /admin/users/:id | ✅ | ❌ | ❌ | ❌ |

### 10.5 多租户 RBAC 预留 (ADR-003)

Phase 1 使用全局角色 (`users.role`)。ADR-003 引入组织后，将扩展为：

```
users.role          → 全局角色 (admin / regular)
org_members.role    → 组织内角色 (owner / instructor / student)
```

数据模型已预留此扩展路径 — `User.role` 字段独立于未来的 `org_members` 表。

---

## 11. API 端点设计

### 11.1 完整端点列表

```
Auth (/api/v1/auth)
├── POST   /register              注册新用户
├── POST   /login                 邮箱/密码登录
├── POST   /logout                登出 (撤销 refresh token)
├── POST   /refresh               刷新 access token
├── GET    /me                    获取当前用户资料
├── PUT    /me                    更新用户资料
├── POST   /change-password       修改密码
├── POST   /forgot-password       请求密码重置
├── POST   /reset-password        重置密码 (带 token)
├── GET    /verify-email          验证邮箱 (带 token)
└── POST   /resend-verification   重发验证邮件

Admin (/api/v1/admin)  — Phase 1 基础版
├── GET    /users                 列出全部用户 (分页)
├── GET    /users/:id             获取用户详情
├── PUT    /users/:id/role        修改用户角色
└── DELETE /users/:id             软删除用户 (status → deleted)
```

### 11.2 响应示例

```json
// POST /api/v1/auth/register — 201
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "01JKXYZ...",
    "email": "alice@example.com",
    "email_verified": false,
    "display_name": "Alice",
    "avatar_url": null,
    "role": "student",
    "created_at": "2026-08-13T10:30:00Z"
  }
}

// POST /api/v1/auth/login — 400
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}

// POST /api/v1/auth/register — 409
{
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "An account with this email already exists"
  }
}
```

### 11.3 错误码枚举

```python
# app/exceptions.py (新增认证相关错误)
class AuthError:
    INVALID_CREDENTIALS = ("INVALID_CREDENTIALS", "Invalid email or password", 401)
    EMAIL_ALREADY_EXISTS = ("EMAIL_ALREADY_EXISTS", "An account with this email already exists", 409)
    TOKEN_EXPIRED = ("TOKEN_EXPIRED", "Token has expired", 401)
    TOKEN_INVALID = ("TOKEN_INVALID", "Invalid or malformed token", 401)
    TOKEN_REUSE = ("TOKEN_REUSE", "Possible token theft detected", 401)
    EMAIL_NOT_VERIFIED = ("EMAIL_NOT_VERIFIED", "Please verify your email address", 403)
    ACCOUNT_SUSPENDED = ("ACCOUNT_SUSPENDED", "Account has been suspended", 403)
    INSUFFICIENT_ROLE = ("INSUFFICIENT_ROLE", "Insufficient permissions", 403)
    WEAK_PASSWORD = ("WEAK_PASSWORD", "Password does not meet requirements", 422)
    RATE_LIMITED = ("RATE_LIMITED", "Too many requests, try again later", 429)
```

---

## 12. 中间件与依赖注入

### 12.1 认证中间件链

```
Request
  │
  ▼
RequestIDMiddleware        → 注入 X-Request-ID
  │
  ▼
LoggingMiddleware          → 记录请求日志
  │
  ▼
SecurityHeadersMiddleware  → 安全响应头
  │
  ▼
RateLimitMiddleware        → 限流 (新增, §15)
  │
  ▼
CORSMiddleware             → 跨域处理
  │
  ▼
Router
  │
  ├── 公开端点 (register, login, health)
  │     → 无认证检查
  │
  └── 受保护端点
        │
        ▼
      Depends(get_current_user)    → JWT 验证 + 用户加载
        │
        ▼
      Depends(require_role(...))   → 角色检查 (可选)
```

### 12.2 OAuth2 Bearer Scheme

```python
# app/api/deps.py
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True,
)

# 可选认证 (不强制)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """可选认证: 未登录返回 None，已登录返回用户."""
    if token is None:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
```

---

## 13. 前端认证流程

### 13.1 认证状态管理

```typescript
// lib/auth.ts
import { create } from "zustand";

interface AuthState {
  accessToken: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: UserResponse) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  isAuthenticated: false,
  setAuth: (token, user) =>
    set({ accessToken: token, user, isAuthenticated: true }),
  clearAuth: () =>
    set({ accessToken: null, user: null, isAuthenticated: false }),
}));
```

**为什么 Zustand 而不是 Context?**
- 不触发全组件树重渲染
- 支持 selector — 只订阅需要的字段
- 极轻量 (1.1 KB)
- 对标: Cal.com (Zustand), Twenty (Recoil → Jotai)

### 13.2 API 客户端拦截器 (自动 refresh)

```typescript
// lib/api.ts (增强版)
import { useAuthStore } from "./auth";

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const res = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    credentials: "include", // 发送 httpOnly cookie
  });

  if (!res.ok) {
    useAuthStore.getState().clearAuth();
    throw new ApiError(401, "SESSION_EXPIRED", "Please log in again");
  }

  const data = await res.json();
  useAuthStore.getState().setAuth(data.access_token, data.user);
  return data.access_token;
}

export async function apiWithAuth<T>(path: string, init?: RequestInit): Promise<T> {
  let token = useAuthStore.getState().accessToken;

  const doFetch = (t: string | null) =>
    fetch(`/api/v1${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(t ? { Authorization: `Bearer ${t}` } : {}),
        ...init?.headers,
      },
    });

  let res = await doFetch(token);

  // 401 → 尝试 refresh (去重: 并发请求共享同一个 refresh promise)
  if (res.status === 401 && token) {
    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
    }
    token = await refreshPromise;
    res = await doFetch(token);
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      res.status,
      body?.error?.code ?? "UNKNOWN",
      body?.error?.message ?? `HTTP ${res.status}`,
    );
  }

  return res.json();
}
```

### 13.3 前端路由守卫

```typescript
// middleware.ts (Next.js middleware)
import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/", "/login", "/register", "/forgot-password", "/reset-password", "/health"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 公开页面放行
  if (PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith("/api/"))) {
    return NextResponse.next();
  }

  // 检查 refresh token cookie (存在即可 — 实际验证由 API 处理)
  const hasRefreshToken = request.cookies.has("refresh_token");

  if (!hasRefreshToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|og-image.png).*)"],
};
```

### 13.4 登录页面

```tsx
// app/(auth)/login/page.tsx
"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await api<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
        credentials: "include",
      });
      setAuth(data.access_token, data.user);
      router.push(searchParams.get("redirect") ?? "/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-bold">Log in to OpenSkill Studio</h1>

        {error && <p className="text-sm text-destructive">{error}</p>}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full rounded border px-3 py-2"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full rounded border px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Log in"}
        </button>
      </form>
    </main>
  );
}
```

---

## 14. 会话管理与安全

### 14.1 多设备管理

```python
# 用户可以查看活跃会话列表
@router.get("/sessions", response_model=DataResponse[list[SessionResponse]])
async def list_sessions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tokens = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .where(RefreshToken.revoked_at.is_(None))
        .where(RefreshToken.expires_at > func.now())
        .order_by(RefreshToken.created_at.desc())
    )
    return [SessionResponse.from_token(t) for t in tokens.scalars()]


# 撤销指定会话
@router.delete("/sessions/{token_id}", status_code=204)
async def revoke_session(
    token_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    token = await db.get(RefreshToken, token_id)
    if token is None or token.user_id != user.id:
        raise HTTPException(status_code=404)
    token.revoked_at = func.now()
    await db.commit()
```

### 14.2 安全事件日志

```python
# 关键认证事件记录 (structlog)
# 每个事件包含: user_id, ip, user_agent, request_id

log.info("auth_register", user_id=user.id, email=user.email)
log.info("auth_login", user_id=user.id, method="password")
log.warning("auth_login_failed", email=email, reason="invalid_password")
log.warning("auth_token_reuse", user_id=user_id, jti=jti)
log.info("auth_password_changed", user_id=user.id)
log.info("auth_logout", user_id=user.id)
log.info("auth_role_changed", user_id=target.id, old=old_role, new=new_role, by=admin.id)
```

### 14.3 登出

```python
@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 从 cookie 获取 refresh token 并撤销
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            await revoke_refresh_token(db, payload["jti"])
        except Exception:
            pass  # token 无效也没关系，重点是清除 cookie

    # 清除 cookie
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        httponly=True,
        secure=True,
        samesite="lax",
    )
```

---

## 15. 限流与防暴力破解

### 15.1 限流策略

| 端点 | 限制 | 窗口 | 维度 |
|------|------|------|------|
| POST /auth/login | 5 次 | 1 分钟 | 每 IP |
| POST /auth/register | 3 次 | 1 分钟 | 每 IP |
| POST /auth/forgot-password | 3 次 | 15 分钟 | 每邮箱 |
| POST /auth/refresh | 30 次 | 1 分钟 | 每用户 |
| 其他 API | 60 次 | 1 分钟 | 每用户 |

### 15.2 实现 (Redis 滑动窗口)

```python
# app/core/rate_limit.py
import time
from redis.asyncio import Redis
from app.core.redis import redis_pool


async def check_rate_limit(key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """
    Redis 滑动窗口限流.
    返回 (is_allowed, remaining_requests).
    """
    r: Redis = redis_pool()
    now = time.time()
    window_start = now - window_seconds
    pipe_key = f"ratelimit:{key}"

    async with r.pipeline(transaction=True) as pipe:
        # 移除窗口外的记录
        pipe.zremrangebyscore(pipe_key, 0, window_start)
        # 统计当前窗口内的请求数
        pipe.zcard(pipe_key)
        # 添加当前请求
        pipe.zadd(pipe_key, {str(now): now})
        # 设置 key 过期时间
        pipe.expire(pipe_key, window_seconds)
        results = await pipe.execute()

    current_count = results[1]
    allowed = current_count < limit
    remaining = max(0, limit - current_count - 1)

    return allowed, remaining
```

### 15.3 限流依赖注入

```python
# app/api/deps.py
from fastapi import Request, HTTPException

def rate_limit(limit: int, window: int, by: str = "ip"):
    """
    限流依赖.
    by: "ip" = 按客户端 IP, "user" = 按用户 ID
    """
    async def checker(request: Request):
        if by == "ip":
            key = f"{request.url.path}:{request.client.host}"
        else:
            user = await get_current_user(...)
            key = f"{request.url.path}:{user.id}"

        allowed, remaining = await check_rate_limit(key, limit, window)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(window)},
            )

        return remaining
    return checker


# 使用
@router.post("/login", dependencies=[Depends(rate_limit(5, 60, by="ip"))])
async def login(...): ...
```

### 15.4 账户锁定 (可选, Phase 2)

- 连续 10 次登录失败 → 锁定账户 30 分钟
- Redis key: `lockout:{user_id}` with TTL 1800s
- 锁定期间返回 `ACCOUNT_LOCKED` 错误 (不暴露 "密码错误")

---

## 16. 测试策略

### 16.1 测试矩阵

| 测试类型 | 覆盖内容 | 工具 |
|---------|---------|------|
| Unit | 密码哈希、JWT 生成/验证、Schema 验证 | pytest |
| Integration | 注册/登录/refresh/logout 端点 | httpx + TestClient |
| Security | SQL 注入、XSS、暴力破解 | pytest + 手动 |
| Frontend | 登录表单、认证状态、路由守卫 | Vitest + Testing Library |

### 16.2 后端测试用例

```python
# tests/test_auth.py

class TestRegister:
    async def test_register_success(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "alice@example.com",
            "password": "Alice123!",
            "display_name": "Alice",
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "alice@example.com"
        assert data["user"]["role"] == "student"

    async def test_register_duplicate_email(self, client):
        # 先注册
        await client.post("/api/v1/auth/register", json={...})
        # 重复注册
        response = await client.post("/api/v1/auth/register", json={...})
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    async def test_register_weak_password(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "bob@example.com",
            "password": "short",
            "display_name": "Bob",
        })
        assert response.status_code == 422

    async def test_register_invalid_email(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "Valid123!",
            "display_name": "Test",
        })
        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, client, registered_user):
        response = await client.post("/api/v1/auth/login", json={
            "email": "alice@example.com",
            "password": "Alice123!",
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.cookies

    async def test_login_wrong_password(self, client, registered_user):
        response = await client.post("/api/v1/auth/login", json={
            "email": "alice@example.com",
            "password": "WrongPass1!",
        })
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

    async def test_login_nonexistent_user(self, client):
        response = await client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "Whatever1!",
        })
        assert response.status_code == 401
        # 相同的错误码 — 不暴露用户是否存在
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


class TestRefresh:
    async def test_refresh_success(self, client, auth_cookies):
        response = await client.post("/api/v1/auth/refresh", cookies=auth_cookies)
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_refresh_revoked_token_triggers_theft_detection(self, client):
        # 使用同一个 refresh token 两次 → 第二次应失败 + 撤销全部
        ...


class TestProtectedRoutes:
    async def test_get_me_authenticated(self, client, access_token):
        response = await client.get("/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200

    async def test_get_me_no_token(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_admin_route_as_student(self, client, student_token):
        response = await client.get("/api/v1/admin/users",
            headers={"Authorization": f"Bearer {student_token}"})
        assert response.status_code == 403
```

---

## 17. 验收标准

| # | 验收项 | 方案章节 |
|---|--------|---------|
| 1 | 用户可通过邮箱/密码注册 | §5.1 |
| 2 | 用户可通过邮箱/密码登录 | §5.2 |
| 3 | JWT access + refresh token 正常工作 | §6 |
| 4 | Access token 过期后可通过 refresh 续期 | §6.3 |
| 5 | Refresh token 使用轮转策略 | §6.3 |
| 6 | 密码使用 bcrypt 哈希存储 | §7 |
| 7 | RBAC 角色 (admin/instructor/student) 可控制端点访问 | §10 |
| 8 | 登出正确清除 refresh token | §14.3 |
| 9 | 认证相关端点有限流保护 | §15 |
| 10 | 密码重置流程不暴露用户是否存在 | §9.2 |
| 11 | 前端登录/注册页面可用 | §13.4 |
| 12 | 前端 API 客户端自动处理 token refresh | §13.2 |
| 13 | 前端路由守卫保护受保护页面 | §13.3 |
| 14 | 全部认证端点有测试覆盖 | §16 |

---

## 18. 实施计划

### Phase 1: 核心认证 (~3h)

1. 创建 User / RefreshToken 数据模型 + Alembic migration
2. 实现密码哈希 + JWT 生成/验证 (`core/security.py`)
3. 实现 AuthService (register, login, refresh, logout)
4. 实现认证端点 (register, login, refresh, logout, me)
5. 实现 `get_current_user` + `require_role` 依赖

### Phase 2: 安全加固 (~2h)

6. Redis 滑动窗口限流
7. 密码重置流程 (ConsoleEmailSender 开发环境)
8. 邮箱验证流程
9. Refresh token 轮转 + 泄露检测
10. 安全事件日志

### Phase 3: 前端认证 (~2h)

11. Zustand 认证状态管理
12. API 客户端拦截器 (自动 refresh)
13. 登录/注册页面
14. Next.js middleware 路由守卫
15. 认证 layout (`(auth)` route group)

### Phase 4: Admin + 测试 (~1.5h)

16. Admin 用户管理端点 (list, get, update role, soft delete)
17. 后端测试 (register, login, refresh, RBAC)
18. 前端测试 (表单, 认证状态)

### Phase 5: OAuth 预置 (~1h, 可延后)

19. OAuth 数据模型 (oauth_accounts 表)
20. GitHub OAuth 流程
21. Google OAuth 流程
22. 账户关联/解绑逻辑

---

## 新增依赖 (相对 ADR-001)

### 后端 (pyproject.toml)

```toml
[project]
dependencies = [
    # ... ADR-001 existing ...
    "pyjwt>=2.9",               # JWT 编解码
    "passlib[bcrypt]>=1.7",     # 密码哈希 (bcrypt 后端)
    "pydantic[email]>=2.0",     # EmailStr 验证
]
```

### 前端 (package.json)

```json
{
  "dependencies": {
    "zustand": "^5"              // 认证状态管理
  }
}
```

---

## ADR 元数据

- **Status**: Proposed
- **Decision**: Self-hosted JWT (access + refresh) auth with bcrypt, RBAC (admin/instructor/student), Redis rate limiting
- **Context**: Education platform needs low-friction registration, batch student invites (ADR-003), and reliable identity for AI evaluation (ADR-006)
- **Consequences**: No external auth dependency (full control); must carefully implement OWASP best practices (token rotation, password hashing, rate limiting). OAuth is deferred but architecturally pre-wired.

---

*ADR-002 v1 — 认证与用户系统完整设计。*
