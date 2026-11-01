"use client";

interface NoteItem { scope: string; message: string; }
interface NoteSection { category: string; label: string; items: NoteItem[]; count: number; }
interface ReleaseNotesPageProps { version: string; date: string; totalCommits: number;
  sections: NoteSection[]; hasBreaking: boolean; }

export function ReleaseNotesPage({ version, date, totalCommits, sections, hasBreaking }: ReleaseNotesPageProps) {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <h2 className="text-2xl font-bold">v{version}</h2>
          {hasBreaking && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">⚠️ Breaking</span>}
        </div>
        <p className="text-sm text-gray-400">{date} · {totalCommits} commits</p>
      </div>
      <div className="space-y-6">
        {sections.map(s => (
          <div key={s.category}>
            <h3 className="text-sm font-semibold mb-2">{s.label} ({s.count})</h3>
            <ul className="space-y-1">
              {s.items.map((item, i) => (
                <li key={i} className="text-sm flex gap-2">
                  <span className="text-gray-300">•</span>
                  <span>
                    {item.scope && <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1 rounded mr-1">{item.scope}</code>}
                    {item.message}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
