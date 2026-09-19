export default function NotificationsLoading() {
  return (
    <div className="space-y-4">
      <div className="h-8 w-48 animate-pulse rounded bg-[hsl(var(--secondary))]" />
      <div className="h-10 w-full animate-pulse rounded bg-[hsl(var(--secondary))]" />
      {[...Array(5)].map((_, i) => (
        <div key={i} className="h-20 w-full animate-pulse rounded-lg bg-[hsl(var(--secondary))]" />
      ))}
    </div>
  );
}
