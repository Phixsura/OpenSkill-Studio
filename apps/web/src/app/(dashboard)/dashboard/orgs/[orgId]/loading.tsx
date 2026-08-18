export default function OrgLoading() {
  return (
    <div className="animate-pulse space-y-4 p-4">
      <div className="h-8 w-48 rounded bg-[hsl(var(--secondary))]" />
      <div className="h-4 w-96 rounded bg-[hsl(var(--secondary))]" />
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="h-24 rounded-lg bg-[hsl(var(--secondary))]" />
        <div className="h-24 rounded-lg bg-[hsl(var(--secondary))]" />
        <div className="h-24 rounded-lg bg-[hsl(var(--secondary))]" />
      </div>
    </div>
  );
}
