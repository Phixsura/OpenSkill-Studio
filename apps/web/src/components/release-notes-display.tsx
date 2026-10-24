"use client";

interface PrItem { title: string; number: number; author: string; }
interface NotesSection { type: string; items: PrItem[]; count: number; }
interface ReleaseNotesDisplayProps { version: string; date: string;
  sections: NotesSection[]; contributors: string[];
  totalPrs: number; hasBreaking: boolean; }

const TYPE_EMOJI: Record<string, string> = {
  breaking: "💥", added: "✨", fixed: "🐛", changed: "🔄", deprecated: "⚠️", removed: "🗑️",
};

export function ReleaseNotesDisplay({ version, date, sections, contributors, totalPrs, hasBreaking }: ReleaseNotesDisplayProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-5 border-b dark:border-gray-700">
        <div className="flex items-center gap-2 mb-1">
          <h2 className="text-lg font-bold">v{version}</h2>
          {hasBreaking && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">Breaking</span>}
        </div>
        <p className="text-xs text-gray-400">{date} · {totalPrs} changes · {contributors.length} contributors</p>
      </div>
      {sections.map(s => (
        <div key={s.type} className="border-b last:border-0 dark:border-gray-700">
          <div className="px-5 py-2 bg-gray-50 dark:bg-gray-800 text-sm font-medium">
            {TYPE_EMOJI[s.type] || "📌"} {s.type.charAt(0).toUpperCase() + s.type.slice(1)} ({s.count})
          </div>
          {s.items.map(item => (
            <div key={item.number} className="px-5 py-1.5 text-sm flex items-center gap-2">
              <span className="text-gray-300">•</span>
              <span>{item.title}</span>
              <span className="text-xs text-gray-400">#{item.number} by @{item.author}</span>
            </div>
          ))}
        </div>
      ))}
      <div className="px-5 py-3 text-xs text-gray-400">
        Contributors: {contributors.join(", ")}
      </div>
    </div>
  );
}
