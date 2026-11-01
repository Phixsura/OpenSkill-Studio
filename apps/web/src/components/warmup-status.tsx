"use client";

interface WarmupService { name: string; ready: boolean; latencyMs: number; thresholdMs: number; }
interface WarmupStatusProps { services: WarmupService[]; allReady: boolean;
  ready: number; total: number; }

export function WarmupStatus({ services, allReady, ready, total }: WarmupStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${allReady ? "bg-green-50 dark:bg-green-900/10" : "bg-yellow-50 dark:bg-yellow-900/10"}`}>
        <h3 className="font-semibold text-sm">🔥 Warm-up Status</h3>
        <span className={`text-xs ${allReady ? "text-green-600" : "text-yellow-600"}`}>
          {allReady ? "✅ All Ready" : `⏳ ${ready}/${total} ready`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{s.ready ? "✅" : "⏳"}</span>
              <span className="font-mono">{s.name}</span>
            </div>
            <span className="text-gray-400">{s.latencyMs}ms / {s.thresholdMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
