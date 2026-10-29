"use client";

interface EntryInfo { entry_id: string; key_id: string; action: string; actor: string; }
interface Props { entries: EntryInfo[]; actionCounts: Record<string, number>; appName: string; }

const aIcon: Record<string, string> = { created: "✨", rotated: "🔄", revoked: "🚫", suspended: "⏸️", reactivated: "▶️", used: "📡" };

export default function APIDeveloperPlatformSDKApiKeyAuditTrailCard({ entries, actionCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 Key Audit Trail</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        {Object.entries(actionCounts).map(([action, count]) => (
          <span key={action} className="text-[10px] text-gray-400">{aIcon[action] ?? "•"} {action}: {count}</span>
        ))}
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No audit entries</p>
      ) : (
        <div className="space-y-1">
          {entries.slice(0, 8).map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{aIcon[e.action] ?? "•"}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{e.key_id}</span>
              </div>
              <span className="text-gray-400">{e.action} by {e.actor}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
