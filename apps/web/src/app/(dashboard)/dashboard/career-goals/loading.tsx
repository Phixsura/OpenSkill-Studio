export default function Loading() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-48 animate-pulse rounded bg-[hsl(var(--muted))]" />
      <div className="h-4 w-80 animate-pulse rounded bg-[hsl(var(--muted))]" />
      <div className="grid gap-4 sm:grid-cols-2">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-48 animate-pulse rounded-lg border bg-[hsl(var(--muted))]" />
        ))}
      </div>
    </div>
  );
}
