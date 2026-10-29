"use client";

interface FindingInfo { finding_id: string; severity: string; category: string; message: string; destination: string; }
interface Props { findings: FindingInfo[]; severityBreakdown: Record<string, number>; criticalCount: number; appName: string; }

const sevColor: Record<string, string> = { critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", medium: "bg-yellow-100 text-yellow-700", low: "bg-blue-100 text-blue-700" };

export default function APIDeveloperAPIApiWebhookSecurityScannerCard({ findings, severityBreakdown, criticalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Security Scanner</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{criticalCount} critical</span>}
      </div>
      <div className="mb-3 flex gap-2">
        {Object.entries(severityBreakdown).map(([sev, count]) => (
          <span key={sev} className={`rounded px-1.5 py-0.5 text-[10px] ${sevColor[sev] ?? ""}`}>{sev}: {count}</span>
        ))}
      </div>
      {findings.length === 0 ? (
        <p className="text-center text-sm text-green-600">✓ No security findings</p>
      ) : (
        <div className="space-y-1.5">
          {findings.map((f) => (
            <div key={f.finding_id} className="text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${sevColor[f.severity] ?? ""}`}>{f.severity}</span>
                <span className="text-gray-700 dark:text-gray-300">{f.message}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
