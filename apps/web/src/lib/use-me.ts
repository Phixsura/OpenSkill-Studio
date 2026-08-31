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
