"use client";

interface HealthOverviewCardProps { total: number; healthy: number; degraded: number; critical: number; avgScore: number; worstApp: { name: string; score: number } | null; }

export function HealthOverviewCard({ total, healthy, degraded, critical, avgScore, worstApp }: HealthOverviewCardProps) {
  const color = avgScore >= 95 ? "green" : avgScore >= 80 ? "yellow" : "red";
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">❤️ Health Overview</h4>
        <span className={`text-2xl font-bold text-${color}-600`}>{avgScore}%</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-sm">
        <div><p className="font-bold text-green-600">{healthy}</p><p className="text-xs">Healthy</p></div>
        <div><p className="font-bold text-yellow-600">{degraded}</p><p className="text-xs">Degraded</p></div>
        <div><p className="font-bold text-red-600">{critical}</p><p className="text-xs">Critical</p></div>
      </div>
      {worstApp && <p className="text-xs text-gray-500">⚠️ Worst: {worstApp.name} ({worstApp.score}%)</p>}
    </div>
  );
}
