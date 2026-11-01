"use client";

interface Scope { id: string; description: string; risk: string; granted: boolean; }
interface ScopeSelectorGridProps { categories: Record<string, Scope[]>; granted: number;
  totalScopes: number; hasHighRisk: boolean; onToggle: (id: string) => void; }

const riskDot: Record<string, string> = { low: "bg-green-500", medium: "bg-yellow-500", high: "bg-red-500" };

export function ScopeSelectorGrid({ categories, granted, totalScopes, hasHighRisk, onToggle }: ScopeSelectorGridProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">API Key Scopes</h3>
        <div className="flex items-center gap-2">
          {hasHighRisk && <span className="text-xs text-red-600">⚠ High-risk</span>}
          <span className="text-xs text-gray-400">{granted}/{totalScopes} selected</span>
        </div>
      </div>
      {Object.entries(categories).map(([cat, scopes]) => (
        <div key={cat}>
          <p className="text-xs font-semibold text-gray-400 uppercase mb-1">{cat}</p>
          <div className="space-y-1">
            {scopes.map(s => (
              <label key={s.id} className="flex items-center gap-3 rounded border px-3 py-2 cursor-pointer dark:border-gray-700">
                <input type="checkbox" checked={s.granted} onChange={() => onToggle(s.id)} className="accent-blue-600" />
                <div className="flex-1">
                  <code className="text-xs font-mono">{s.id}</code>
                  <p className="text-xs text-gray-400">{s.description}</p>
                </div>
                <span className={`h-2 w-2 rounded-full ${riskDot[s.risk] ?? ""}`} title={s.risk} />
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
