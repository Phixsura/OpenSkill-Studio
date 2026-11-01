"use client";
interface DepWeightPanelProps { weights: Record<string, number>; mostCritical: string; }
export function DepWeightPanel({ weights, mostCritical }: DepWeightPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚖️ Dependency Weights</h3>
        <span className="text-xs text-gray-400">critical: {mostCritical}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(weights).map(([svc, w]) => (
          <div key={svc} className="flex justify-between px-4 py-1.5 text-xs">
            <span className={`font-mono ${svc === mostCritical ? "font-bold text-red-500" : ""}`}>{svc}</span>
            <span className="text-gray-400">{w}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
