"use client";

interface RuleInfo { rule_id: string; endpoint: string; splits: Record<string, number>; total_routed: number; per_version_count: Record<string, number>; }
interface Props { rules: RuleInfo[]; appName: string; }

export default function APIDeveloperAPIApiTrafficSplitterCard({ rules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Traffic Splitter</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No split rules</p>
      ) : (
        <div className="space-y-3">
          {rules.map((r) => (
            <div key={r.rule_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.endpoint}</span>
                <span className="text-gray-400">{r.total_routed.toLocaleString()} routed</span>
              </div>
              <div className="mt-1 flex gap-1">
                {Object.entries(r.splits).map(([ver, pct]) => (
                  <div key={ver} className="flex-1 rounded bg-blue-100 py-0.5 text-center text-[10px] text-blue-700 dark:bg-blue-900 dark:text-blue-200" style={{ flex: pct }}>
                    {ver}: {pct}%
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
