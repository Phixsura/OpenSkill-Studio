"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Chunk load failures after deployment — reload to get fresh HTML
    const msg = error.message || "";
    if (
      error.name === "ChunkLoadError" ||
      msg.includes("Loading chunk") ||
      msg.includes("dynamically imported module")
    ) {
      window.location.reload();
    }
  }, [error]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-bold">Something went wrong</h1>
      <p className="text-[hsl(var(--muted-foreground))]">
        An unexpected error occurred. Please try again.
      </p>
      <button
        onClick={reset}
        className="rounded bg-[hsl(var(--primary))] px-4 py-2 text-[hsl(var(--primary-foreground))]"
      >
        Try again
      </button>
    </main>
  );
}
