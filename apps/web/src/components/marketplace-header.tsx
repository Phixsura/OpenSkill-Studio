"use client";

interface NavItem { label: string; href: string; icon: string; active: boolean; }
interface User { name: string; initials: string; plan: string; }
interface MarketplaceHeaderProps { nav: NavItem[]; user: User | null;
  notifications: number; loggedIn: boolean;
  onNavigate: (href: string) => void; onSearch: (query: string) => void; }

export function MarketplaceHeader({ nav, user, notifications, loggedIn, onNavigate, onSearch }: MarketplaceHeaderProps) {
  return (
    <header className="border-b dark:border-gray-800">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <button onClick={() => onNavigate("/")} className="flex items-center gap-1.5 text-lg font-bold">
            🧩 OpenSkill
          </button>
          <nav className="hidden gap-1 sm:flex">
            {nav.map(n => (
              <button key={n.href} onClick={() => onNavigate(n.href)}
                className={`rounded px-2.5 py-1.5 text-sm ${n.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20" : "text-gray-500 hover:text-gray-900 dark:hover:text-white"}`}>
                {n.icon} {n.label}
              </button>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <input type="search" placeholder="Search apps..."
            onChange={e => onSearch(e.target.value)}
            className="hidden rounded-lg border px-3 py-1.5 text-sm sm:block dark:bg-gray-800 dark:border-gray-600 w-48" />
          {loggedIn ? (
            <div className="flex items-center gap-2">
              {notifications > 0 && <span className="rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">{notifications}</span>}
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs text-white" title={user?.name}>
                {user?.initials}
              </div>
            </div>
          ) : (
            <button onClick={() => onNavigate("/login")} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Sign In</button>
          )}
        </div>
      </div>
    </header>
  );
}
