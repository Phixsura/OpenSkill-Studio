"use client";

interface LegalPageLayoutProps { title: string; lastUpdated: string; sections: string[];
  activeSection: string | null; onSectionClick: (section: string) => void; children: React.ReactNode; }

export function LegalPageLayout({ title, lastUpdated, sections, activeSection, onSectionClick, children }: LegalPageLayoutProps) {
  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{title}</h1>
        <p className="mt-1 text-sm text-gray-400">Last updated: {lastUpdated}</p>
      </div>
      <div className="flex gap-8">
        <nav className="hidden w-48 md:block">
          <h3 className="text-xs font-semibold text-gray-400">Contents</h3>
          <ul className="mt-2 space-y-1">
            {sections.map((s, i) => (
              <li key={i}>
                <button onClick={() => onSectionClick(s)}
                  className={`block w-full rounded px-2 py-1 text-left text-sm ${activeSection === s ? "bg-blue-50 font-semibold text-blue-700 dark:bg-blue-900/20" : "text-gray-600 hover:bg-gray-50 dark:text-gray-400"}`}>
                  {i + 1}. {s}
                </button>
              </li>
            ))}
          </ul>
        </nav>
        <div className="flex-1 prose prose-sm dark:prose-invert">{children}</div>
      </div>
    </div>
  );
}
