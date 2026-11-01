"use client";

interface NavItem { label: string; path: string; icon: string; active: boolean; badge: string | null; }
interface SidebarNavProps { sections: Record<string, NavItem[]>; onNavigate: (path: string) => void; }

export function SidebarNav({ sections, onNavigate }: SidebarNavProps) {
  return (
    <nav className="space-y-4 w-56">
      {Object.entries(sections).map(([section, items]) => (
        <div key={section}>
          <p className="px-3 text-xs font-semibold text-gray-400 uppercase mb-1">{section}</p>
          {items.map(item => (
            <button key={item.path} onClick={() => onNavigate(item.path)}
              className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm ${item.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20 dark:text-blue-300" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"}`}>
              <span>{item.icon}</span>
              <span className="flex-1 text-left">{item.label}</span>
              {item.badge && <span className="rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">{item.badge}</span>}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );
}
