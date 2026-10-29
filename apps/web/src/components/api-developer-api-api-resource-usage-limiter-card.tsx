"use client";

interface LimitInfo { resource_type: string; limit: number; used: number; remaining: number; usage_pct: number; exceeded: boolean; unit: string; }
interface Props { limits: LimitInfo[]; exceededCount: number; appName: string; }

const rIcon: Record<string, string> = { compute: "⚙️", storage: "💾", bandwidth: "🌐", connections: "🔌" };

export default function APIDeveloperAPIApiResourceUsageLimiterCard({ limits, exceededCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Resource Limits</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exceededCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{exceededCount} exceeded</span>}
      </div>
      {limits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No resource limits</p>
      ) : (
        <div className="space-y-2">
          {limits.map((l) => (
            <div key={l.resource_type}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{rIcon[l.resource_type] ?? "•"} {l.resource_type}</span>
                <span className={l.exceeded ? "text-red-500 font-bold" : "text-gray-400"}>{l.used}/{l.limit} {l.unit}</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${l.usage_pct >= 90 ? "bg-red-500" : l.usage_pct >= 70 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(l.usage_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
