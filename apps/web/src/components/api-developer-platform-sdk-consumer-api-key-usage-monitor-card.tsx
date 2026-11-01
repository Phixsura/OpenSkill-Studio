"use client";

interface Snapshot { keyId: string; reqsLastMin: number; reqsLastHour: number; errorsLastHour: number; avgMs: number; status: string; }
interface Props { snapshots: Snapshot[]; consumerId: string; appName: string; }

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  idle: "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
  throttled: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKConsumerApiKeyUsageMonitorCard({ snapshots, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Key Usage Monitor</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {snapshots.length} keys</p>
      </div>
      {snapshots.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No key usage data</p>
      ) : (
        <div className="space-y-2">
          {snapshots.map((s) => (
            <div key={s.keyId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{s.keyId}</code>
                <span className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${statusColors[s.status] ?? ""}`}>{s.status}</span>
              </div>
              <div className="mt-0.5 grid grid-cols-4 gap-1 text-center text-[9px] text-gray-400">
                <span>{s.reqsLastMin}/min</span>
                <span>{s.reqsLastHour}/hr</span>
                <span className={s.errorsLastHour > 0 ? "text-red-400" : ""}>{s.errorsLastHour} err</span>
                <span>{s.avgMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
