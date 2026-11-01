"use client";

interface LinkResult { url: string; valid: boolean; status: string; }
interface LinkCheckerReportProps { results: LinkResult[]; valid: number; broken: number; health: string; }

const healthColors: Record<string, string> = {
  good: "text-green-600", warning: "text-yellow-600", critical: "text-red-600",
};

export function LinkCheckerReport({ results, valid, broken, health }: LinkCheckerReportProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Link Checker</h3>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium ${healthColors[health] ?? ""}`}>{valid}✓ {broken}✗</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-48 overflow-y-auto">
        {results.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2 min-w-0">
              <span className={r.valid ? "text-green-600" : "text-red-600"}>{r.valid ? "✓" : "✗"}</span>
              <span className="text-xs font-mono truncate">{r.url}</span>
            </div>
            <span className="text-xs text-gray-400">{r.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
