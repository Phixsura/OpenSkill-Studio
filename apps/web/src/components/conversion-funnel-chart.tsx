"use client";

interface FunnelStep { step: string; count: number; dropOffPct: number;
  conversionPct: number; icon: string; }
interface ConversionFunnelChartProps { steps: FunnelStep[]; overallConversion: number;
  worstStep: string | null; }

export function ConversionFunnelChart({ steps, overallConversion, worstStep }: ConversionFunnelChartProps) {
  const maxCount = Math.max(...steps.map(s => s.count), 1);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">📊 Conversion Funnel</h3>
        <span className="text-xs text-gray-400">Overall: {overallConversion}%</span>
      </div>
      <div className="space-y-2">
        {steps.map((s, i) => (
          <div key={i}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span>{s.icon} {s.step}</span>
              <div className="flex items-center gap-2 text-xs">
                <span>{s.count.toLocaleString()}</span>
                {s.dropOffPct > 0 && <span className="text-red-500">-{s.dropOffPct}%</span>}
              </div>
            </div>
            <div className="h-6 rounded bg-gray-200 dark:bg-gray-700">
              <div className="h-full rounded bg-blue-500 flex items-center justify-end pr-2 text-xs text-white"
                style={{ width: `${(s.count / maxCount) * 100}%`, minWidth: 30 }}>
                {s.conversionPct}%
              </div>
            </div>
          </div>
        ))}
      </div>
      {worstStep && <p className="text-xs text-yellow-600">⚠ Biggest drop-off: {worstStep}</p>}
    </div>
  );
}
