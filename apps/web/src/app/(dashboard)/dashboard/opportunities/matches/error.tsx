"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="mb-4 text-4xl">⚠️</div>
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="mt-2 max-w-md text-center text-[hsl(var(--muted-foreground))]">
        {error.message || "An unexpected error occurred while loading opportunity matches."}
      </p>
      <button
        onClick={reset}
        className="mt-6 rounded-md bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] hover:opacity-90"
      >
        Try again
      </button>
    </div>
  );
}
