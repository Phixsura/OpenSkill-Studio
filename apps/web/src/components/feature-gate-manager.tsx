"use client";

interface Gate { type: string; feature: string; config: Record<string, unknown>; }
interface FeatureGateManagerProps { gates: Gate[]; onAdd: () => void; onRemove: (index: number) => void; }

const gateIcon: Record<string, string> = {
  plan: "💳", role: "👤", org: "🏢", user: "🎯", percentage: "📊",
};

export function FeatureGateManager({ gates, onAdd, onRemove }: FeatureGateManagerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Feature Gates</h2>
        <button onClick={onAdd} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add Gate</button>
      </div>
      {gates.length === 0 ? (
        <p className="text-sm text-gray-400">No gates — feature available to everyone</p>
      ) : (
        <div className="space-y-2">
          {gates.map((g, i) => (
            <div key={i} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <span>{gateIcon[g.type] ?? "🔒"}</span>
                <div>
                  <p className="text-sm font-medium">{g.feature}</p>
                  <p className="text-xs capitalize text-gray-400">{g.type} gate</p>
                </div>
              </div>
              <button onClick={() => onRemove(i)} className="text-xs text-red-500">Remove</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
