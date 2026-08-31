"use client";

import { useEffect } from "react";

/**
 * Global error boundary — catches errors from the root layout itself.
 * Must provide its own <html> and <body> since the root layout is bypassed.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Chunk load failures (after deployment with new hashes) —
    // reload the page to get fresh HTML with correct chunk URLs.
    const msg = error.message || "";
    if (
      error.name === "ChunkLoadError" ||
      msg.includes("Loading chunk") ||
      msg.includes("dynamically imported module") ||
      msg.includes("Failed to fetch")
    ) {
      window.location.reload();
    }
  }, [error]);

  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 0 }}>
        <main
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100vh",
            gap: "1rem",
            padding: "2rem",
          }}
        >
          <h1 style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
            Something went wrong
          </h1>
          <p style={{ color: "#666" }}>
            An unexpected error occurred. Please try again.
          </p>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              onClick={reset}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.375rem",
                border: "1px solid #ccc",
                cursor: "pointer",
                background: "#000",
                color: "#fff",
              }}
            >
              Try again
            </button>
            {/* Intentional hard link: global-error replaces the root layout,
                so client-side routing may be broken — a full reload is the
                only reliable escape. */}
            {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
            <a
              href="/"
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.375rem",
                border: "1px solid #ccc",
                textDecoration: "none",
                color: "#000",
                display: "inline-flex",
                alignItems: "center",
              }}
            >
              Go home
            </a>
          </div>
        </main>
      </body>
    </html>
  );
}
