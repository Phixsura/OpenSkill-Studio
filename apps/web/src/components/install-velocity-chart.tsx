"use client";

interface InstallVelocityChartProps { velocity: number; trend: string; avgDaily: number; recentAvg: number; }

const TREND_CONFIG = {
  accelerating: { icon: "🚀", color: "text-green-600", label: "Accelerating" },
  decelerating: { icon: "📉", color: "text-red-600", label: "Decelerating" },
  stable: { icon: "➡️", color: "text-gray-600", label: "Stable" },
};

export function InstallVelocityChart({ velocity, trend, avgDaily, recentAvg }: InstallVelocityChartProps) {
  const cfg = TREND_CONFIG[trend as keyof typeof TREND_CONFIG] || TREND_CONFIG.stable;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Install Velocity</h3>
        <span className={`text-sm font-medium ${cfg.color}`}>{cfg.icon} {cfg.label}</span>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-3 text-center">
        <div><p className={`text-xl font-bold ${velocity > 0 ? "text-green-600" : velocity < 0 ? "text-red-600" : ""}`}>{velocity > 0 ? "+" : ""}{velocity}%</p><p className="text-xs text-gray-400">Velocity</p></div>
        <div><p className="text-xl font-bold">{avgDaily}</p><p className="text-xs text-gray-400">Avg/day</p></div>
        <div><p className="text-xl font-bold">{recentAvg}</p><p className="text-xs text-gray-400">Recent avg</p></div>
      </div>
    </div>
  );
}
