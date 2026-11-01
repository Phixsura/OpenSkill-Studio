"use client";

interface IsolationLevel { id: string; label: string; risk: string; cost_multiplier: number; features: string[]; }
interface TenantIsolationConfigProps { levels: IsolationLevel[]; currentLevel: string;
  onSelect: (level: string) => void; }

const riskColor: Record<string, string> = {
  none: "text-green-600", minimal: "text-blue-600", low: "text-yellow-600",
};

export function TenantIsolationConfig({ levels, currentLevel, onSelect }: TenantIsolationConfigProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Tenant Isolation</h2>
      <div className="grid gap-3 sm:grid-cols-3">
        {levels.map(l => (
          <div key={l.id} className={`rounded-lg border p-4 ${currentLevel === l.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <h3 className="font-semibold">{l.label}</h3>
            <p className={`text-xs ${riskColor[l.risk] ?? ""}`}>Risk: {l.risk}</p>
            <p className="text-sm font-bold">{l.cost_multiplier}×</p>
            <ul className="mt-2 space-y-0.5 text-xs text-gray-400">
              {l.features.map(f => <li key={f}>✓ {f.replace(/_/g, " ")}</li>)}
            </ul>
            <button onClick={() => onSelect(l.id)}
              className={`mt-3 w-full rounded py-1.5 text-sm ${currentLevel === l.id ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
              {currentLevel === l.id ? "Current" : "Select"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
