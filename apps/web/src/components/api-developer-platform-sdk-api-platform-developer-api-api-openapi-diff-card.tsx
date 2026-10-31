"use client";

interface ChangeInfo { change_type: string; path: string; detail: string; breaking: boolean; }
interface Props { versionFrom: string; versionTo: string; changes: ChangeInfo[]; breakingCount: number; nonBreakingCount: number; appName: string; }

const changeIcon: Record<string, string> = { endpoint_added: "➕", endpoint_removed: "🗑️", field_added: "📝", field_removed: "❌", type_changed: "🔄" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiffCard({ versionFrom, versionTo, changes, breakingCount, nonBreakingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 API Diff</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {versionFrom} → {versionTo}</p>
        </div>
        {breakingCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">💥 {breakingCount} breaking</span>}
      </div>
      {changes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changes detected</p>
      ) : (
        <div className="space-y-1">
          {changes.map((c, i) => (
            <div key={i} className="flex items-center gap-1.5 text-[11px]">
              <span>{changeIcon[c.change_type] ?? "•"}</span>
              <span className={c.breaking ? "font-medium text-red-600 dark:text-red-400" : "text-gray-700 dark:text-gray-300"}>{c.detail}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
