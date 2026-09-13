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
  // R101[M15]: /platform and /partner live OUTSIDE the /dashboard URL prefix
  // (the (dashboard) route group is not part of the URL) — session expiry
  // there stranded users on a blank pane instead of bouncing to login.
  if (
    path.startsWith("/dashboard") ||
    path.startsWith("/platform") ||
    path.startsWith("/partner")
  ) {
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

/** R101[H11]: impersonation tokens carry an `imp` claim and have NO refresh
 * token — the browser's refresh cookie belongs to the SUPPORT OPERATOR's own
 * login. Auto-refreshing on 401 silently swapped the read-only impersonated
 * session for the operator's fully-privileged one. Detect the claim (base64
 * payload decode — no verification needed client-side) and end the session
 * instead of refreshing. */
function isImpersonationToken(token: string | null): boolean {
  if (!token) return false;
  try {
    const part = token.split(".")[1];
    if (!part) return false;
    const payload = JSON.parse(atob(part.replace(/-/g, "+").replace(/_/g, "/")));
    return Boolean(payload?.imp);
  } catch {
    return false;
  }
}

/**
 * Authenticated API client — attaches Bearer token, auto-refreshes on 401.
 */
export async function apiWithAuth<T>(path: string, init?: RequestInit): Promise<T> {
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
    if (isImpersonationToken(token)) {
      // R101[H11]: never refresh an expired impersonation session into the
      // operator's own privileged token — the impersonation window is over.
      const { useAuthStore: store } = await import("@/stores/auth");
      store.getState().clearAuth();
      redirectToLoginIfProtected();
      throw new ApiError(401, "IMPERSONATION_EXPIRED", "Impersonation session ended");
    }
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
