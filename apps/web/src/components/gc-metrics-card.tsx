"use client";

interface GcMetricsCardProps { total: number; avgPauseMs: number; maxPauseMs: number;
  gcPressure: string; byGeneration: Record<string, number>;
  suggestions: { action: string; reason: string }[]; }

const PRESSURE_COLORS: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-red-600",
};

export function GcMetricsCard({ total, avgPauseMs, maxPauseMs, gcPressure, byGeneration, suggestions }: GcMetricsCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">♻️ GC Metrics</h3>
        <span className={`text-xs font-medium ${PRESSURE_COLORS[gcPressure] ?? ""}`}>{gcPressure} pressure</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Collections", v: total }, { l: "Avg Pause", v: `${avgPauseMs}ms` },
          { l: "Max Pause", v: `${maxPauseMs}ms` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      {suggestions.length > 0 && (
        <div className="p-3">
          {suggestions.map((s, i) => (
            <div key={i} className="text-xs py-0.5">💡 <span className="font-medium">{s.action}</span> — {s.reason}</div>
          ))}
        </div>
      )}
    </div>
  );
}
