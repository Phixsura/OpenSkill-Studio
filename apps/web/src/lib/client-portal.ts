"use client";

import { ApiError } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

/** Client-portal fetch: uses the sessionStorage guest JWT (or a member access
 * token when logged in). Deliberately separate from apiWithAuth — the portal
 * must never trigger product-side refresh flows. */
export async function portalApi<T>(path: string, init?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? sessionStorage.getItem("client_portal_jwt") : null;
  const res = await fetch(`${API_BASE}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      res.status,
      body?.error?.code ?? "UNKNOWN",
      body?.error?.message ?? `HTTP ${res.status}`,
    );
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export function portalRole(): string | null {
  return typeof window !== "undefined" ? sessionStorage.getItem("client_portal_role") : null;
}

export function portalLabel(): string | null {
  return typeof window !== "undefined" ? sessionStorage.getItem("client_portal_label") : null;
}
