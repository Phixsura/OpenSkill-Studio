"use client";

interface InsightMetric {
  label: string;
  current: number;
  previous: number;
  unit: string;
}

interface TopEvent {
  name: string;
  count: number;
  trend: "up" | "down" | "stable";
}

export function ExtensionInsightsPanel({
  extensionName,
  period,
  metrics,
  topEvents,
  healthScore,
}: {
  extensionName: string;
  period: string;
  metrics: InsightMetric[];
  topEvents: TopEvent[];
  healthScore: number;
}) {
  const formatDelta = (current: number, previous: number) => {
    if (previous === 0) return { text: "New", color: "text-blue-500" };
    const pct = ((current - previous) / previous * 100).toFixed(1);
    const num = parseFloat(pct);
    if (num > 0) return { text: `+${pct}%`, color: "text-green-500" };
    if (num < 0) return { text: `${pct}%`, color: "text-red-500" };
    return { text: "0%", color: "text-gray-400" };
  };

  const healthColor = healthScore >= 90 ? "text-green-500" : healthScore >= 70 ? "text-yellow-500" : "text-red-500";
  const trendIcons = { up: "↑", down: "↓", stable: "→" };
  const trendColors = { up: "text-green-500", down: "text-red-500", stable: "text-gray-400" };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💡 {extensionName} Insights</h2>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">{period}</span>
          <div className="flex items-center gap-1">
            <span className="text-sm text-gray-500">Health:</span>
            <span className={`text-lg font-bold ${healthColor}`}>{healthScore}</span>
          </div>
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {metrics.map((m) => {
          const delta = formatDelta(m.current, m.previous);
          return (
            <div key={m.label} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="text-xs text-gray-500 mb-1">{m.label}</div>
              <div className="text-xl font-bold">{m.current.toLocaleString()}<span className="text-xs text-gray-400 ml-1">{m.unit}</span></div>
              <div className={`text-xs ${delta.color}`}>{delta.text} vs prev period</div>
            </div>
          );
        })}
      </div>

      {/* Top events */}
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <h3 className="font-semibold text-sm mb-3">📊 Top Events</h3>
        <div className="space-y-2">
          {topEvents.map((evt, i) => (
            <div key={evt.name} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="text-gray-400 w-4">{i + 1}.</span>
                <span>{evt.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-mono">{evt.count.toLocaleString()}</span>
                <span className={trendColors[evt.trend]}>{trendIcons[evt.trend]}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
