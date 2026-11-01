"use client";

interface ThrottleStatusIndicatorProps { currentRps: number; effectiveMaxRps: number;
  throttled: boolean; delayMs: number; recommendation: string; loadFactor: number; }

export function ThrottleStatusIndicator({ currentRps, effectiveMaxRps, throttled, delayMs, recommendation, loadFactor }: ThrottleStatusIndicatorProps) {
  const pct = Math.min(Math.round((currentRps / Math.max(effectiveMaxRps, 1)) * 100), 100);
  const color = recommendation === "shed_load" ? "bg-red-500" : throttled ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Throttle Status</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${recommendation === "normal" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : recommendation === "throttle" ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {recommendation}
        </span>
      </div>
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-400">
          <span>{currentRps} RPS</span>
          <span>max {effectiveMaxRps}</span>
        </div>
        <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
      <div className="mt-2 flex justify-between text-xs text-gray-400">
        <span>Load: {(loadFactor * 100).toFixed(0)}%</span>
        {delayMs > 0 && <span className="text-yellow-600">+{delayMs}ms delay</span>}
      </div>
    </div>
  );
}
