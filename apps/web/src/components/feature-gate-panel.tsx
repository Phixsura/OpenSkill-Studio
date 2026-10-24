"use client";

interface FeatureLimit { feature: string; type: string; value: unknown; display: string; }
interface FeatureGatePanelProps { plan: string; features: FeatureLimit[]; onUpgrade: () => void; }

export function FeatureGatePanel({ plan, features, onUpgrade }: FeatureGatePanelProps) {
  const locked = features.filter(f => f.type === "boolean" && !f.value);
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Plan: <span className="capitalize">{plan}</span></h3>
        {locked.length > 0 && (
          <button onClick={onUpgrade} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Upgrade</button>
        )}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {features.map(f => (
          <div key={f.feature} className="flex items-center justify-between px-4 py-2">
            <span className="text-sm capitalize">{f.feature.replace(/_/g, " ")}</span>
            <span className={`text-xs font-medium ${f.type === "boolean" ? (f.value ? "text-green-600" : "text-gray-400") : ""}`}>
              {f.display}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
