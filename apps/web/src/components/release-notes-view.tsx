"use client";

interface NoteEntry { title: string; description: string; icon: string; pr: number | null; author: string; }
interface ReleaseNotesViewProps { version: string; date: string;
  categories: Record<string, NoteEntry[]>; hasBreaking: boolean; hasSecurity: boolean; }

export function ReleaseNotesView({ version, date, categories, hasBreaking, hasSecurity }: ReleaseNotesViewProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold">v{version}</h2>
        {hasBreaking && <span className="rounded bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">Breaking</span>}
        {hasSecurity && <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">Security</span>}
        <time className="ml-auto text-xs text-gray-400">{date}</time>
      </div>
      {Object.entries(categories).map(([cat, entries]) => (
        <div key={cat}>
          <h3 className="text-sm font-semibold capitalize mb-2">{cat}</h3>
          <ul className="space-y-1.5">
            {entries.map((e, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span>{e.icon}</span>
                <div>
                  <span className="font-medium">{e.title}</span>
                  {e.pr && <span className="ml-1 text-xs text-gray-400">#{e.pr}</span>}
                  {e.author && <span className="ml-1 text-xs text-gray-400">by {e.author}</span>}
                  {e.description && <p className="text-xs text-gray-500">{e.description}</p>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
