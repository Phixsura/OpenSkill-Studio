"use client";

interface FanOutInfo { event_type: string; destination_count: number; delivered: number; failed: number; success_rate: number; }
interface Props { results: FanOutInfo[]; totalFanOuts: number; appName: string; }

export default function APIWebhookFanOutCard({ results, totalFanOuts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Webhook Fan Out</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalFanOuts} fan-outs</span>
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No fan-out events</p>
      ) : (
        <div className="space-y-1">
          {results.map((r, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.event_type} → {r.destination_count} dest</span>
              <span className={`${r.success_rate >= 100 ? "text-green-600" : "text-yellow-600"}`}>{r.success_rate}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
