"use client";

interface Window { id: string; path: string; startsAt: string; endsAt: string; reason: string; status: string; }
interface Props { windows: Window[]; appName: string; }

const statusColors: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  active: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  cancelled: "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointMaintenanceWindowCard({ windows, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Maintenance Windows</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {windows.length} windows</p>
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No maintenance scheduled</p>
      ) : (
        <div className="space-y-2">
          {windows.map((w) => (
            <div key={w.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{w.path}</code>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[w.status] ?? ""}`}>{w.status}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{w.startsAt} — {w.endsAt}{w.reason && ` · ${w.reason}`}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
