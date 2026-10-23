"use client";

interface FunnelStep { name: string; count: number; pct_of_total: number;
  drop_off: number; drop_off_pct: number; }
interface ConversionFunnelChartProps { steps: FunnelStep[]; overallConversion: number;
  worstStep: string | null; }

export function ConversionFunnelChart({ steps, overallConversion, worstStep }: ConversionFunnelChartProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Conversion Funnel</h2>
        <span className="text-sm font-bold text-blue-600">{overallConversion}% conversion</span>
      </div>
      <div className="space-y-1">
        {steps.map((s, i) => (
          <div key={s.name}>
            <div className="flex items-center gap-2">
              <span className="w-32 truncate text-sm">{s.name}</span>
              <div className="flex-1">
                <div className="h-8 rounded bg-blue-400 dark:bg-blue-600"
                  style={{ width: `${s.pct_of_total}%`, opacity: 0.5 + s.pct_of_total / 200 }}>
                  <span className="flex h-full items-center px-2 text-xs text-white">{s.count.toLocaleString()}</span>
                </div>
              </div>
              {s.drop_off > 0 && (
                <span className="w-20 text-right text-xs text-red-400">↓ {s.drop_off_pct}%</span>
              )}
            </div>
          </div>
        ))}
      </div>
      {worstStep && (
        <p className="text-center text-xs text-red-500">⚠️ Biggest drop: {worstStep}</p>
      )}
    </div>
  );
}
