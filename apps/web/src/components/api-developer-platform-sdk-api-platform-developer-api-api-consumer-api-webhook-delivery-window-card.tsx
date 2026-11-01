"use client";

interface WindowInfo { consumer_id: string; start_hour: number; end_hour: number; timezone: string; days: string[]; buffer: boolean; }
interface Props { windows: WindowInfo[]; appName: string; }

const fmtHour = (h: number) => `${h.toString().padStart(2, "0")}:00`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindowCard({ windows, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕐 Delivery Windows</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {windows.length} consumers</p>
      </div>
      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery windows</p>
      ) : (
        <div className="space-y-1.5">
          {windows.map((w) => (
            <div key={w.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{w.consumer_id}</span>
                <span className="text-gray-400">{fmtHour(w.start_hour)}–{fmtHour(w.end_hour)} {w.timezone}</span>
              </div>
              <div className="flex gap-1 mt-0.5">
                {w.days.map((d) => <span key={d} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{d}</span>)}
                {w.buffer && <span className="text-[9px] text-amber-500">📦 buffer</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
