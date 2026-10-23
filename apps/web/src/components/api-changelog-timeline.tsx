"use client";

interface ApiVersion { version: string; date: string; added: number; removed: number; modified: number; breaking: boolean; total_changes: number; }
interface ApiChangelogTimelineProps { entries: ApiVersion[]; stabilityScore: number; }

export function ApiChangelogTimeline({ entries, stabilityScore }: ApiChangelogTimelineProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">API Changelog</h1>
        <div className="text-right">
          <span className={`text-lg font-bold ${stabilityScore >= 80 ? "text-green-600" : "text-yellow-600"}`}>{stabilityScore}</span>
          <p className="text-xs text-gray-400">Stability Score</p>
        </div>
      </div>
      <div className="space-y-3">
        {entries.map(e => (
          <div key={e.version} className={`border-l-4 ${e.breaking ? "border-red-400" : "border-green-400"} rounded-r-lg bg-white p-4 shadow-sm dark:bg-gray-800`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-mono text-lg font-bold">{e.version}</span>
                {e.breaking && <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700">Breaking</span>}
              </div>
              <span className="text-xs text-gray-400">{e.date}</span>
            </div>
            <div className="mt-2 flex gap-4 text-xs">
              {e.added > 0 && <span className="text-green-600">+{e.added} added</span>}
              {e.modified > 0 && <span className="text-blue-600">~{e.modified} modified</span>}
              {e.removed > 0 && <span className="text-red-600">-{e.removed} removed</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
