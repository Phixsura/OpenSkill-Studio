"use client";
interface FeatureUsage { feature: string; count: number; uniqueUsers: number; }
interface FeatUsagePanelProps { features: FeatureUsage[]; totalEvents: number; unusedCount: number; }
export function FeatUsagePanel({ features, totalEvents, unusedCount }: FeatUsagePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Feature Usage</h3>
        <span className="text-xs text-gray-400">{totalEvents.toLocaleString()} events{unusedCount > 0 ? ` · ${unusedCount} unused` : ""}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {features.map(f => (
          <div key={f.feature} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{f.feature}</span>
            <span className="text-gray-400">{f.count.toLocaleString()} uses · {f.uniqueUsers} users</span>
          </div>
        ))}
      </div>
    </div>
  );
}
