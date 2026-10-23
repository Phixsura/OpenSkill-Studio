"use client";

interface ChangeEntry { endpoint: string; description: string; version: string; date: string; }
interface ChangeSection { type: string; count: number; entries: ChangeEntry[]; }
interface ApiChangelogTimelineProps { totalChanges: number; severity: string; sections: ChangeSection[]; }

const TYPE_ICON: Record<string, string> = {
  breaking: "🔴", deprecated: "🟡", added: "🟢", fixed: "🔵", changed: "⚪",
};
const TYPE_LABEL: Record<string, string> = {
  breaking: "Breaking Changes", deprecated: "Deprecations",
  added: "New Endpoints", fixed: "Bug Fixes", changed: "Changes",
};

export function ApiChangelogTimeline({ totalChanges, severity, sections }: ApiChangelogTimelineProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📋 API Changelog</h3>
        <div className="flex gap-2 items-center">
          <span className="text-xs text-gray-400">{totalChanges} changes</span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            severity === "major" ? "bg-red-100 text-red-700" :
            severity === "minor" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"
          }`}>{severity}</span>
        </div>
      </div>
      {sections.map(s => (
        <div key={s.type} className="mb-4 last:mb-0">
          <h4 className="text-sm font-medium mb-2">{TYPE_ICON[s.type]} {TYPE_LABEL[s.type]} ({s.count})</h4>
          <div className="space-y-1 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
            {s.entries.map((e, i) => (
              <div key={i} className="text-sm py-1">
                <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1 rounded">{e.endpoint}</code>
                <span className="text-gray-500 ml-2">{e.description}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
