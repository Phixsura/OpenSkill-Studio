"use client";

interface NavItem { id: string; label: string; icon: string; path: string;
  active: boolean; badge: number | null; }
interface NavSidebarProps { items: NavItem[]; onNavigate: (path: string) => void; }

export function NavSidebar({ items, onNavigate }: NavSidebarProps) {
  return (
    <nav className="w-52 border-r dark:border-gray-700 py-3 space-y-0.5">
      {items.map(item => (
        <button key={item.id} onClick={() => onNavigate(item.path)}
          className={`w-full flex items-center gap-2 px-4 py-2 text-sm ${
            item.active ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 font-medium"
                       : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
          }`}>
          <span>{item.icon}</span>
          <span className="flex-1 text-left">{item.label}</span>
          {item.badge != null && item.badge > 0 && (
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-red-500 text-white">{item.badge}</span>
          )}
        </button>
      ))}
    </nav>
  );
}
