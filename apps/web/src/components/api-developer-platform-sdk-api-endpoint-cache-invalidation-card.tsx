"use client";

interface RuleInfo { rule_id: string; endpoint: string; trigger: string; pattern: string; invalidations: number; }
interface Props { rules: RuleInfo[]; appName: string; }

const tBadge: Record<string, string> = { on_write: "bg-blue-100 text-blue-700", on_delete: "bg-red-100 text-red-700", ttl_expired: "bg-yellow-100 text-yellow-700", manual: "bg-gray-100 text-gray-600" };

export default function APIDeveloperPlatformSDKApiEndpointCacheInvalidationCard({ rules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗑️ Cache Invalidation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invalidation rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${tBadge[r.trigger] ?? ""}`}>{r.trigger}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.endpoint}</span>
              </div>
              <span className="text-gray-400">{r.invalidations}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
