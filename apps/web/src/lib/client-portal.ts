"use client";

import { ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";
const FETCH_TIMEOUT_MS = 30_000;

/** R101[M1]: the portal token is EITHER a guest JWT (sessionStorage) or the
 * logged-in member's product access token — the backend's principal resolver
 * accepts both, but the old code only ever sent the guest JWT, making the
 * member channel unreachable from the UI. */
export function portalToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem("client_portal_jwt") ?? useAuthStore.getState().accessToken;
}

/** Client-portal fetch: guest JWT or member access token. Deliberately
 * separate from apiWithAuth — the portal must never trigger product-side
 * refresh flows. */
export async function portalApi<T>(path: string, init?: RequestInit): Promise<T> {
  const token = portalToken();
  let res: Response;
  try {
    // R101[L3]: bare fetch had no timeout, and network failures threw raw
    // TypeError past every `instanceof ApiError` handler (unhandled crash).
    res = await fetch(`${API_BASE}/api/v1${path}`, {
      ...init,
      signal: init?.signal ?? AbortSignal.timeout(FETCH_TIMEOUT_MS),
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init?.headers,
      },
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      throw new ApiError(0, "TIMEOUT", "Request timed out");
    }
    throw new ApiError(0, "NETWORK_ERROR", "Unable to reach the server");
  }
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
