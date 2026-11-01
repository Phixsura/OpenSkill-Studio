"use client";

interface SnapInfo { endpoint: string; rps: number; peak_rps: number; avg_rps: number; }
interface Props { snapshots: SnapInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitorCard({ snapshots, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Throughput Monitor</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {snapshots.length} endpoints</p>
      </div>
      {snapshots.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No throughput data</p>
      ) : (
        <div className="space-y-1.5">
          {snapshots.map((s) => (
            <div key={s.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.endpoint}</span>
              <div className="flex gap-2 text-[10px] text-gray-400">
                <span className="font-bold text-blue-600">{s.rps} rps</span>
                <span>peak: {s.peak_rps}</span>
                <span>avg: {s.avg_rps}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
