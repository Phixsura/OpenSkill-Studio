"use client";

interface FunnelStep { step: string; count: number; conversion_pct: number; }
interface TelemetryFunnelChartProps { steps: FunnelStep[]; overallPct: number; }

export function TelemetryFunnelChart({ steps, overallPct }: TelemetryFunnelChartProps) {
  const maxCount = Math.max(...steps.map(s => s.count), 1);
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Conversion Funnel</h3>
        <span className="text-sm font-medium text-blue-600">{overallPct}% overall</span>
      </div>
      <div className="mt-4 space-y-2">
        {steps.map((s, i) => {
          const width = Math.max(5, Math.round((s.count / maxCount) * 100));
          return (
            <div key={s.step}>
              <div className="flex justify-between text-xs">
                <span className="font-medium">{s.step}</span>
                <span className="text-gray-400">{s.count.toLocaleString()} {i > 0 ? `(${s.conversion_pct}%)` : ""}</span>
              </div>
              <div className="mt-0.5 h-6 rounded bg-blue-100 dark:bg-blue-900/20" style={{ width: `${width}%` }}>
                <div className="h-full rounded bg-blue-500" style={{ width: "100%" }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
