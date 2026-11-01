"use client";

interface FunnelStep { step: string; count: number; dropOffPct: number; conversionPct: number; }
interface FunnelVisualizationProps { funnel: FunnelStep[]; overallConversion: number;
  bottleneck: string | null; }

export function FunnelVisualization({ funnel, overallConversion, bottleneck }: FunnelVisualizationProps) {
  const maxCount = Math.max(...funnel.map(s => s.count), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔽 User Funnel</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{overallConversion}% conversion</span>
          {bottleneck && <span className="text-red-500">bottleneck: {bottleneck}</span>}
        </div>
      </div>
      <div className="p-4 space-y-2">
        {funnel.map(s => {
          const width = (s.count / maxCount) * 100;
          const isBn = s.step === bottleneck;
          return (
            <div key={s.step}>
              <div className="flex justify-between text-xs mb-0.5">
                <span className={isBn ? "text-red-600 font-bold" : ""}>{s.step}</span>
                <span className="text-gray-400">{s.count.toLocaleString()} ({s.conversionPct}%)</span>
              </div>
              <div className="w-full h-6 bg-gray-100 dark:bg-gray-800 rounded flex items-center">
                <div className={`h-full rounded ${isBn ? "bg-red-400" : "bg-blue-400"}`} style={{ width: `${width}%` }} />
              </div>
              {s.dropOffPct > 0 && <div className="text-[10px] text-red-400 mt-0.5">↓ {s.dropOffPct}% drop-off</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
