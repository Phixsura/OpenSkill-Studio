"use client";

interface ReqSamplingPanelProps { total: number; sampled: number; dropped: number;
  targetRate: number; actualRate: number; deviationPct: number; accurate: boolean; }

export function ReqSamplingPanel({ total, sampled, dropped, targetRate, actualRate, deviationPct, accurate }: ReqSamplingPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Request Sampling</h3>
        <span className={`text-xs ${accurate ? "text-green-600" : "text-yellow-600"}`}>
          {accurate ? "✅ Accurate" : `⚠ ${deviationPct}% deviation`}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Total", v: total.toLocaleString() }, { l: "Sampled", v: sampled.toLocaleString() },
          { l: "Target", v: `${(targetRate * 100).toFixed(1)}%` },
          { l: "Actual", v: `${(actualRate * 100).toFixed(1)}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
