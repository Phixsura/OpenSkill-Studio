"use client";

import Link from "next/link";

export default function DashboardError({
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 p-8">
      <h2 className="text-xl font-bold">Something went wrong</h2>
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        An error occurred while loading this page.
      </p>
      <div className="flex gap-3">
        <button
          onClick={reset}
          className="rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm text-[hsl(var(--primary-foreground))]"
        >
          Try again
        </button>
        <Link
          href="/dashboard"
          className="rounded-md border px-4 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
