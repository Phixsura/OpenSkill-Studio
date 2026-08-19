"use client";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
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
