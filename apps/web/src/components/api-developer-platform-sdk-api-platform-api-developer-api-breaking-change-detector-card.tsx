"use client";

interface ChangeInfo { change_id: string; endpoint: string; change_type: string; description: string; affected_consumers: number; severity: string; }
interface Props { changes: ChangeInfo[]; criticalCount: number; totalAffected: number; appName: string; }

const sBadge: Record<string, string> = { critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", medium: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperApiBreakingChangeDetectorCard({ changes, criticalCount, totalAffected, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💥 Breaking Changes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalAffected} consumers affected</p>
        </div>
        {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{criticalCount} critical</span>}
      </div>
      {changes.length === 0 ? (
        <p className="text-center text-sm text-green-600">✓ No breaking changes</p>
      ) : (
        <div className="space-y-1.5">
          {changes.map((c) => (
            <div key={c.change_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${sBadge[c.severity] ?? ""}`}>{c.severity}</span>
                  <span className="text-gray-700 dark:text-gray-300">{c.endpoint}</span>
                </div>
                <span className="text-gray-400">{c.affected_consumers} affected</span>
              </div>
              <p className="ml-5 text-[10px] text-gray-400">{c.change_type}: {c.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
