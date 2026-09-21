export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-48 animate-pulse rounded bg-[hsl(var(--muted))]" />
      <div className="h-4 w-96 animate-pulse rounded bg-[hsl(var(--muted))]" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-36 animate-pulse rounded-lg border bg-[hsl(var(--muted))]" />
        ))}
      </div>
    </div>
  );
}
