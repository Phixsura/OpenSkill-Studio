"use client";
export default function NotificationsError({ reset }: { reset: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="mb-4 text-4xl">⚠️</div>
      <h2 className="mb-2 text-xl font-bold">Failed to load notifications</h2>
      <button
        onClick={reset}
        className="rounded-md border px-4 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
      >
        Try again
      </button>
    </div>
  );
}
