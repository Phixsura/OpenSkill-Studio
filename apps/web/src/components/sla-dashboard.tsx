"use client";

interface SlaResult { metric: string; target: number; actual: number; met: boolean; margin: number; status: string; }
interface SlaDashboardProps { results: SlaResult[]; compliancePct: number; overall: string; }

export function SlaDashboard({ results, compliancePct, overall }: SlaDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">SLA Compliance</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${overall === "compliant" ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-sm font-medium">{compliancePct}%</span>
        </div>
      </div>
      <div className="space-y-2">
        {results.map(r => (
          <div key={r.metric} className={`flex items-center justify-between rounded-lg border px-4 py-3 ${r.met ? "dark:border-gray-700" : "border-red-300 bg-red-50 dark:bg-red-900/10 dark:border-red-700"}`}>
            <div>
              <p className="text-sm font-medium">{r.metric}</p>
              <p className="text-xs text-gray-400">Target: {r.target} · Actual: {r.actual}</p>
            </div>
            <span className={`text-xs font-medium ${r.met ? "text-green-600" : "text-red-600"}`}>
              {r.met ? "✓ PASS" : "✗ FAIL"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
