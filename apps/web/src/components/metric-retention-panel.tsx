"use client";

interface Tier { retentionDays: number; sizeGb: number; resolution: string; }
interface MetricRetentionPanelProps { tiers: Record<string, Tier>; totalGb: number;
  needsOptimization: boolean; reductionPct: number; }

export function MetricRetentionPanel({ tiers, totalGb, needsOptimization, reductionPct }: MetricRetentionPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Metric Retention</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalGb} GB total</span>
          {needsOptimization && <span className="text-yellow-600">⚠ Reduce {reductionPct}%</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(tiers).map(([name, t]) => (
          <div key={name} className="flex justify-between px-4 py-2 text-xs">
            <span className="font-mono">{name} ({t.resolution})</span>
            <span className="text-gray-400">{t.retentionDays}d · {t.sizeGb} GB</span>
          </div>
        ))}
      </div>
    </div>
  );
}
