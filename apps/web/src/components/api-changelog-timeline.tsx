"use client";

interface ApiChange { type: string; endpoint: string; description: string; breaking: boolean; }
interface ApiChangelogTimelineProps { versions: Record<string, ApiChange[]>;
  totalChanges: number; breakingCount: number; }

const TYPE_ICONS: Record<string, string> = {
  added: "🟢", deprecated: "🟡", removed: "🔴", changed: "🔵", fixed: "🔧",
};

export function ApiChangelogTimeline({ versions, totalChanges, breakingCount }: ApiChangelogTimelineProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 API Changelog</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalChanges} changes</span>
          {breakingCount > 0 && <span className="text-red-500">⚠ {breakingCount} breaking</span>}
        </div>
      </div>
      {Object.entries(versions).map(([version, changes]) => (
        <div key={version}>
          <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 text-xs font-bold">v{version}</div>
          <div className="divide-y dark:divide-gray-700">
            {changes.map((c, i) => (
              <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs">
                <span>{TYPE_ICONS[c.type] ?? "⚪"}</span>
                <span className="font-mono text-blue-500">{c.endpoint}</span>
                <span className="text-gray-400">{c.description}</span>
                {c.breaking && <span className="text-red-500 text-[10px] ml-auto">breaking</span>}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
