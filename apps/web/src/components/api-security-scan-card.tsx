"use client";

interface FindingInfo {
  finding_id: string;
  check_name: string;
  severity: string;
  resolved: boolean;
}

interface APISecurityScanCardProps {
  findings: FindingInfo[];
  score: number;
  appName: string;
}

const sevStyle: Record<string, string> = {
  info: "bg-gray-100 text-gray-500 dark:bg-gray-800",
  low: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function APISecurityScanCard({ findings, score, appName }: APISecurityScanCardProps) {
  const unresolved = findings.filter((f) => !f.resolved).length;
  const scoreColor = score >= 90 ? "text-green-600" : score >= 70 ? "text-yellow-600" : "text-red-500";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Security Scan</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${scoreColor}`}>{score}</span>
          {unresolved > 0 && <p className="text-[10px] text-red-500">{unresolved} unresolved</p>}
        </div>
      </div>

      {findings.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">No findings</p>
      ) : (
        <div className="space-y-1">
          {findings.map((f) => (
            <div key={f.finding_id} className={`flex items-center justify-between text-[11px] ${f.resolved ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${sevStyle[f.severity] ?? ""}`}>{f.severity}</span>
                <span className="text-gray-700 dark:text-gray-300">{f.check_name}</span>
              </div>
              {f.resolved && <span className="text-[9px] text-green-600">✓</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
