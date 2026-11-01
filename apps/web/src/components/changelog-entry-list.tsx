"use client";

interface ChangelogItem { title: string; description: string; breaking: boolean; }
interface ChangelogSection { type: string; emoji: string; label: string;
  entries: ChangelogItem[]; count: number; }
interface ChangelogEntryListProps { sections: ChangelogSection[];
  total: number; hasBreaking: boolean; version: string; }

export function ChangelogEntryList({ sections, total, hasBreaking, version }: ChangelogEntryListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-bold text-lg">v{version}</h3>
          <p className="text-xs text-gray-400">{total} changes</p>
        </div>
        {hasBreaking && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">⚠️ Breaking</span>}
      </div>
      {sections.map(s => (
        <div key={s.type} className="border-b last:border-0 dark:border-gray-700">
          <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 text-sm font-medium">
            {s.emoji} {s.label} ({s.count})
          </div>
          {s.entries.map((e, i) => (
            <div key={i} className="px-4 py-2 text-sm flex items-start gap-2">
              <span className="text-gray-300">•</span>
              <div>
                <span className={e.breaking ? "font-bold text-red-600" : ""}>{e.title}</span>
                {e.breaking && <span className="text-xs text-red-500 ml-1">[BREAKING]</span>}
                {e.description && <p className="text-xs text-gray-400">{e.description}</p>}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
