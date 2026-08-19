const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Unauthenticated API client — for public endpoints (login, register, health).
 */
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api/v1${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
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

// ── Authenticated API client ────────────────────────────────

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const { useAuthStore } = await import("@/stores/auth");

  const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  if (!res.ok) {
    useAuthStore.getState().clearAuth();
    // Redirect to login — session expired
    if (typeof window !== "undefined") {
      const current = window.location.pathname;
      window.location.href = `/login?redirect=${encodeURIComponent(current)}`;
    }
    throw new ApiError(401, "SESSION_EXPIRED", "Please log in again");
  }

  const data = await res.json();
  useAuthStore.getState().setAuth(data.access_token, data.user);
  return data.access_token;
}

/**
 * Authenticated API client — attaches Bearer token, auto-refreshes on 401.
 */
export async function apiWithAuth<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const { useAuthStore } = await import("@/stores/auth");
  let token = useAuthStore.getState().accessToken;

  const doFetch = (t: string | null) =>
    fetch(`${API_BASE}/api/v1${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(t ? { Authorization: `Bearer ${t}` } : {}),
        ...init?.headers,
      },
      credentials: "include",
    });

  let res = await doFetch(token);

  // 401 → try refresh (dedup: concurrent requests share one refresh promise)
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

  if (res.status === 204) return undefined as T;
  return res.json();
}
