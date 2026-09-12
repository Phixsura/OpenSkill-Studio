/** Minimal client-portal shell: brand header + project context only.
 * ZERO dashboard navigation — clients never see internal routes (#27 §29). */
export default function ClientPortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[hsl(var(--background))]">
      <header className="border-b bg-[hsl(var(--card))] px-6 py-4">
        <p className="text-lg font-bold">Project review</p>
      </header>
      <main className="mx-auto max-w-5xl p-4 md:p-8">{children}</main>
    </div>
  );
}
