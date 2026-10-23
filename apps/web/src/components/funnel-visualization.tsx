"use client";

interface FunnelStep { step: string; count: number; conversionDisplay: string;
  dropOff: number; dropPct: number; }
interface FunnelVisualizationProps { steps: FunnelStep[]; overallDisplay: string;
  worstStep: string | null; }

export function FunnelVisualization({ steps, overallDisplay, worstStep }: FunnelVisualizationProps) {
  const maxCount = steps[0]?.count || 1;
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📊 Conversion Funnel</h3>
        <span className="text-sm font-bold">{overallDisplay} overall</span>
      </div>
      <div className="space-y-2">
        {steps.map((s, i) => (
          <div key={s.step}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className={s.step === worstStep ? "text-red-600 font-medium" : ""}>{s.step}</span>
              <span className="text-gray-400">{s.count.toLocaleString()} ({s.conversionDisplay})</span>
            </div>
            <div className="h-6 bg-gray-100 dark:bg-gray-800 rounded overflow-hidden">
              <div className={`h-full rounded ${s.step === worstStep ? "bg-red-400" : "bg-blue-500"}`}
                   style={{ width: `${(s.count / maxCount) * 100}%` }} />
            </div>
            {s.dropOff > 0 && (
              <p className="text-xs text-red-400 mt-0.5">↓ {s.dropOff.toLocaleString()} dropped ({s.dropPct}%)</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
