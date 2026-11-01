"use client";

interface DrainStatsInfo {
  sent: number;
  failed: number;
  dropped: number;
  success_rate: number;
}

interface LogDrainInfo {
  drain_id: string;
  destination: string;
  drain_type: string;
  min_level: string;
  enabled: boolean;
  stats: DrainStatsInfo;
}

interface LogDrainCardProps {
  drains: LogDrainInfo[];
  appName: string;
}

export default function LogDrainCard({ drains, appName }: LogDrainCardProps) {
  const active = drains.filter((d) => d.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Log Drains</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {active} active / {drains.length} total
        </span>
      </div>

      {drains.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No log drains</p>
      ) : (
        <div className="space-y-2">
          {drains.map((d) => (
            <div
              key={d.drain_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${d.enabled ? "bg-green-500" : "bg-gray-400"}`}
                  />
                  <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                    {d.drain_id}
                  </span>
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                    {d.drain_type}
                  </span>
                </div>
                <span className="text-[10px] text-gray-400">{d.min_level}+</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                <span className="max-w-[180px] truncate">{d.destination}</span>
                <span>
                  {d.stats.success_rate}% · {d.stats.sent} sent
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
