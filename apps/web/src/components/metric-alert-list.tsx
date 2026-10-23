"use client";

interface AlertResult { name: string; metric: string; current: number;
  threshold: number; operator: string; triggered: boolean; severity: string | null; }
interface MetricAlertListProps { results: AlertResult[]; fired: number; allClear: boolean; }

export function MetricAlertList({ results, fired, allClear }: MetricAlertListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 Metric Alerts</h3>
        <span className={`text-xs font-medium ${allClear ? "text-green-600" : "text-red-500"}`}>
          {allClear ? "✅ All Clear" : `⚠ ${fired} firing`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.name} className={`flex items-center justify-between px-4 py-2.5 ${r.triggered ? "bg-red-50 dark:bg-red-900/10" : ""}`}>
            <div>
              <div className="text-sm font-medium">{r.triggered ? "🔴" : "🟢"} {r.name}</div>
              <div className="text-[10px] text-gray-400">{r.metric} {r.operator} {r.threshold}</div>
            </div>
            <div className="text-right">
              <div className={`text-sm font-mono ${r.triggered ? "text-red-600 font-bold" : ""}`}>{r.current}</div>
              {r.severity && <div className="text-[10px] text-red-500">{r.severity}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
