"use client";

interface Window { id: string; webhookId: string; startHour: number; endHour: number; days: number[]; enabled: boolean; }
interface Props { windows: Window[]; consumerId: string; appName: string; }

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindowCard({ windows, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕐 Delivery Windows</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery windows (always deliver)</p>
      ) : (
        <div className="space-y-2">
          {windows.map((w) => (
            <div key={w.id} className={`rounded-lg bg-gray-50 p-2 dark:bg-gray-800 ${!w.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{w.webhookId}</code>
                <span className="text-gray-500">{w.startHour}:00 — {w.endHour}:00</span>
              </div>
              <div className="mt-0.5 flex gap-0.5">
                {[0, 1, 2, 3, 4, 5, 6].map((d) => (
                  <span key={d} className={`rounded px-1 py-0.5 text-[8px] ${w.days.includes(d) ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" : "bg-gray-200 text-gray-400"}`}>{DAY_NAMES[d]}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
