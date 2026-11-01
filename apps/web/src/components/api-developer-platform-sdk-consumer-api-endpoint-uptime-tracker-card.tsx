"use client";

interface Report { endpoint: string; uptimePct: number; totalChecks: number; upCount: number; downCount: number; avgMs: number; currentStatus: string; downtimeMin: number; }
interface Props { reports: Report[]; appName: string; }

const statusDot: Record<string, string> = { up: "bg-green-500", down: "bg-red-500", unknown: "bg-gray-400" };

export default function APIDeveloperPlatformSDKConsumerApiEndpointUptimeTrackerCard({ reports, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🟢 Uptime Tracker</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {reports.length} endpoints</p>
      </div>
      {reports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No uptime data</p>
      ) : (
        <div className="space-y-2">
          {reports.map((r) => (
            <div key={r.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`h-2 w-2 rounded-full ${statusDot[r.currentStatus] ?? "bg-gray-400"}`} />
                  <code className="text-gray-700 dark:text-gray-300">{r.endpoint}</code>
                </div>
                <span className={`font-bold ${r.uptimePct >= 99.9 ? "text-green-600" : r.uptimePct >= 99 ? "text-amber-600" : "text-red-600"}`}>{r.uptimePct}%</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{r.avgMs}ms avg · {r.downCount} outages · {r.downtimeMin}min downtime</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
