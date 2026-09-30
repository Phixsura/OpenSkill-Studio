import type { NextConfig } from "next";

const config: NextConfig = {
  output: "standalone",
  // Dev proxy: /api/* → FastAPI, eliminates CORS issues
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        // API_PROXY_URL: server-only override for the rewrite target (e2e/staging
        // stacks) — unlike NEXT_PUBLIC_API_URL it is never inlined into the
        // client bundle, so connect-src 'self' CSP still holds.
        destination: `${process.env.API_PROXY_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/:path*`,
      },
    ];
  },

  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains",
          },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              // Next.js App Router requires unsafe-inline for its runtime scripts;
              // nonce-based CSP would need a custom middleware generating per-request nonces.
              `script-src 'self' 'unsafe-inline'${process.env.NODE_ENV === "development" ? " 'unsafe-eval'" : ""}`,
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' blob: data: https:",
              "font-src 'self' data:",
              `connect-src 'self'${process.env.NODE_ENV === "development" ? " http://localhost:8000" : ""}`,
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join("; "),
          },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          {
            key: "X-XSS-Protection",
            value: "0",
          },
        ],
      },
    ];
  },
};

export default config;
