"use client";

interface Section { key: string; title?: string; type: string; }
interface MarketplaceHomeShellProps { sections: Section[]; authenticated: boolean; userName?: string;
  notificationCount?: number; onSearch: (q: string) => void; children: React.ReactNode; }

export function MarketplaceHomeShell({ sections, authenticated, userName, notificationCount, onSearch, children }: MarketplaceHomeShellProps) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-900">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <h1 className="text-lg font-bold">OpenSkill Marketplace</h1>
          <div className="flex items-center gap-3">
            <input onChange={e => onSearch(e.target.value)} placeholder="Search apps..."
              className="rounded-lg border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
            {authenticated ? (
              <span className="text-sm">{userName} {notificationCount ? `(${notificationCount})` : ""}</span>
            ) : (
              <a href="/login" className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Sign In</a>
            )}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl p-4">{children}</main>
      <footer className="border-t py-6 text-center text-xs text-gray-400">
        {sections.length} sections · OpenSkill Marketplace
      </footer>
    </div>
  );
}
