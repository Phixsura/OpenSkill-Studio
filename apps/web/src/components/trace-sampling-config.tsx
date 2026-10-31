"use client";

interface SamplingRule { name: string; path: string; rate: number; rateDisplay: string; }
interface TraceSamplingConfigProps { defaultRate: number; rules: SamplingRule[];
  onAddRule: (name: string, path: string, rate: number) => void; }

export function TraceSamplingConfig({ defaultRate, rules, onAddRule }: TraceSamplingConfigProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🎯 Trace Sampling</h3>
        <span className="text-xs text-gray-400">Default: {(defaultRate * 100).toFixed(0)}%</span>
      </div>
      <div className="space-y-2 mb-4">
        {rules.map(r => (
          <div key={r.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <div>
              <span className="text-sm font-medium">{r.name}</span>
              <span className="text-xs text-gray-400 ml-2 font-mono">{r.path}</span>
            </div>
            <span className="text-xs font-medium px-2 py-0.5 bg-blue-100 text-blue-700 rounded">{r.rateDisplay}</span>
          </div>
        ))}
        {rules.length === 0 && <p className="text-sm text-gray-400">No custom rules</p>}
      </div>
      <button onClick={() => onAddRule("new_rule", "/api", 0.5)}
        className="w-full py-1.5 border border-dashed border-gray-300 dark:border-gray-600 rounded text-xs text-gray-400 hover:text-gray-600">
        + Add Sampling Rule
      </button>
    </div>
  );
}
