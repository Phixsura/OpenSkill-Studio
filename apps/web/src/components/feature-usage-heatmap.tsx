"use client";

interface FeatureUsage { feature: string; category: string; total_usage: number; avg_daily: number;
  intensity_pct: number; trend: string; }
interface FeatureUsageHeatmapProps { features: FeatureUsage[]; periodDays: number; }

const trendIcon = (t: string) => t === "up" ? "📈" : t === "down" ? "📉" : "➡️";

export function FeatureUsageHeatmap({ features, periodDays }: FeatureUsageHeatmapProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Feature Usage</h2>
        <span className="text-xs text-gray-400">Last {periodDays} days</span>
      </div>
      <div className="space-y-1.5">
        {features.map(f => (
          <div key={f.feature} className="flex items-center gap-3 rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{f.feature}</span>
                <span className="text-xs">{trendIcon(f.trend)}</span>
              </div>
              <p className="text-xs text-gray-400">{f.category} · {f.avg_daily}/day avg</p>
            </div>
            <div className="w-24">
              <div className="h-3 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500"
                  style={{ width: `${f.intensity_pct}%`, opacity: Math.max(0.3, f.intensity_pct / 100) }} />
              </div>
            </div>
            <span className="w-14 text-right text-xs font-bold">{f.total_usage.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
