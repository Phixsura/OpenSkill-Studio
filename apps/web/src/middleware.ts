import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/", "/login", "/register", "/forgot-password", "/reset-password", "/health"];

/** Hosts that serve the platform UI directly (comma-separated env).
 * Any other host is treated as a white-label custom domain: the request
 * passes through unchanged but carries x-tenant-host so the root layout
 * can resolve site-context (branding + theme) for it. */
const PLATFORM_HOSTS = new Set(
  (process.env.NEXT_PUBLIC_PLATFORM_HOSTS ?? "localhost:3000,localhost")
    .split(",")
    .map((h) => h.trim().toLowerCase())
    .filter(Boolean),
);

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const host = (request.headers.get("host") ?? "").toLowerCase();

  // White-label custom domain → tag the request; the root layout resolves
  // site-context (branding + theme) for it. The backend never trusts this
  // header — it is only a lookup key for the public site-context endpoint.
  const requestHeaders = new Headers(request.headers);
  // R101[L14]: strip any client-supplied x-tenant-host first — on platform
  // hosts the conditional set below never runs, so a spoofed inbound header
  // would otherwise pass through and let a caller impersonate a custom domain.
  requestHeaders.delete("x-tenant-host");
  if (host && !PLATFORM_HOSTS.has(host)) {
    requestHeaders.set("x-tenant-host", host);
  }

  // Public pages + API + static assets → pass through
  if (
    PUBLIC_PATHS.some((p) => pathname === p) ||
    pathname.startsWith("/api/") ||
    pathname.startsWith("/_next/") ||
    pathname.startsWith("/join/") ||
    pathname.startsWith("/u/") ||
    pathname.startsWith("/registry") ||
    pathname.startsWith("/certificates") ||
    pathname.startsWith("/client")
  ) {
    return NextResponse.next({ request: { headers: requestHeaders } });
  }

  // Check for refresh token cookie (presence only — actual validation by API)
  const hasRefreshToken = request.cookies.has("refresh_token");

  if (!hasRefreshToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next({ request: { headers: requestHeaders } });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|og-image.png|robots.txt).*)"],
};
