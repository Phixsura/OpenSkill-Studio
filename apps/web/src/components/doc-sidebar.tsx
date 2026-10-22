"use client";

interface DocItem { slug: string; title: string; children?: { slug: string; title: string }[]; }
interface DocSidebarProps { items: DocItem[]; activeSlug: string; onNavigate: (slug: string) => void; }

export function DocSidebar({ items, activeSlug, onNavigate }: DocSidebarProps) {
  return (
    <nav className="w-56 space-y-1" aria-label="Documentation">
      {items.map(item => (
        <div key={item.slug}>
          <button onClick={() => onNavigate(item.slug)}
            className={`block w-full rounded px-3 py-1.5 text-left text-sm ${activeSlug === item.slug ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400"}`}>
            {item.title}
          </button>
          {item.children?.map(child => (
            <button key={child.slug} onClick={() => onNavigate(child.slug)}
              className={`block w-full rounded pl-6 pr-3 py-1 text-left text-sm ${activeSlug === child.slug ? "font-semibold text-blue-700" : "text-gray-500 hover:text-gray-700"}`}>
              {child.title}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );
}
