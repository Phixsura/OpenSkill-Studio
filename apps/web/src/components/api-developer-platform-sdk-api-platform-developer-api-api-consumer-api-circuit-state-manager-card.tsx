"use client";

interface CircuitInfo { consumer_id: string; endpoint: string; state: string; failure_count: number; total_transitions: number; }
interface Props { circuits: CircuitInfo[]; openCount: number; appName: string; }

const stateColor: Record<string, string> = { closed: "text-green-600 dark:text-green-400", open: "text-red-600 dark:text-red-400", half_open: "text-yellow-600 dark:text-yellow-400" };
const stateDot: Record<string, string> = { closed: "🟢", open: "🔴", half_open: "🟡" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManagerCard({ circuits, openCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Circuit States</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {openCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">{openCount} open</span>}
      </div>
      {circuits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuits</p>
      ) : (
        <div className="space-y-1">
          {circuits.map((c, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{stateDot[c.state]} {c.consumer_id} → {c.endpoint}</span>
              <span className={stateColor[c.state]}>{c.state}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
