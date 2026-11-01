"use client";

interface ErrorResult { service: string; rate: number; threshold: number; breaching: boolean; }
interface ErrorRateMonitorProps { results: ErrorResult[]; alerting: number; allOk: boolean; }

export function ErrorRateMonitor({ results, alerting, allOk }: ErrorRateMonitorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐛 Error Rates</h3>
        <span className={`text-xs ${allOk ? "text-green-600" : "text-red-500"}`}>
          {allOk ? "✅ All OK" : `⚠ ${alerting} alerting`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.service} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className={r.breaching ? "text-red-600 font-bold" : ""}>{r.breaching ? "🔴" : "🟢"} {r.service}</span>
            <span className="font-mono">{r.rate}% / {r.threshold}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
