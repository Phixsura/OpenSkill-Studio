"use client";

interface NavItem { path: string; title: string; icon: string; }
interface PortalSidebarProps { items: NavItem[]; activePath: string; onNavigate: (path: string) => void; }

export function PortalSidebar({ items, activePath, onNavigate }: PortalSidebarProps) {
  return (
    <nav className="w-52 space-y-0.5" aria-label="Developer Portal">
      {items.map(item => (
        <button key={item.path} onClick={() => onNavigate(item.path)}
          className={`flex w-full items-center gap-2 rounded px-3 py-2 text-sm ${activePath === item.path ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"}`}>
          <span>{item.icon}</span>{item.title}
        </button>
      ))}
    </nav>
  );
}
