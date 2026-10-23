"use client";

interface NavItem { id: string; label: string; href: string; icon: string; active: boolean; }
interface FooterLink { label: string; href: string; }
interface CompleteNavLayoutProps { mainNav: NavItem[]; consoleNav: NavItem[];
  footerNav: Record<string, FooterLink[]>; children: React.ReactNode;
  showConsole: boolean; onNavigate: (href: string) => void; }

export function CompleteNavLayout({ mainNav, consoleNav, footerNav, children,
  showConsole, onNavigate }: CompleteNavLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-40 border-b bg-white/95 backdrop-blur dark:bg-gray-950/95 dark:border-gray-800">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5">
          <div className="flex items-center gap-5">
            <button onClick={() => onNavigate("/")} className="text-lg font-bold">🧩 OpenSkill</button>
            <nav className="hidden gap-1 md:flex">
              {mainNav.map(n => (
                <button key={n.id} onClick={() => onNavigate(n.href)}
                  className={`rounded-lg px-3 py-1.5 text-sm ${n.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20" : "text-gray-500"}`}>
                  {n.icon} {n.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <div className="flex flex-1">
        {showConsole && (
          <nav className="w-48 border-r p-3 dark:border-gray-800 hidden md:block">
            {consoleNav.map(n => (
              <button key={n.id} onClick={() => onNavigate(n.href)}
                className={`flex w-full items-center gap-2 rounded px-3 py-2 text-sm ${n.active ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20" : "text-gray-500"}`}>
                {n.icon} {n.label}
              </button>
            ))}
          </nav>
        )}
        <main className="flex-1 p-6">{children}</main>
      </div>
      <footer className="border-t py-8 dark:border-gray-800">
        <div className="mx-auto max-w-5xl grid grid-cols-4 gap-6 px-4">
          {Object.entries(footerNav).map(([section, links]) => (
            <div key={section}>
              <h4 className="text-xs font-semibold mb-2">{section}</h4>
              {links.map(l => <a key={l.href} href={l.href} className="block text-xs text-gray-400 py-0.5 hover:text-gray-600">{l.label}</a>)}
            </div>
          ))}
        </div>
      </footer>
    </div>
  );
}
