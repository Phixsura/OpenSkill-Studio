"use client";

interface Page { title: string; path: string; active: boolean; }
interface Section { title: string; icon: string; pages: Page[]; expanded: boolean; }
interface DocsSidebarProps { sections: Section[]; onNavigate: (path: string) => void; }

export function DocsSidebar({ sections, onNavigate }: DocsSidebarProps) {
  return (
    <nav className="w-56 space-y-3">
      {sections.map(sec => (
        <div key={sec.title}>
          <p className="flex items-center gap-1.5 px-3 text-xs font-semibold text-gray-400 uppercase">
            <span>{sec.icon}</span>{sec.title}
          </p>
          <div className="mt-1 space-y-0.5">
            {sec.pages.map(p => (
              <button key={p.path} onClick={() => onNavigate(p.path)}
                className={`block w-full rounded px-3 py-1.5 text-left text-sm ${p.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20 dark:text-blue-300" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"}`}>
                {p.title}
              </button>
            ))}
          </div>
        </div>
      ))}
    </nav>
  );
}
