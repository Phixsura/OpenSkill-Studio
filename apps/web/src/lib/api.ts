const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

// Default fetch timeout (30 seconds)
const FETCH_TIMEOUT_MS = 30_000;

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
 * Safely parse JSON from a response. Throws ApiError on parse failure.
 */
async function safeJson<T>(res: Response): Promise<T> {
  try {
    return await res.json();
  } catch {
    throw new ApiError(res.status, "PARSE_ERROR", "Server returned invalid JSON");
  }
}

/**
 * Wrap a fetch call with timeout and network error handling.
 */
async function safeFetch(url: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, {
      ...init,
      signal: init?.signal ?? AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      throw new ApiError(0, "TIMEOUT", "Request timed out");
    }
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError(0, "ABORTED", "Request was aborted");
    }
    throw new ApiError(0, "NETWORK_ERROR", "Unable to reach the server");
  }
}

/**
 * Unauthenticated API client — for public endpoints (login, register, health).
 */
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await safeFetch(`${API_BASE}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
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
  return safeJson<T>(res);
}

// ── Authenticated API client ────────────────────────────────

let refreshPromise: Promise<string> | null = null;

/** Redirect to login only from protected routes — public pages (registry,
 * certificates) may probe auth without a session and must not bounce
 * anonymous visitors to /login. */
function redirectToLoginIfProtected(): void {
  if (typeof window === "undefined") return;
  const path = window.location.pathname;
  if (path.startsWith("/dashboard")) {
    window.location.href = `/login?redirect=${encodeURIComponent(path)}`;
  }
}

async function refreshAccessToken(): Promise<string> {
  const { useAuthStore } = await import("@/stores/auth");

  let res: Response;
  try {
    // safeFetch (not bare fetch): without the 30s timeout a hung /auth/refresh
    // leaves sharedRefresh permanently unsettled — logout and the on-mount
    // refresh both await it forever.
    res = await safeFetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    // Network error or timeout during refresh — clear auth and redirect
    useAuthStore.getState().clearAuth();
    redirectToLoginIfProtected();
    throw new ApiError(0, "NETWORK_ERROR", "Network error during token refresh");
  }

  if (!res.ok) {
    useAuthStore.getState().clearAuth();
    redirectToLoginIfProtected();
    throw new ApiError(401, "SESSION_EXPIRED", "Please log in again");
  }

  const data = await res.json();
  const token = data.access_token;
  const user = data.user;

  // Validate refresh response before trusting it
  if (!token || typeof token !== "string" || !user) {
    useAuthStore.getState().clearAuth();
    redirectToLoginIfProtected();
    throw new ApiError(401, "INVALID_REFRESH", "Refresh response missing token or user");
  }

  useAuthStore.getState().setAuth(token, user);
  return token;
}

/**
 * Shared, deduplicated token refresh. All refresh paths (AuthInitializer on
 * mount, apiWithAuth on 401) MUST go through this: refresh tokens rotate on
 * use, so two concurrent raw refresh calls race — the loser presents the
 * just-revoked token, gets 401, and wrongly clears the session.
 */
export function sharedRefresh(): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
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
    safeFetch(`${API_BASE}/api/v1${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(t ? { Authorization: `Bearer ${t}` } : {}),
        ...init?.headers,
      },
      credentials: "include",
    });

  let res = await doFetch(token);

  // 401 → try refresh (dedup: concurrent requests share one refresh promise).
  // Also attempt when token is null: on a hard reload the in-memory store is
  // empty but the browser may hold a valid refresh cookie — skipping refresh
  // here caused permanent 401s on deep links (queries fired before
  // AuthInitializer completed and never retried).
  if (res.status === 401) {
    token = await sharedRefresh();
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
  return safeJson<T>(res);
}
