"use client";

interface ChangelogSummaryCardProps { version: string; summary: string; totalChanges: number;
  typeCounts: Record<string, number>; highlights: string[]; hasBreaking: boolean;
  contributorCount: number; }

const typeIcons: Record<string, string> = {
  added: "✨", fixed: "🐛", changed: "🔄", breaking: "💥", performance: "⚡", security: "🔒",
};

export function ChangelogSummaryCard({ version, summary, totalChanges, typeCounts,
  highlights, hasBreaking, contributorCount }: ChangelogSummaryCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold">v{version}</h3>
        {hasBreaking && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Breaking</span>}
      </div>
      <p className="mt-1 text-sm text-gray-500">{summary}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {Object.entries(typeCounts).map(([type, count]) => (
          <span key={type} className="flex items-center gap-1 rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">
            {typeIcons[type] ?? "📌"} {count} {type}
          </span>
        ))}
      </div>
      {highlights.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-semibold text-gray-400 mb-1">Highlights</p>
          {highlights.map((h, i) => <p key={i} className="text-sm">⭐ {h}</p>)}
        </div>
      )}
      <p className="mt-3 text-xs text-gray-400">{totalChanges} changes · {contributorCount} contributors</p>
    </div>
  );
}
