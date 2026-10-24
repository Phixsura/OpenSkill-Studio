"use client";

interface ScopeInfo { scope: string; label: string; category: string; risk: string; }
interface ApiKeyScopeSelectorProps { availableScopes: ScopeInfo[]; selected: Set<string>;
  onToggle: (scope: string) => void; needsApproval: boolean; maxRisk: string; }

const riskDot: Record<string, string> = {
  low: "bg-green-500", medium: "bg-yellow-500", high: "bg-orange-500", critical: "bg-red-500",
};

export function ApiKeyScopeSelector({ availableScopes, selected, onToggle, needsApproval, maxRisk }: ApiKeyScopeSelectorProps) {
  const categories = [...new Set(availableScopes.map(s => s.category))];
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">API Key Scopes</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{selected.size} selected</span>
          {needsApproval && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Needs Approval</span>}
        </div>
      </div>
      {categories.map(cat => (
        <div key={cat}>
          <h3 className="text-xs font-medium uppercase text-gray-400">{cat}</h3>
          <div className="mt-1 space-y-1">
            {availableScopes.filter(s => s.category === cat).map(s => (
              <label key={s.scope} className="flex items-center gap-2 rounded border px-3 py-2 dark:border-gray-700">
                <input type="checkbox" checked={selected.has(s.scope)}
                  onChange={() => onToggle(s.scope)} className="accent-blue-600" />
                <span className={`h-2 w-2 rounded-full ${riskDot[s.risk] ?? ""}`} />
                <span className="flex-1 text-sm">{s.label}</span>
                <code className="text-xs text-gray-400">{s.scope}</code>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
