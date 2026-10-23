"use client";

interface Section { id: string; title: string; type: string; collapsed: boolean; }
interface Breadcrumb { label: string; path: string; }
interface CompletePageLayoutProps { title: string; breadcrumbs: Breadcrumb[];
  sections: Section[]; hasSidebar: boolean; children: React.ReactNode;
  onNavigate: (path: string) => void; }

export function CompletePageLayout({ title, breadcrumbs, sections, hasSidebar, children, onNavigate }: CompletePageLayoutProps) {
  return (
    <div>
      <nav className="flex gap-1 text-xs text-gray-400 mb-4">
        {breadcrumbs.map((b, i) => (
          <span key={b.path}>
            {i > 0 && <span className="mx-1">/</span>}
            <button onClick={() => onNavigate(b.path)} className="hover:text-blue-600">{b.label}</button>
          </span>
        ))}
      </nav>
      <h1 className="text-2xl font-bold mb-6">{title}</h1>
      <div className={hasSidebar ? "flex gap-8" : ""}>
        {hasSidebar && (
          <nav className="w-48 shrink-0 space-y-1">
            {sections.map(s => (
              <a key={s.id} href={`#${s.id}`} className="block text-sm text-gray-500 hover:text-gray-900 py-1">{s.title}</a>
            ))}
          </nav>
        )}
        <div className="flex-1">{children}</div>
      </div>
    </div>
  );
}
