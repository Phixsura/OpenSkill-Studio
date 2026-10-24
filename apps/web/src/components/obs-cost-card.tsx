"use client";

interface ObsCostCardProps { metricsCost: number; logsCost: number; tracesCost: number;
  totalCost: number; display: string; breakdownPct: Record<string, number>;
  suggestions: { area: string; action: string }[]; }

export function ObsCostCard({ metricsCost, logsCost, tracesCost, totalCost, display, breakdownPct, suggestions }: ObsCostCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 Observability Costs</h3>
        <span className="text-lg font-bold">{display}</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Metrics", v: `$${metricsCost}`, p: breakdownPct.metrics },
          { l: "Logs", v: `$${logsCost}`, p: breakdownPct.logs },
          { l: "Traces", v: `$${tracesCost}`, p: breakdownPct.traces }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l} ({s.p}%)</div>
          </div>
        ))}
      </div>
      {suggestions.length > 0 && (
        <div className="p-3">
          {suggestions.map((s, i) => (
            <div key={i} className="text-xs py-0.5">💡 <span className="font-medium">{s.area}</span>: {s.action}</div>
          ))}
        </div>
      )}
    </div>
  );
}
