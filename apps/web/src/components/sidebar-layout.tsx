"use client";

interface SidebarItem { id: string; label: string; icon?: string; }
interface SidebarSection { title: string; items: SidebarItem[]; }
interface SidebarLayoutProps { sections: SidebarSection[]; collapsed: boolean;
  activeItem: string; onItemClick: (id: string) => void; onToggle: () => void;
  children: React.ReactNode; }

export function SidebarLayout({ sections, collapsed, activeItem, onItemClick, onToggle, children }: SidebarLayoutProps) {
  return (
    <div className="flex min-h-screen">
      <aside className={`border-r transition-all dark:border-gray-700 ${collapsed ? "w-14" : "w-56"}`}>
        <div className="flex h-12 items-center justify-between px-3">
          {!collapsed && <span className="text-sm font-bold">Menu</span>}
          <button onClick={onToggle} className="rounded p-1 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800">
            {collapsed ? "→" : "←"}
          </button>
        </div>
        <nav className="space-y-4 px-2 py-3">
          {sections.map(sec => (
            <div key={sec.title}>
              {!collapsed && <p className="px-2 text-[10px] font-medium uppercase text-gray-400">{sec.title}</p>}
              <div className="mt-1 space-y-0.5">
                {sec.items.map(item => (
                  <button key={item.id} onClick={() => onItemClick(item.id)}
                    className={`flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm ${activeItem === item.id ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-900/20" : "text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800"}`}>
                    {item.icon && <span>{item.icon}</span>}
                    {!collapsed && <span>{item.label}</span>}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
