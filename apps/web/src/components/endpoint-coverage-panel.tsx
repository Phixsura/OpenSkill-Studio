"use client";

interface MethodCoverage { total: number; covered: number; }
interface EndpointCoveragePanelProps { coveragePct: number; covered: number;
  total: number; uncoveredPaths: string[]; byMethod: Record<string, MethodCoverage>; }

export function EndpointCoveragePanel({ coveragePct, covered, total, uncoveredPaths, byMethod }: EndpointCoveragePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧪 Endpoint Coverage</h3>
        <span className={`text-xs font-bold ${coveragePct >= 80 ? "text-green-600" : "text-yellow-600"}`}>
          {coveragePct}% · {covered}/{total}
        </span>
      </div>
      <div className="p-3">
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full mb-3">
          <div className={`h-full rounded-full ${coveragePct >= 80 ? "bg-green-500" : "bg-yellow-500"}`}
            style={{ width: `${coveragePct}%` }} />
        </div>
        <div className="flex gap-3 text-xs mb-2">
          {Object.entries(byMethod).map(([m, c]) => (
            <span key={m} className="text-gray-400">{m}: {c.covered}/{c.total}</span>
          ))}
        </div>
        {uncoveredPaths.length > 0 && (
          <div className="text-[10px] text-red-500">
            Uncovered: {uncoveredPaths.map(p => <span key={p} className="font-mono mr-1">{p}</span>)}
          </div>
        )}
      </div>
    </div>
  );
}
