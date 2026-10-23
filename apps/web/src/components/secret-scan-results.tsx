"use client";

interface Finding { type: string; severity: string; line: number; file: string; match_preview: string; }
interface SecretScanResultsProps { findings: Finding[]; filesScanned: number; clean: boolean; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700", medium: "bg-yellow-100 text-yellow-700",
};

export function SecretScanResults({ findings, filesScanned, clean }: SecretScanResultsProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Secret Scanner</h3>
        <span className="text-xs text-gray-400">{filesScanned} files scanned</span>
      </div>
      {clean ? (
        <p className="mt-3 text-sm text-green-600">✅ No secrets detected!</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {findings.map((f, i) => (
            <li key={i} className="rounded border p-2 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{f.type}</span>
                <span className={`rounded px-1.5 py-0.5 text-xs ${SEV_COLORS[f.severity] || ""}`}>{f.severity}</span>
              </div>
              <p className="text-xs text-gray-500">{f.file}:{f.line}</p>
              <code className="text-xs text-red-600">{f.match_preview}</code>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
