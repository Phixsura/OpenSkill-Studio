"use client";

interface NavItem { label: string; href: string; icon: string; }
interface UserInfo { name: string; initials: string; avatar: string | null; }
interface AppHeaderProps { nav: NavItem[]; user: UserInfo | null; notifications: number;
  loggedIn: boolean; onNavigate: (href: string) => void; }

export function AppHeader({ nav, user, notifications, loggedIn, onNavigate }: AppHeaderProps) {
  return (
    <header className="border-b dark:border-gray-800">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <span className="text-lg font-bold">OpenSkill</span>
          <nav className="flex gap-4">
            {nav.map(n => (
              <button key={n.href} onClick={() => onNavigate(n.href)}
                className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
                {n.icon && <span className="mr-1">{n.icon}</span>}{n.label}
              </button>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {loggedIn && notifications > 0 && (
            <button className="relative text-gray-500 hover:text-gray-700">
              🔔<span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs text-white">{notifications}</span>
            </button>
          )}
          {loggedIn && user ? (
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-medium text-white" title={user.name}>
              {user.initials}
            </div>
          ) : (
            <button className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Sign In</button>
          )}
        </div>
      </div>
    </header>
  );
}
