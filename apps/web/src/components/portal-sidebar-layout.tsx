"use client";

interface PortalSidebarLayoutProps { sidebar: React.ReactNode; children: React.ReactNode; }

export function PortalSidebarLayout({ sidebar, children }: PortalSidebarLayoutProps) {
  return (
    <div className="flex gap-6">
      <aside className="hidden w-56 shrink-0 lg:block">{sidebar}</aside>
      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
