"use client";

interface CicdMetricsDashboardProps { totalRuns: number; passRate: number;
  avgDurationSec: number; p95DurationSec: number; deploysPerDay: number;
  doraLevel: string; }

const DORA_COLORS: Record<string, string> = {
  elite: "text-green-600", high: "text-blue-600", medium: "text-yellow-600", low: "text-red-600",
};

export function CicdMetricsDashboard({ totalRuns, passRate, avgDurationSec, p95DurationSec, deploysPerDay, doraLevel }: CicdMetricsDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 CI/CD Metrics</h3>
        <span className={`text-xs font-medium ${DORA_COLORS[doraLevel] ?? ""}`}>DORA: {doraLevel}</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Runs", v: totalRuns }, { l: "Pass Rate", v: `${passRate}%` },
          { l: "Deploys/Day", v: deploysPerDay }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-bold">{avgDurationSec}s</div>
          <div className="text-[10px] text-gray-400">Avg Duration</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-sm font-bold">{p95DurationSec}s</div>
          <div className="text-[10px] text-gray-400">P95 Duration</div>
        </div>
      </div>
    </div>
  );
}
