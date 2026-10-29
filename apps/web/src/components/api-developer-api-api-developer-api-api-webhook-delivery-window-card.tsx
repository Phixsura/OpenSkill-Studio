"use client";

interface WindowInfo { window_id: string; destination: string; start_hour: number; end_hour: number; days: number[]; queued_count: number; }
interface Props { windows: WindowInfo[]; appName: string; }

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindowCard({ windows, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕐 Delivery Windows</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {windows.length} windows</p>
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery windows</p>
      ) : (
        <div className="space-y-2">
          {windows.map((w) => (
            <div key={w.window_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{w.window_id}</span>
                <span className="text-gray-400">{w.start_hour}:00 – {w.end_hour}:00 UTC</span>
              </div>
              <div className="mt-0.5 flex gap-0.5">
                {DAY_NAMES.map((d, i) => (
                  <span key={d} className={`rounded px-1 py-0.5 text-[8px] ${w.days.includes(i) ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-400"}`}>{d}</span>
                ))}
              </div>
              {w.queued_count > 0 && <p className="mt-0.5 text-[10px] text-orange-500">{w.queued_count} queued</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
