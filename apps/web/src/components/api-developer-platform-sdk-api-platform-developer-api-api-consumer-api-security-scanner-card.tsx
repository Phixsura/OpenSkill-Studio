"use client";

interface FindingInfo { finding_id: string; category: string; severity: string; title: string; resolved: boolean; }
interface Props { consumerId: string; score: number; findings: FindingInfo[]; criticalCount: number; appName: string; }

const sevColor: Record<string, string> = { critical: "text-red-600 dark:text-red-400", high: "text-orange-600 dark:text-orange-400", medium: "text-yellow-600 dark:text-yellow-400", low: "text-gray-400" };
const scoreColor = (s: number) => s >= 90 ? "text-green-600 dark:text-green-400" : s >= 70 ? "text-yellow-600 dark:text-yellow-400" : "text-red-600 dark:text-red-400";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSecurityScannerCard({ consumerId, score, findings, criticalCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Security Scanner</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-lg font-bold ${scoreColor(score)}`}>{score}</span>
      </div>
      {criticalCount > 0 && <div className="mb-2 rounded bg-red-50 p-1 text-center text-[10px] text-red-700 dark:bg-red-900/20 dark:text-red-400">🚨 {criticalCount} critical findings</div>}
      {findings.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No findings</p>
      ) : (
        <div className="space-y-1">
          {findings.filter(f => !f.resolved).map((f) => (
            <div key={f.finding_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{f.title}</span>
              <span className={sevColor[f.severity] ?? ""}>{f.severity}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
