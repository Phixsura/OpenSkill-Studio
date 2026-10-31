"use client";

interface TokenUsageMeterProps { totalConsumed: number; activeKeys: number;
  avgPerKey: number; topEndpoints: { endpoint: string; count: number }[]; }

export function TokenUsageMeter({ totalConsumed, activeKeys, avgPerKey, topEndpoints }: TokenUsageMeterProps) {
  const maxCount = Math.max(...topEndpoints.map(e => e.count), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎫 Token Usage</h3>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Consumed", v: totalConsumed.toLocaleString() },
          { l: "Active Keys", v: activeKeys },
          { l: "Avg/Key", v: avgPerKey.toLocaleString() }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="p-4 space-y-1.5">
        <div className="text-xs text-gray-400 mb-1">Top Endpoints</div>
        {topEndpoints.map(e => (
          <div key={e.endpoint}>
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{e.endpoint}</span>
              <span className="text-gray-400">{e.count}</span>
            </div>
            <div className="w-full h-1 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${(e.count / maxCount) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
