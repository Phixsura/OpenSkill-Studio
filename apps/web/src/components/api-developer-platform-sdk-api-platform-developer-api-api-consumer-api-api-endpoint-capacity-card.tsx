"use client";

interface CapInfo { endpoint: string; method: string; max_rps: number; current_rps: number; utilization_pct: number; status: string; }
interface Props { capacities: CapInfo[]; saturatedCount: number; appName: string; }

const statusColor: Record<string, string> = { low: "text-green-600 dark:text-green-400", moderate: "text-blue-600 dark:text-blue-400", high: "text-orange-600 dark:text-orange-400", saturated: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointCapacityCard({ capacities, saturatedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Endpoint Capacity</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {saturatedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {saturatedCount} saturated</span>}
      </div>
      {capacities.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No capacity data</p>
      ) : (
        <div className="space-y-1.5">
          {capacities.map((c) => (
            <div key={`${c.method}-${c.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.method} {c.endpoint}</span>
                <span className={statusColor[c.status] ?? ""}>{c.current_rps}/{c.max_rps} rps</span>
              </div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1 rounded-full ${c.utilization_pct >= 80 ? "bg-red-500" : "bg-green-500"}`} style={{ width: `${Math.min(c.utilization_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
