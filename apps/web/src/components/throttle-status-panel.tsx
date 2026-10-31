"use client";

interface ThrottleState {
  extensionId: string;
  level: "none" | "light" | "moderate" | "heavy" | "block";
  throughput: number;
  reason: string;
  allowed: number;
  throttled: number;
  hasOverride: boolean;
}

const levelConfig: Record<string, { color: string; icon: string; label: string }> = {
  none: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅", label: "Normal" },
  light: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "🔵", label: "Light" },
  moderate: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "🟡", label: "Moderate" },
  heavy: { color: "bg-orange-100 text-orange-700 dark:bg-orange-900/30", icon: "🟠", label: "Heavy" },
  block: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🔴", label: "Blocked" },
};

export function ThrottleStatusPanel({
  states,
  onOverride,
  onClearOverride,
}: {
  states: ThrottleState[];
  onOverride?: (extId: string, level: string) => void;
  onClearOverride?: (extId: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🚦 Throttle Status</h2>

      <div className="space-y-2">
        {states.map((state) => {
          const cfg = levelConfig[state.level];
          const total = state.allowed + state.throttled;
          const throttledPct = total > 0 ? Math.round((state.throttled / total) * 100) : 0;

          return (
            <div key={state.extensionId} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <code className="text-sm font-semibold">{state.extensionId}</code>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
                  {state.hasOverride && <span className="text-xs text-purple-600">⚡ override</span>}
                </div>
                <div className="flex gap-1">
                  {state.hasOverride ? (
                    <button onClick={() => onClearOverride?.(state.extensionId)}
                      className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Clear</button>
                  ) : (
                    <button onClick={() => onOverride?.(state.extensionId, "block")}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Block</button>
                  )}
                </div>
              </div>

              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-1">
                <div className="h-full bg-green-500 rounded-full" style={{ width: `${state.throughput * 100}%` }} />
              </div>

              <div className="flex gap-4 text-xs text-gray-500">
                <span>Throughput: {Math.round(state.throughput * 100)}%</span>
                <span className="text-green-600">✓ {state.allowed}</span>
                <span className="text-red-500">✗ {state.throttled}</span>
                {throttledPct > 0 && <span>({throttledPct}% dropped)</span>}
                <span className="text-gray-400">{state.reason}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
