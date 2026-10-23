"use client";

interface ResourceStats { peak: number; avg: number; current: number; }
interface ResourceUsageTimelineChartProps { resources: string[];
  stats: Record<string, ResourceStats>; totalPoints: number; }

const resIcon: Record<string, string> = { cpu: "🖥️", memory: "💾", disk: "💿", network: "🌐" };

export function ResourceUsageTimelineChart({ resources, stats, totalPoints }: ResourceUsageTimelineChartProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Resource Usage</h2>
        <span className="text-xs text-gray-400">{totalPoints} data points</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {resources.map(res => {
          const s = stats[res];
          if (!s) return null;
          const pct = Math.min(Math.round(s.current), 100);
          return (
            <div key={res} className="rounded-lg border p-3 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span>{resIcon[res] ?? "📊"}</span>
                <span className="font-medium capitalize">{res}</span>
              </div>
              <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${pct > 80 ? "bg-red-500" : pct > 60 ? "bg-yellow-500" : "bg-green-500"}`}
                  style={{ width: `${pct}%` }} />
              </div>
              <div className="mt-1 flex justify-between text-xs text-gray-400">
                <span>Current: {s.current}%</span>
                <span>Peak: {s.peak}%</span>
                <span>Avg: {s.avg}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
