"use client";

interface NavItem { path: string; label: string; icon: string; active: boolean; }
interface NavigationSidebarProps { items: NavItem[]; onNavigate: (path: string) => void;
  collapsed?: boolean; }

export function NavigationSidebar({ items, onNavigate, collapsed = false }: NavigationSidebarProps) {
  return (
    <nav className={`flex flex-col gap-1 ${collapsed ? "w-14" : "w-56"}`}>
      {items.map(item => (
        <button key={item.path} onClick={() => onNavigate(item.path)}
          className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors ${item.active ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20 dark:text-blue-400" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"}`}>
          <span className="text-lg">{item.icon}</span>
          {!collapsed && <span>{item.label}</span>}
        </button>
      ))}
    </nav>
  );
}
