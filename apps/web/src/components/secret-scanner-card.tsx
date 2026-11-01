"use client";

interface SecretFindingInfo {
  finding_id: string;
  pattern_name: string;
  matched_text: string;
  location: string;
  severity: string;
  resolved: boolean;
}

interface SecretScannerCardProps {
  findings: SecretFindingInfo[];
  appName: string;
}

const severityStyle: Record<string, string> = {
  critical: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  low: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

export default function SecretScannerCard({ findings, appName }: SecretScannerCardProps) {
  const unresolved = findings.filter((f) => !f.resolved).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔍 Secret Scanner
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{findings.length} findings</span>
          {unresolved > 0 && (
            <p className="text-[10px] font-medium text-red-600 dark:text-red-400">
              {unresolved} unresolved
            </p>
          )}
        </div>
      </div>

      {findings.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">
          No secrets detected
        </p>
      ) : (
        <div className="space-y-1.5">
          {findings.map((f) => (
            <div
              key={f.finding_id}
              className={`rounded-lg border px-3 py-2 ${f.resolved ? "border-gray-100 opacity-60 dark:border-gray-800" : "border-gray-200 dark:border-gray-700"}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${severityStyle[f.severity] ?? ""}`}
                  >
                    {f.severity}
                  </span>
                  <span className="text-xs text-gray-700 dark:text-gray-300">{f.pattern_name}</span>
                </div>
                {f.resolved && <span className="text-[10px] text-green-600">✓ resolved</span>}
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                <span className="font-mono">{f.matched_text}</span>
                <span>{f.location}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
