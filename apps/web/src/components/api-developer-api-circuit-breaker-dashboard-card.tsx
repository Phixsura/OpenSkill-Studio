"use client";

interface CircuitInfo { endpoint: string; state: string; failure_count: number; success_count: number; failure_rate: number; }
interface Props { circuits: CircuitInfo[]; openCount: number; appName: string; }

const stColor: Record<string, string> = { closed: "bg-green-100 text-green-700", open: "bg-red-100 text-red-700", half_open: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperAPICircuitBreakerDashboardCard({ circuits, openCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Circuit Breakers</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {openCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{openCount} open</span>}
      </div>
      {circuits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuits</p>
      ) : (
        <div className="space-y-2">
          {circuits.map((c) => (
            <div key={c.endpoint} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-gray-700 dark:text-gray-300">{c.endpoint}</span>
                <span className={`rounded-full px-1.5 py-0.5 text-[9px] font-medium ${stColor[c.state] ?? ""}`}>{c.state}</span>
              </div>
              <span className="text-[10px] text-gray-400">{c.failure_rate}% fail</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
