"use client";

interface NavItem { id: string; label: string; icon: string; href: string; active: boolean; badge: number | null; }
interface AppSidebarProps { appName: string; items: NavItem[]; onNavigate: (href: string) => void; }

export function AppSidebar({ appName, items, onNavigate }: AppSidebarProps) {
  return (
    <nav className="w-52 space-y-1">
      <p className="px-3 mb-3 text-sm font-bold truncate">{appName}</p>
      {items.map(item => (
        <button key={item.id} onClick={() => onNavigate(item.href)}
          className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm ${item.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20 dark:text-blue-300" : "text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
          <span>{item.icon}</span>
          <span className="flex-1 text-left">{item.label}</span>
          {item.badge != null && item.badge > 0 && (
            <span className="rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">{item.badge}</span>
          )}
        </button>
      ))}
    </nav>
  );
}
