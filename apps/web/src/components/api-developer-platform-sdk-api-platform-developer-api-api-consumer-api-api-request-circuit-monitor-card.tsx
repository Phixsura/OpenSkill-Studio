"use client";

interface CircuitInfo { endpoint: string; state: string; failure_count: number; }
interface Summary { total_circuits: number; closed_count: number; open_count: number; half_open_count: number; }
interface Props { circuits: CircuitInfo[]; summary: Summary; appName: string; }

const stateColor: Record<string, string> = { closed: "text-green-600 dark:text-green-400", open: "text-red-600 dark:text-red-400", half_open: "text-yellow-600 dark:text-yellow-400" };
const stateDot: Record<string, string> = { closed: "🟢", open: "🔴", half_open: "🟡" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestCircuitMonitorCard({ circuits, summary, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Circuit Monitor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {summary.total_circuits} circuits</p>
        </div>
        {summary.open_count > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {summary.open_count} open</span>}
      </div>
      {circuits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuits</p>
      ) : (
        <div className="space-y-1">
          {circuits.map((c) => (
            <div key={c.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{stateDot[c.state]} {c.endpoint}</span>
              <span className={stateColor[c.state]}>{c.state} ({c.failure_count}F)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
