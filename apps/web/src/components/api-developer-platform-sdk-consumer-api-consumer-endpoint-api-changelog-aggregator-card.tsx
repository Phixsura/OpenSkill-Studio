"use client";

interface Entry { id: string; version: string; type: string; title: string; breaking: boolean; }
interface Props { entries: Entry[]; totalEntries: number; breakingCount: number; versions: string[]; byType: Record<string, number>; appName: string; }

const typeIcons: Record<string, string> = { added: "✨", changed: "🔄", deprecated: "📦", removed: "🗑️", fixed: "🐛", security: "🔒" };
const typeColors: Record<string, string> = {
  added: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  fixed: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  deprecated: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  removed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  security: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointApiChangelogAggregatorCard({ entries, totalEntries, breakingCount, versions, byType, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Changelog</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalEntries} entries · {versions.length} versions{breakingCount > 0 ? ` · ${breakingCount} breaking` : ""}</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(byType).map(([t, c]) => <span key={t} className={`rounded px-1.5 py-0.5 text-[9px] ${typeColors[t] ?? "bg-gray-200 text-gray-600"}`}>{typeIcons[t] ?? ""} {t}: {c}</span>)}
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changelog entries</p>
      ) : (
        <div className="space-y-1">
          {entries.slice(0, 8).map((e) => (
            <div key={e.id} className="flex items-center justify-between text-[10px]">
              <div className="flex items-center gap-1">
                <span>{typeIcons[e.type] ?? "📋"}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.title}</span>
                {e.breaking && <span className="text-[8px] text-red-500">⚠ breaking</span>}
              </div>
              <span className="text-gray-400">v{e.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
