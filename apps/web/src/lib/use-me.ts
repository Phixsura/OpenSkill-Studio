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
