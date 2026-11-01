"use client";

interface AppShellProps {
  platformName: string; authenticated: boolean; userName?: string;
  notificationCount: number; theme: string;
  navItems: { label: string; url: string; icon: string }[];
  children: React.ReactNode;
}

export function CompleteMarketplaceAppShell({ platformName, authenticated, userName, notificationCount, theme, navItems, children }: AppShellProps) {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white px-4 py-3 dark:border-gray-700 dark:bg-gray-900">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-lg font-bold">{platformName}</h1>
            <nav className="flex gap-1">
              {navItems.map(n => (
                <a key={n.label} href={n.url} className="rounded px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 dark:text-gray-400">
                  {n.icon} {n.label}
                </a>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            {authenticated ? (
              <>
                {notificationCount > 0 && (
                  <span className="relative">🔔<span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs text-white">{notificationCount}</span></span>
                )}
                <span className="text-sm">{userName}</span>
              </>
            ) : (
              <a href="/login" className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">Sign In</a>
            )}
          </div>
        </div>
      </header>
      {/* Main */}
      <main className="mx-auto max-w-7xl p-4">{children}</main>
      {/* Footer */}
      <footer className="border-t border-gray-200 py-6 text-center text-xs text-gray-400 dark:border-gray-700">
        © 2026 {platformName}. All rights reserved.
      </footer>
    </div>
  );
}
