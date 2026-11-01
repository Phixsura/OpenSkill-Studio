"use client";

interface NavItem { label: string; href: string; icon: string; active?: boolean; badge?: number; }

interface AppSidebarNavProps { items: NavItem[]; }

export function AppSidebarNav({ items }: AppSidebarNavProps) {
  return (
    <nav className="space-y-1">
      {items.map(item => (
        <a key={item.href} href={item.href}
          className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
            item.active ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-900/20 dark:text-blue-300" : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          }`}>
          <span>{item.icon}</span>
          <span className="flex-1">{item.label}</span>
          {item.badge != null && item.badge > 0 && (
            <span className="rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">{item.badge}</span>
          )}
        </a>
      ))}
    </nav>
  );
}
