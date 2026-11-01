"use client";
interface Outlier { instance: string; errorRate: number; zScore: number; }
interface MeshOutlierPanelProps { outliers: Outlier[]; total: number; meanError: number; ejectionsNeeded: number; }
export function MeshOutlierPanel({ outliers, total, meanError, ejectionsNeeded }: MeshOutlierPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Mesh Outliers</h3>
        <span className={`text-xs font-bold ${ejectionsNeeded > 0 ? "text-red-500" : "text-green-600"}`}>
          {ejectionsNeeded > 0 ? `⚠ ${ejectionsNeeded} outliers` : "✅ No outliers"} · {total} instances · avg {meanError}%
        </span>
      </div>
      {outliers.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {outliers.map(o => (
            <div key={o.instance} className="flex justify-between px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{o.instance}</span>
              <span>{o.errorRate}% err ({o.zScore}σ) — EJECT</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
