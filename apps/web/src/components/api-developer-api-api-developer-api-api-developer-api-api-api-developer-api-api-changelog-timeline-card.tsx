"use client";

interface EntryInfo { entry_id: string; version: string; title: string; change_type: string; }
interface Props { entries: EntryInfo[]; typeCounts: Record<string, number>; appName: string; }

const ctIcon: Record<string, string> = { feature: "✨", fix: "🐛", breaking: "💥", deprecation: "⚠️", security: "🔒" };
const ctColor: Record<string, string> = { feature: "text-green-600", fix: "text-blue-600", breaking: "text-red-600", deprecation: "text-yellow-600", security: "text-purple-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimelineCard({ entries, typeCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Changelog Timeline</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {entries.length} changes</p>
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(typeCounts).map(([type, count]) => (
          <span key={type} className={`text-[10px] ${ctColor[type] ?? ""}`}>{ctIcon[type] ?? ""} {count}</span>
        ))}
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changes</p>
      ) : (
        <div className="space-y-1.5">
          {entries.slice(0, 8).map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{ctIcon[e.change_type] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{e.title}</span>
              </div>
              <span className="text-[10px] text-gray-400">{e.version}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
