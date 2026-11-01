"use client";

interface FeatureGate {
  feature: string;
  minTier: string;
  enabled: boolean;
  description: string;
  isAvailable: boolean;
  reason: string;
  hasOverride: boolean;
}

const tierColors: Record<string, string> = {
  free: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  starter: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  pro: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
  enterprise: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
};

export function FeatureGatePanel({
  gates,
  currentTier,
  onOverride,
  onClearOverride,
}: {
  gates: FeatureGate[];
  currentTier: string;
  onOverride?: (feature: string, enabled: boolean) => void;
  onClearOverride?: (feature: string) => void;
}) {
  const available = gates.filter((g) => g.isAvailable).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🚪 Feature Gates</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-2 py-0.5 rounded-full capitalize">
            {currentTier}
          </span>
          <span className="text-sm text-gray-500">{available}/{gates.length} available</span>
        </div>
      </div>

      <div className="space-y-1">
        {gates.map((gate) => (
          <div key={gate.feature} className={`rounded-lg border dark:border-gray-700 p-3 ${!gate.isAvailable && !gate.hasOverride ? "opacity-60" : ""}`}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={gate.isAvailable ? "text-green-600" : "text-gray-400"}>
                  {gate.isAvailable ? "✅" : "🔒"}
                </span>
                <span className="font-semibold text-sm">{gate.feature}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${tierColors[gate.minTier] || "bg-gray-100"}`}>
                  {gate.minTier}+
                </span>
                {gate.hasOverride && <span className="text-xs text-purple-600">⚡ override</span>}
                {!gate.enabled && <span className="text-xs text-red-500">disabled</span>}
              </div>
              <div className="flex gap-1">
                {gate.hasOverride ? (
                  <button onClick={() => onClearOverride?.(gate.feature)}
                    className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">Clear</button>
                ) : !gate.isAvailable ? (
                  <button onClick={() => onOverride?.(gate.feature, true)}
                    className="text-xs bg-purple-600 text-white px-2 py-0.5 rounded">Override</button>
                ) : null}
              </div>
            </div>
            {gate.description && <p className="text-xs text-gray-500">{gate.description}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
