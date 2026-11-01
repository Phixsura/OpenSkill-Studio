"use client";

interface WindowInfo { window_id: string; destination: string; start_hour: number; end_hour: number; timezone: string; enabled: boolean; }
interface Props { windows: WindowInfo[]; appName: string; }

export default function APIWebhookDeliveryWindowCard({ windows, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕐 Delivery Windows</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{windows.length} windows</span>
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery windows</p>
      ) : (
        <div className="space-y-1">
          {windows.map((w) => (
            <div key={w.window_id} className={`flex items-center justify-between text-[11px] ${!w.enabled ? "opacity-50" : ""}`}>
              <span className="truncate max-w-[150px] text-gray-700 dark:text-gray-300">{w.destination}</span>
              <span className="text-gray-400">{w.start_hour}:00–{w.end_hour}:00 {w.timezone}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
