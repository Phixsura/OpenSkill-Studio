"use client";

interface FunnelStep { step: number; name: string; users: number; drop_off: number; conversion_pct: number; avg_time_sec: number; }
interface UserJourneyFunnelProps { steps: FunnelStep[]; startUsers: number; overallConversion: number; bottleneck: string | null; }

export function UserJourneyFunnel({ steps, startUsers, overallConversion, bottleneck }: UserJourneyFunnelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">User Journey</h2>
        <span className="text-sm text-gray-400">{overallConversion}% overall conversion</span>
      </div>
      <div className="space-y-1">
        {steps.map(s => {
          const widthPct = Math.max(s.conversion_pct, 5);
          return (
            <div key={s.step} className="flex items-center gap-3">
              <span className="w-28 truncate text-sm">{s.name}</span>
              <div className="flex-1">
                <div className="h-8 rounded" style={{ width: `${widthPct}%`, backgroundColor: s.name === bottleneck ? "#ef4444" : "#3b82f6", opacity: 0.7 + s.conversion_pct / 300 }}>
                  <span className="flex h-full items-center px-2 text-xs text-white">{s.users.toLocaleString()}</span>
                </div>
              </div>
              {s.drop_off > 0 && <span className="w-16 text-right text-xs text-red-400">-{s.drop_off}</span>}
            </div>
          );
        })}
      </div>
      {bottleneck && (
        <p className="text-center text-xs text-red-500">⚠️ Biggest drop-off: {bottleneck}</p>
      )}
    </div>
  );
}
