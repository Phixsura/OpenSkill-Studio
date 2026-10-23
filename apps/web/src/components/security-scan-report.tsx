"use client";

interface ScanResult { title: string; severity: string; passed: boolean; }
interface SecurityScanReportProps { results: ScanResult[]; scoreDisplay: string;
  status: string; criticalFailures: number; }

const SEV_STYLE: Record<string, string> = {
  critical: "text-red-600", high: "text-orange-600", medium: "text-yellow-600",
};

export function SecurityScanReport({ results, scoreDisplay, status, criticalFailures }: SecurityScanReportProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔒 Security Scan</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold">{scoreDisplay}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            status === "passed" ? "bg-green-100 text-green-700" :
            status === "failed" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"
          }`}>{status}</span>
        </div>
      </div>
      {criticalFailures > 0 && (
        <p className="text-xs text-red-500 mb-3">⚠️ {criticalFailures} critical issue(s) must be fixed</p>
      )}
      <div className="space-y-1.5">
        {results.map(r => (
          <div key={r.title} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span>{r.passed ? "✅" : "❌"}</span>
              <span>{r.title}</span>
            </div>
            <span className={`text-xs ${SEV_STYLE[r.severity] || ""}`}>{r.severity}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
