"use client";

interface FindingInfo {
  pattern_name: string;
  severity: "critical" | "high" | "medium";
  location: string;
  snippet: string;
}

interface SecretScannerCardProps {
  findings: FindingInfo[];
  scannedFields: number;
  appName: string;
}

const SEV_STYLES: Record<string, { bg: string; text: string }> = {
  critical: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400" },
  high: { bg: "bg-orange-100 dark:bg-orange-900/30", text: "text-orange-700 dark:text-orange-400" },
  medium: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
  },
};

export default function SecretScannerCard({
  findings,
  scannedFields,
  appName,
}: SecretScannerCardProps) {
  const clean = findings.length === 0;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Secret Scanner</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{scannedFields} fields scanned</span>
          {clean ? (
            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
              ✓ Clean
            </span>
          ) : (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {findings.length} secrets found
            </span>
          )}
        </div>
      </div>

      {clean ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">
          No secrets detected
        </p>
      ) : (
        <div className="space-y-1.5">
          {findings.map((f, i) => {
            const sev = SEV_STYLES[f.severity] ?? SEV_STYLES.medium;
            return (
              <div
                key={i}
                className="flex items-start gap-2 rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <span
                  className={`mt-0.5 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${sev.bg} ${sev.text}`}
                >
                  {f.severity}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-800 dark:text-gray-200">
                      {f.pattern_name.replace(/_/g, " ")}
                    </span>
                    <span className="text-[11px] text-gray-400">in {f.location}</span>
                  </div>
                  <span className="font-mono text-[10px] text-gray-400">{f.snippet}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
