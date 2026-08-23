import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = [
  "/",
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/health",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public pages + API + static assets → pass through
  if (
    PUBLIC_PATHS.some((p) => pathname === p) ||
    pathname.startsWith("/api/") ||
    pathname.startsWith("/_next/") ||
    pathname.startsWith("/join/") ||
    pathname.startsWith("/u/") ||
    pathname.startsWith("/registry") ||
    pathname.startsWith("/certificates")
  ) {
    return NextResponse.next();
  }

  // Check for refresh token cookie (presence only — actual validation by API)
  const hasRefreshToken = request.cookies.has("refresh_token");

  if (!hasRefreshToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|og-image.png).*)"],
};
