export default function ProjectsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Projects</h1>
      <p className="text-[hsl(var(--muted-foreground))]">
        View and submit your project assignments.
      </p>
      <div className="rounded-lg border border-dashed p-12 text-center text-sm text-[hsl(var(--muted-foreground))]">
        Project management and submissions coming in ADR-005.
      </div>
    </div>
  );
}
