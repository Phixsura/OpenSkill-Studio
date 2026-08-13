from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.organization import (
    AcceptInviteRequest,
    CreateInviteLinkRequest,
    CreateOrgRequest,
    InviteLinkResponse,
    InviteMembersRequest,
    InviteResponse,
    JoinByCodeRequest,
    OrgDetailResponse,
    OrgMemberResponse,
    OrgMemberUserResponse,
    OrgResponse,
    UpdateMemberRoleRequest,
    UpdateOrgRequest,
    UpdateOrgSettingsRequest,
)
from app.services.organization import OrgService

router = APIRouter(tags=["Organizations"])


# ── Helpers ───────────────────────────────────────────────




def _link_response(link, base_url: str = "http://localhost:3000") -> InviteLinkResponse:
    return InviteLinkResponse(
        id=link.id,
        code=link.code,
        url=f"{base_url}/join/{link.code}",
        role=link.role.value,
        max_uses=link.max_uses,
        use_count=link.use_count,
        expires_at=link.expires_at,
        is_active=link.is_active,
        created_at=link.created_at,
    )


async def _member_response(member, db: AsyncSession) -> OrgMemberResponse:
    user = await db.get(User, member.user_id)
    return OrgMemberResponse(
        id=member.id,
        user=OrgMemberUserResponse.model_validate(user) if user else OrgMemberUserResponse(
            id=member.user_id, email="", display_name="Unknown", avatar_url=None
        ),
        role=member.role.value,
        status=member.status.value,
        joined_at=member.joined_at,
    )


# ── Organization CRUD ────────────────────────────────────


@router.post("/orgs", response_model=DataResponse[OrgResponse], status_code=201)
async def create_org(
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
    await db.commit()

    count = await service.get_member_count(org.id)
    resp = OrgResponse(
        id=org.id, name=org.name, slug=org.slug, description=org.description,
        logo_url=org.logo_url, role="owner", member_count=count, created_at=org.created_at,
    )
    return DataResponse(data=resp)


@router.get("/orgs", response_model=DataResponse[list[OrgResponse]])
async def list_my_orgs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrgService(db)
    orgs = await service.get_user_orgs(user.id)
    items = [
        OrgResponse(
            id=o["org"].id, name=o["org"].name, slug=o["org"].slug,
            description=o["org"].description, logo_url=o["org"].logo_url,
            role=o["role"], member_count=o["member_count"], created_at=o["org"].created_at,
        )
        for o in orgs
    ]
    return DataResponse(data=items)


@router.get("/orgs/{org_id}", response_model=DataResponse[OrgDetailResponse])
async def get_org(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrgService(db)
    member = await require_org_member(org_id, user, db)
    org = await service.get_org(org_id)
    count = await service.get_member_count(org_id)

    resp = OrgDetailResponse(
        id=org.id, name=org.name, slug=org.slug, description=org.description,
        logo_url=org.logo_url, status=org.status.value, settings=org.settings or {},
        created_by=org.created_by, role=member.role.value, member_count=count,
        created_at=org.created_at,
    )
    return DataResponse(data=resp)


@router.put("/orgs/{org_id}", response_model=DataResponse[OrgResponse])
async def update_org(
    org_id: str,
    body: UpdateOrgRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    service = OrgService(db)
    org = await service.update_org(
        org_id, name=body.name, description=body.description, logo_url=body.logo_url
    )
    await db.commit()
    count = await service.get_member_count(org_id)

    resp = OrgResponse(
        id=org.id, name=org.name, slug=org.slug, description=org.description,
        logo_url=org.logo_url, member_count=count, created_at=org.created_at,
    )
    return DataResponse(data=resp)


@router.delete("/orgs/{org_id}", status_code=204)
async def delete_org(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrgService(db)
    await service.delete_org(org_id, user.id)
    await db.commit()


@router.put("/orgs/{org_id}/settings", response_model=DataResponse[OrgDetailResponse])
async def update_org_settings(
    org_id: str,
    body: UpdateOrgSettingsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    service = OrgService(db)
    org = await service.update_settings(org_id, body.settings)
    await db.commit()
    count = await service.get_member_count(org_id)
    member = await service._get_active_member(org_id, user.id)

    resp = OrgDetailResponse(
        id=org.id, name=org.name, slug=org.slug, description=org.description,
        logo_url=org.logo_url, status=org.status.value, settings=org.settings or {},
        created_by=org.created_by, role=member.role.value, member_count=count,
        created_at=org.created_at,
    )
    return DataResponse(data=resp)


# ── Members ──────────────────────────────────────────────


@router.get("/orgs/{org_id}/members", response_model=ListResponse[OrgMemberResponse])
async def list_members(
    org_id: str,
    page: int = 1,
    per_page: int = 20,
    role: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    service = OrgService(db)
    members, total = await service.get_members(org_id, page, per_page, role)

    items = [await _member_response(m, db) for m in members]
    return ListResponse(
        data=items,
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page,
            has_more=(page * per_page) < total,
        ),
    )


@router.put("/orgs/{org_id}/members/{user_id}")
async def update_member_role(
    org_id: str,
    user_id: str,
    body: UpdateMemberRoleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        new_role = OrgRole(body.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid role: {body.role}") from exc

    service = OrgService(db)
    member = await service.update_member_role(org_id, user_id, new_role, user.id)
    await db.commit()
    resp = await _member_response(member, db)
    return DataResponse(data=resp)


@router.delete("/orgs/{org_id}/members/{user_id}", status_code=204)
async def remove_member(
    org_id: str,
    user_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrgService(db)
    await service.remove_member(org_id, user_id, user.id)
    await db.commit()


# ── Invitations ──────────────────────────────────────────


@router.post("/orgs/{org_id}/invites", response_model=InviteResponse)
async def invite_members(
    org_id: str,
    body: InviteMembersRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    try:
        role = OrgRole(body.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid role: {body.role}") from exc

    service = OrgService(db)
    result = await service.invite_members(org_id, body.emails, role, user.id)
    await db.commit()
    return InviteResponse(
        invited=result.invited,
        already_member=result.already_member,
        already_invited=result.already_invited,
    )


@router.get("/orgs/{org_id}/invites")
async def list_invitations(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    service = OrgService(db)
    invites = await service.get_invitations(org_id)
    return DataResponse(data=[
        {"id": inv.id, "email": inv.email, "role": inv.role.value,
         "status": inv.status.value, "expires_at": inv.expires_at.isoformat(),
         "created_at": inv.created_at.isoformat()}
        for inv in invites
    ])


@router.delete("/orgs/{org_id}/invites/{invite_id}", status_code=204)
async def revoke_invite(
    org_id: str,
    invite_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    service = OrgService(db)
    await service.revoke_invitation(org_id, invite_id)
    await db.commit()


# ── Direct Member Add ────────────────────────────────────


@router.post("/orgs/{org_id}/members")
async def add_member_directly(
    org_id: str,
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Directly add an existing user to the org (admin+)."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    user_id = body.get("user_id")
    role_str = body.get("role", "student")
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id is required")
    try:
        role = OrgRole(role_str)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid role: {role_str}") from exc

    service = OrgService(db)
    member = await service.add_member(org_id, user_id, role, invited_by=user.id)
    await db.commit()
    resp = await _member_response(member, db)
    return DataResponse(data=resp)


# ── Invite Links ─────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/invite-links",
    response_model=DataResponse[InviteLinkResponse],
    status_code=201,
)
async def create_invite_link(
    org_id: str,
    body: CreateInviteLinkRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    try:
        role = OrgRole(body.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid role: {body.role}") from exc

    service = OrgService(db)
    link = await service.create_invite_link(org_id, role, body.max_uses, body.expires_in_days, user.id)
    await db.commit()
    return DataResponse(data=_link_response(link))


@router.get("/orgs/{org_id}/invite-links", response_model=DataResponse[list[InviteLinkResponse]])
async def list_invite_links(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    service = OrgService(db)
    links = await service.get_invite_links(org_id)
    return DataResponse(data=[_link_response(lnk) for lnk in links])


@router.put("/orgs/{org_id}/invite-links/{link_id}", response_model=DataResponse[InviteLinkResponse])
async def toggle_invite_link(
    org_id: str,
    link_id: str,
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    is_active = body.get("is_active", True)
    service = OrgService(db)
    link = await service.toggle_invite_link(org_id, link_id, is_active)
    await db.commit()
    return DataResponse(data=_link_response(link))


@router.delete("/orgs/{org_id}/invite-links/{link_id}", status_code=204)
async def delete_invite_link(
    org_id: str,
    link_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    service = OrgService(db)
    await service.delete_invite_link(org_id, link_id)
    await db.commit()


# ── Invite Actions (public-ish) ──────────────────────────


@router.post("/invites/accept")
async def accept_email_invite(
    body: AcceptInviteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrgService(db)
    member = await service.accept_email_invite(body.token, user.id)
    await db.commit()
    return {"message": "Invitation accepted", "org_id": member.org_id}


@router.post("/invites/join")
async def join_by_code(
    body: JoinByCodeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrgService(db)
    member = await service.join_by_code(body.code, user.id)
    await db.commit()
    return {"message": "Joined organization", "org_id": member.org_id}
