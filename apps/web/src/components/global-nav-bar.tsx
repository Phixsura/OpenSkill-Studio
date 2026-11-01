"use client";

interface NavItem { label: string; path: string; icon: string; }
interface NavSection { id: string; label: string; icon: string; items: NavItem[]; active: boolean; }
interface GlobalNavBarProps { sections: NavSection[]; onNavigate: (path: string) => void; }

export function GlobalNavBar({ sections, onNavigate }: GlobalNavBarProps) {
  return (
    <nav className="border-b dark:border-gray-700">
      <div className="flex items-center gap-1 px-4">
        <span className="font-bold text-lg mr-4">⚡ OpenSkill</span>
        {sections.map(s => (
          <div key={s.id} className="group relative">
            <button className={`px-3 py-3 text-sm font-medium ${
              s.active ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-500 hover:text-gray-700"
            }`}>{s.icon} {s.label}</button>
            <div className="hidden group-hover:block absolute left-0 top-full bg-white dark:bg-gray-900 border dark:border-gray-700 rounded-lg shadow-xl p-2 min-w-[200px] z-50">
              {s.items.map(item => (
                <button key={item.path} onClick={() => onNavigate(item.path)}
                  className="w-full text-left flex items-center gap-2 px-3 py-1.5 text-sm rounded hover:bg-gray-50 dark:hover:bg-gray-800">
                  <span>{item.icon}</span>{item.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </nav>
  );
}
