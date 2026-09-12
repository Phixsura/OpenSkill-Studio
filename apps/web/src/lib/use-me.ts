"use client";

import { useQuery } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";
import { type MeExtended } from "@/lib/cp";

/** Extended /auth/me: platform roles, tenant + partner memberships,
 * impersonation banner data. Drives role-conditional navigation. */
export function useMe() {
  return useQuery({
    queryKey: ["me-extended"],
    queryFn: () => apiWithAuth<{ data: MeExtended }>("/auth/me"),
    staleTime: 60_000,
  });
}

/** R101[M27]: impersonation sessions are read-only server-side (#27 §6), but
 * only the banner reflected that — every mutation button stayed enabled and
 * failed with a confusing 403 on click. Pages gate their write controls on
 * this hook instead. */
export function useImpersonation(): boolean {
  const { data } = useMe();
  return Boolean(data?.data?.impersonation);
}

/** R113[L6]: platform admins bypass tenant membership server-side
 * (require_tenant_member grants a virtual owner membership to UserRole.ADMIN
 * and platform_admin), but useTenantRole returns null for them — so every
 * owner-only control was hidden from the very admins allowed to use it. */
export function usePlatformAdmin(): boolean {
  const { data } = useMe();
  const me = data?.data;
  return me?.role === "admin" || (me?.platform_roles ?? []).includes("platform_admin");
}

/** R101[M30]: the tenant admin pages rendered owner-only mutations (cancel/
 * change subscription, member add/remove, domain ops, branding save) to
 * billing_admins, who got a 403 toast on every click. Resolve the caller's
 * role in ONE tenant so pages can gate the controls. */
export function useTenantRole(tenantId: string | null | undefined): string | null {
  const { data } = useMe();
  if (!tenantId) return null;
  const membership = data?.data?.tenant_memberships?.find(
    (m: { tenant_id: string; role: string }) => m.tenant_id === tenantId,
  );
  return membership?.role ?? null;
}
