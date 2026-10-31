"use client";
interface Pattern { pattern: string; count: number; services: string[]; sample: string; }
interface ErrPatternPanelProps { patterns: Pattern[]; totalErrors: number; }
export function ErrPatternPanel({ patterns, totalErrors }: ErrPatternPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Error Patterns</h3>
        <span className="text-xs text-gray-400">{patterns.length} patterns · {totalErrors} errors</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {patterns.map(p => (
          <div key={p.pattern} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono text-red-500">{p.pattern}</span>
              <span className="text-gray-400">{p.count}x · {p.services.join(", ")}</span>
            </div>
            <div className="text-gray-400 truncate">{p.sample}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
