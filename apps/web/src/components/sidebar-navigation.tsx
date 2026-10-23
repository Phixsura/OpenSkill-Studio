"use client";

interface NavItem { id: string; label: string; icon: string; path: string;
  active: boolean; badge: number | null; }
interface SidebarNavigationProps { items: NavItem[]; collapsed: boolean;
  onNavigate: (path: string) => void; onToggle: () => void; }

export function SidebarNavigation({ items, collapsed, onNavigate, onToggle }: SidebarNavigationProps) {
  return (
    <nav className={`flex flex-col border-r dark:border-gray-700 h-full ${collapsed ? "w-16" : "w-56"} transition-all`}>
      <div className="p-3 border-b dark:border-gray-700 flex items-center justify-between">
        {!collapsed && <span className="text-sm font-bold">OpenSkill</span>}
        <button onClick={onToggle} className="text-xs text-gray-400 hover:text-gray-600">{collapsed ? "→" : "←"}</button>
      </div>
      <div className="flex-1 py-2 space-y-0.5">
        {items.map(item => (
          <button key={item.id} onClick={() => onNavigate(item.path)}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm transition ${
              item.active ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 font-medium" : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
            }`}>
            <span className="text-base">{item.icon}</span>
            {!collapsed && <span className="flex-1 text-left">{item.label}</span>}
            {!collapsed && item.badge && item.badge > 0 && (
              <span className="text-xs px-1.5 py-0.5 rounded-full bg-red-500 text-white font-bold">{item.badge}</span>
            )}
          </button>
        ))}
      </div>
    </nav>
  );
}
