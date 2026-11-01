"use client";

interface DocChild { slug: string; title: string; }
interface DocSection { slug: string; title: string; children: DocChild[]; }
interface DocsSidebarNavProps { sections: DocSection[]; activeSlug: string;
  onNavigate: (slug: string) => void; }

export function DocsSidebarNav({ sections, activeSlug, onNavigate }: DocsSidebarNavProps) {
  return (
    <nav className="w-56 space-y-4">
      {sections.map(s => (
        <div key={s.slug}>
          <button onClick={() => onNavigate(s.slug)}
            className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-1 hover:text-gray-600">{s.title}</button>
          <ul className="space-y-0.5 border-l dark:border-gray-700 ml-1">
            {s.children.map(c => (
              <li key={c.slug}>
                <button onClick={() => onNavigate(c.slug)}
                  className={`block w-full text-left text-sm px-3 py-1 border-l-2 -ml-px ${
                    c.slug === activeSlug ? "border-blue-500 text-blue-600 font-medium" :
                    "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}>{c.title}</button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}
