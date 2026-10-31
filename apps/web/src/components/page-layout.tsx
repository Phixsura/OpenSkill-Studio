"use client";

interface Breadcrumb { label: string; href: string | null; }
interface NavItem { label: string; href: string; icon: string; active: boolean; badge: string | null; }
interface User { name: string; initials: string; }
interface PageLayoutProps { pageTitle: string; breadcrumbs: Breadcrumb[];
  sidebar: NavItem[]; user: User | null; notifications: number;
  children: React.ReactNode; onNavigate: (href: string) => void; }

export function PageLayout({ pageTitle, breadcrumbs, sidebar, user, notifications, children, onNavigate }: PageLayoutProps) {
  return (
    <div className="min-h-screen">
      <header className="border-b px-4 py-3 dark:border-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            {breadcrumbs.map((b, i) => (
              <span key={i} className="flex items-center gap-1">
                {i > 0 && <span className="text-gray-400">/</span>}
                {b.href ? <a href={b.href} className="text-blue-600 hover:underline">{b.label}</a>
                  : <span className="text-gray-600 dark:text-gray-300">{b.label}</span>}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-3">
            {notifications > 0 && <span className="rounded-full bg-red-500 px-2 py-0.5 text-xs text-white">{notifications}</span>}
            {user && <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs text-white">{user.initials}</div>}
          </div>
        </div>
      </header>
      <div className="flex">
        {sidebar.length > 0 && (
          <nav className="w-48 border-r p-3 dark:border-gray-800">
            {sidebar.map(item => (
              <button key={item.href} onClick={() => onNavigate(item.href)}
                className={`flex w-full items-center gap-2 rounded px-3 py-2 text-sm ${item.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20" : "text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
                <span>{item.icon}</span>{item.label}
                {item.badge && <span className="ml-auto rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">{item.badge}</span>}
              </button>
            ))}
          </nav>
        )}
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
