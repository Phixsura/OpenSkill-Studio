"use client";

interface SandboxTimer {
  timerId: string;
  timerType: "timeout" | "interval";
  callbackName: string;
  delayMs: number;
  state: "active" | "paused" | "fired" | "cancelled";
  fireCount: number;
  maxFires: number;
}

const stateConfig: Record<string, { color: string; icon: string }> = {
  active: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "▶" },
  paused: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏸" },
  fired: { color: "bg-gray-100 text-gray-500 dark:bg-gray-800", icon: "✓" },
  cancelled: { color: "bg-red-100 text-red-500 dark:bg-red-900/30", icon: "⊘" },
};

function formatDelay(ms: number) {
  if (ms >= 60000) return `${(ms / 60000).toFixed(0)}min`;
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${ms}ms`;
}

export function TimerPoolPanel({
  timers,
  activeCount,
  onCancel,
  onClearAll,
}: {
  timers: SandboxTimer[];
  activeCount: number;
  onCancel?: (timerId: string) => void;
  onClearAll?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⏱️ Timer Pool</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{activeCount} active</span>
          {activeCount > 0 && (
            <button onClick={onClearAll} className="text-xs bg-red-600 text-white px-2 py-1 rounded">Clear All</button>
          )}
        </div>
      </div>

      <div className="space-y-1">
        {timers.map((t) => {
          const cfg = stateConfig[t.state];
          return (
            <div key={t.timerId} className={`rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between ${t.state === "cancelled" || t.state === "fired" ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2 text-sm">
                <span>{cfg.icon}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${t.timerType === "interval" ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30" : "bg-gray-100 text-gray-600 dark:bg-gray-800"}`}>
                  {t.timerType}
                </span>
                <code>{t.callbackName}</code>
                <span className="text-xs text-gray-400">{formatDelay(t.delayMs)}</span>
                {t.timerType === "interval" && (
                  <span className="text-xs text-gray-400">×{t.fireCount}{t.maxFires > 0 ? `/${t.maxFires}` : ""}</span>
                )}
              </div>
              {t.state === "active" && (
                <button onClick={() => onCancel?.(t.timerId)} className="text-xs text-red-500">Cancel</button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
